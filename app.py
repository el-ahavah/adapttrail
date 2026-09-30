"""AdaptTrail's first pages. All examples are fictional demonstration data."""
from flask import Flask, abort, render_template, request, redirect, url_for, session, g
from pathlib import Path
import secrets
import sqlite3
import hmac
import re
import click
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
secret_path = Path(app.instance_path) / 'session-key'
if not secret_path.exists():
    secret_path.write_text(secrets.token_hex(32))
    secret_path.chmod(0o600)
app.config.update(SECRET_KEY=secret_path.read_text(),
                  DATABASE=str(Path(app.instance_path) / 'drafts.sqlite3'),
                  MAX_CONTENT_LENGTH=64 * 1024,
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')


def database():
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, country TEXT NOT NULL,
        problem TEXT NOT NULL, approach TEXT NOT NULL, conditions TEXT NOT NULL,
        source_id TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )""")
    if 'user_id' not in {row['name'] for row in connection.execute('PRAGMA table_info(drafts)')}:
        connection.execute('ALTER TABLE drafts ADD COLUMN user_id INTEGER REFERENCES users(id)')
    connection.commit()
    return connection


@app.context_processor
def form_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return dict(csrf_token=session['csrf_token'], current_user=g.user)

PROJECTS = [
    dict(id='garden-mulch', title='Keeping moisture in a school garden', action='Soil cover', setting='School garden', problem='A school wants to reduce frequent watering during dry periods.', approach='Explore covering exposed soil with suitable mulch and observing moisture before watering.', conditions='Plant type, soil drainage, available mulch, and maintenance capacity need assessment.', lessons='Record watering volumes and weather over the same measurement period. No measured results are available.', icon='01'),
    dict(id='rainwater', title='Making better use of seasonal rain', action='Rainwater collection', setting='Community garden', problem='A garden has an unreliable supply of water for plants.', approach='Document an existing roof collection and storage system and explore improvements with local guidance.', conditions='Roof materials, storage, overflow, maintenance, and intended water use matter.', lessons='Track collected water and maintenance. This example is not a construction design or drinking-water recommendation.', icon='02'),
    dict(id='water-log', title='Understanding where garden water goes', action='Water monitoring', setting='Youth group', problem='A group does not know how much water its garden uses.', approach='Keep a dated record of watering volumes, rainfall observations, and plant condition.', conditions='Use a consistent measurement method and record changes in garden size or plants.', lessons='A baseline helps compare later observations. Missing entries must not be counted as zero.', icon='03'),
]

@app.get('/')
def home():
    return render_template('home.html')

@app.get('/discover')
def discover():
    action = request.args.get('action', '')
    projects = [p for p in PROJECTS if not action or p['action'] == action]
    return render_template('discover.html', projects=projects, action=action,
                           actions=sorted({p['action'] for p in PROJECTS}))

@app.get('/projects/<project_id>')
def project_detail(project_id):
    project = next((p for p in PROJECTS if p['id'] == project_id), None)
    if project is None:
        abort(404)
    return render_template('project.html', project=project)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.get('/drafts')
def drafts():
    connection = database()
    try:
        records = connection.execute('SELECT * FROM drafts WHERE user_id = ? ORDER BY id DESC', (g.user['id'],)).fetchall()
    finally:
        connection.close()
    return render_template('drafts.html', drafts=records)


@app.route('/drafts/new', methods=['GET', 'POST'])
def new_draft():
    values = dict.fromkeys(['title', 'country', 'problem', 'approach', 'conditions', 'source_id'], '')
    errors = []
    if request.method == 'POST':
        check_csrf()
        values, errors = validate_draft(request.form)
        if not errors:
            connection = database()
            try:
                with connection:
                    cursor = connection.execute(
                        'INSERT INTO drafts (title,country,problem,approach,conditions,source_id,user_id) VALUES (?,?,?,?,?,?,?)',
                        tuple(values[key] for key in ['title', 'country', 'problem', 'approach', 'conditions', 'source_id']) + (g.user['id'],))
                    draft_id = cursor.lastrowid
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('draft_form.html', values=values, errors=errors, projects=PROJECTS), (400 if errors else 200)


@app.get('/drafts/<int:draft_id>')
def draft_detail(draft_id):
    draft = get_draft(draft_id)
    source = next((p for p in PROJECTS if p['id'] == draft['source_id']), None)
    return render_template('draft_detail.html', draft=draft, source=source)


DRAFT_FIELDS = ['title', 'country', 'problem', 'approach', 'conditions', 'source_id']


def check_csrf():
    token = request.form.get('csrf_token', '')
    if not token or not hmac.compare_digest(token, session.get('csrf_token', '')):
        abort(400)


def validate_draft(form):
    values = {key: form.get(key, '').strip() for key in DRAFT_FIELDS}
    errors = []
    for key in ['title', 'country', 'problem', 'approach']:
        if not values[key]:
            errors.append(f'{key.capitalize()} is required.')
    for key, value in values.items():
        limit = 120 if key in ['title', 'country', 'source_id'] else 3000
        if len(value) > limit:
            errors.append(f'{key.capitalize()} must be {limit} characters or fewer.')
    if values['source_id'] and values['source_id'] not in {p['id'] for p in PROJECTS}:
        errors.append('Choose an available source project.')
    return values, errors


def get_draft(draft_id):
    connection = database()
    try:
        draft = connection.execute('SELECT * FROM drafts WHERE id = ? AND user_id = ?', (draft_id, g.user['id'])).fetchone()
    finally:
        connection.close()
    if draft is None:
        abort(404)
    return draft


@app.route('/drafts/<int:draft_id>/edit', methods=['GET', 'POST'])
def edit_draft(draft_id):
    draft = get_draft(draft_id)
    values, errors = dict(draft), []
    if request.method == 'POST':
        check_csrf()
        values, errors = validate_draft(request.form)
        if not errors:
            connection = database()
            try:
                with connection:
                    connection.execute(
                        'UPDATE drafts SET title=?,country=?,problem=?,approach=?,conditions=?,source_id=? WHERE id=? AND user_id=?',
                        tuple(values[key] for key in DRAFT_FIELDS) + (draft_id, g.user['id']))
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('draft_form.html', values=values, errors=errors,
                           projects=PROJECTS, editing=True, draft_id=draft_id), (400 if errors else 200)


@app.route('/drafts/<int:draft_id>/delete', methods=['GET', 'POST'])
def delete_draft(draft_id):
    draft = get_draft(draft_id)
    if request.method == 'POST':
        check_csrf()
        if request.form.get('confirm') != 'delete':
            abort(400)
        connection = database()
        try:
            with connection:
                connection.execute('DELETE FROM drafts WHERE id = ? AND user_id = ?', (draft_id, g.user['id']))
        finally:
            connection.close()
        return redirect(url_for('drafts'))
    return render_template('draft_delete.html', draft=draft)


@app.before_request
def load_user():
    g.user = None
    if session.get('user_id'):
        connection = database()
        try:
            g.user = connection.execute('SELECT id,username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        finally:
            connection.close()
        if g.user is None:
            session.clear()
    if request.path.startswith('/drafts') and g.user is None:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error, username = None, ''
    if request.method == 'POST':
        check_csrf()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        if not re.fullmatch(r'[a-z0-9_]{3,30}', username):
            error = 'Use 3–30 letters, numbers, or underscores for your username.'
        elif not 12 <= len(password) <= 128:
            error = 'Use a password between 12 and 128 characters.'
        elif password != request.form.get('confirmation', ''):
            error = 'The passwords do not match.'
        else:
            password_hash = generate_password_hash(password)
            connection = database()
            try:
                with connection:
                    connection.execute('INSERT INTO users (username,password_hash) VALUES (?,?)', (username, password_hash))
            except sqlite3.IntegrityError:
                error = 'That username is unavailable.'
            finally:
                connection.close()
            if error is None:
                return redirect(url_for('login'))
    return render_template('auth.html', registering=True, error=error, username=username), (400 if error else 200)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error, username = None, ''
    if request.method == 'POST':
        check_csrf()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        connection = database()
        try:
            user = connection.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        finally:
            connection.close()
        if len(password) > 128 or user is None or not check_password_hash(user['password_hash'], password):
            error = 'Incorrect username or password.'
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('drafts'))
    return render_template('auth.html', registering=False, error=error, username=username), (400 if error else 200)


@app.post('/logout')
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for('home'))


@app.cli.command('assign-legacy-drafts')
@click.argument('username')
def assign_legacy_drafts(username):
    """Local owner operation: explicitly assign all unowned pre-account drafts."""
    connection = database()
    try:
        user = connection.execute('SELECT id FROM users WHERE username = ?', (username.lower(),)).fetchone()
        if user is None:
            raise click.ClickException('Create this account first.')
        with connection:
            count = connection.execute('UPDATE drafts SET user_id = ? WHERE user_id IS NULL', (user['id'],)).rowcount
    finally:
        connection.close()
    click.echo(f'Assigned {count} legacy drafts to {username}.')
