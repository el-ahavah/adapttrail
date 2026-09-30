"""AdaptTrail's first pages. All examples are fictional demonstration data."""
from flask import Flask, abort, render_template, request, redirect, url_for, session
from pathlib import Path
import secrets
import sqlite3
import hmac

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
    return connection


@app.context_processor
def form_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return dict(csrf_token=session['csrf_token'])

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
        records = connection.execute('SELECT * FROM drafts ORDER BY id DESC').fetchall()
    finally:
        connection.close()
    return render_template('drafts.html', drafts=records)


@app.route('/drafts/new', methods=['GET', 'POST'])
def new_draft():
    values = dict.fromkeys(['title', 'country', 'problem', 'approach', 'conditions', 'source_id'], '')
    errors = []
    if request.method == 'POST':
        token = request.form.get('csrf_token', '')
        if not token or not hmac.compare_digest(token, session.get('csrf_token', '')):
            abort(400)
        values = {key: request.form.get(key, '').strip() for key in values}
        for key in ['title', 'country', 'problem', 'approach']:
            if not values[key]:
                errors.append(f'{key.capitalize()} is required.')
        for key, value in values.items():
            limit = 120 if key in ['title', 'country', 'source_id'] else 3000
            if len(value) > limit:
                errors.append(f'{key.capitalize()} must be {limit} characters or fewer.')
        if values['source_id'] and values['source_id'] not in {p['id'] for p in PROJECTS}:
            errors.append('Choose an available source project.')
        if not errors:
            connection = database()
            try:
                with connection:
                    cursor = connection.execute(
                        'INSERT INTO drafts (title,country,problem,approach,conditions,source_id) VALUES (?,?,?,?,?,?)',
                        tuple(values[key] for key in ['title', 'country', 'problem', 'approach', 'conditions', 'source_id']))
                    draft_id = cursor.lastrowid
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('draft_form.html', values=values, errors=errors, projects=PROJECTS), (400 if errors else 200)


@app.get('/drafts/<int:draft_id>')
def draft_detail(draft_id):
    connection = database()
    try:
        draft = connection.execute('SELECT * FROM drafts WHERE id = ?', (draft_id,)).fetchone()
    finally:
        connection.close()
    if draft is None:
        abort(404)
    source = next((p for p in PROJECTS if p['id'] == draft['source_id']), None)
    return render_template('draft_detail.html', draft=draft, source=source)
