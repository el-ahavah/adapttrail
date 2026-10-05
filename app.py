"""AdaptTrail's first pages. All examples are fictional demonstration data."""
from flask import Flask, abort, render_template, request, redirect, url_for, session, g
from pathlib import Path
import secrets
import os
from storage import connect, IntegrityErrors
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hmac
import re
import json
from documented_projects import DOCUMENTED_PROJECTS
from assessment import FIELDS, VERSION, assess
from weather import search_locations, forecast, planning_notes, WeatherUnavailable
from datetime import date
from decimal import Decimal, InvalidOperation
import click
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
production = os.environ.get('APP_ENV') == 'production'
secret = os.environ.get('SECRET_KEY')
database_url = os.environ.get('DATABASE_URL')
if production and (not secret or len(secret) < 32 or not database_url):
    raise RuntimeError('Production requires SECRET_KEY (32+ characters) and DATABASE_URL.')
if not secret:
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret_path = Path(app.instance_path) / 'session-key'
    if not secret_path.exists():
        secret_path.write_text(secrets.token_hex(32))
        secret_path.chmod(0o600)
    secret = secret_path.read_text()
app.config.update(SECRET_KEY=secret, DATABASE_URL=database_url,
                  DATABASE=str(Path(app.instance_path) / 'drafts.sqlite3'),
                  MAX_CONTENT_LENGTH=64 * 1024,
                  SESSION_COOKIE_SECURE=production,
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')


limiter = Limiter(get_remote_address, app=app, storage_uri='memory://',
                  enabled=production, default_limits=[])


def database():
    return connect(app.config)


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
                           actions=sorted({p['action'] for p in PROJECTS + DOCUMENTED_PROJECTS} | {'Community project'}), community=published_stories(action),
                           documented=[p for p in DOCUMENTED_PROJECTS if not action or p['action'] == action])

@app.get('/projects/<project_id>')
def project_detail(project_id):
    project = next((p for p in PROJECTS + DOCUMENTED_PROJECTS if p['id'] == project_id), None)
    if project is None:
        abort(404)
    return render_template('documented_project.html' if project.get('kind') == 'documented' else 'project.html', project=project)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.get('/drafts')
def drafts():
    connection = database()
    try:
        records = connection.execute("""SELECT d.*,
            (SELECT COUNT(*) FROM assessments a WHERE a.project_id=d.id AND a.user_id=?) AS assessment_count,
            (SELECT COUNT(*) FROM progress_entries p WHERE p.project_id=d.id) AS progress_count
            FROM drafts d WHERE d.user_id=? ORDER BY d.id DESC""", (g.user['id'], g.user['id'])).fetchall()
        recent_assessments = connection.execute("""SELECT a.*, d.title AS project_title
            FROM assessments a LEFT JOIN drafts d ON d.id=a.project_id AND d.user_id=a.user_id
            WHERE a.user_id=? ORDER BY a.id DESC LIMIT 5""", (g.user['id'],)).fetchall()
        assessment_count = connection.execute('SELECT COUNT(*) AS total FROM assessments WHERE user_id=?', (g.user['id'],)).fetchone()['total']
        recent_progress = connection.execute("""SELECT p.*, d.title AS project_title
            FROM progress_entries p JOIN drafts d ON d.id=p.project_id
            WHERE d.user_id=? ORDER BY p.created_at DESC, p.id DESC LIMIT 5""", (g.user['id'],)).fetchall()
    finally:
        connection.close()
    return render_template('drafts.html', drafts=records,
                           recent_assessments=[dict(record) | {'guidance': json.loads(record['result'])['status']} for record in recent_assessments],
                           recent_progress=recent_progress, assessment_count=assessment_count,
                           progress_count=sum(record['progress_count'] for record in records),
                           ongoing_count=sum(record['status'] == 'ongoing' for record in records))


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
                        'INSERT INTO drafts (title,country,problem,approach,conditions,source_id,user_id) VALUES (?,?,?,?,?,?,?) RETURNING id',
                        tuple(values[key] for key in ['title', 'country', 'problem', 'approach', 'conditions', 'source_id']) + (g.user['id'],))
                    draft_id = cursor.fetchone()['id']
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('draft_form.html', values=values, errors=errors, projects=PROJECTS), (400 if errors else 200)


@app.get('/drafts/<int:draft_id>')
def draft_detail(draft_id):
    draft = get_draft(draft_id)
    source = next((p for p in PROJECTS if p['id'] == draft['source_id']), None)
    return render_template('draft_detail.html', draft=draft, source=source, adaptation=get_adaptation(draft_id))


DRAFT_FIELDS = ['title', 'country', 'problem', 'approach', 'conditions', 'source_id']


@app.get('/drafts/<int:draft_id>/history')
def project_history(draft_id):
    draft = get_draft(draft_id)
    connection = database()
    try:
        progress = connection.execute('SELECT * FROM progress_entries WHERE project_id=? ORDER BY entry_date,id', (draft_id,)).fetchall()
        assessments = connection.execute('SELECT * FROM assessments WHERE project_id=? AND user_id=? ORDER BY id', (draft_id,g.user['id'])).fetchall()
        publication = connection.execute('SELECT * FROM publications WHERE project_id=?', (draft_id,)).fetchone()
    finally:
        connection.close()
    events = [dict(date=str(draft['created_at'])[:10], kind='project', record=draft)]
    events += [dict(date=entry['entry_date'], kind='progress', record=entry) for entry in progress]
    events += [dict(date=str(record['created_at'])[:10], kind='assessment', record=record,
                    result=json.loads(record['result'])) for record in assessments]
    events.sort(key=lambda event: event['date'])
    source = next((p for p in PROJECTS if p['id'] == draft['source_id']), None)
    return render_template('project_history.html', draft=draft, events=events,
                           publication=publication, source=source, adaptation=get_adaptation(draft_id))


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
    if values['source_id'] and values['source_id'] not in {p['id'] for p in PROJECTS + DOCUMENTED_PROJECTS}:
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
        values, errors = validate_draft(dict(request.form) | ({'source_id': draft['source_id']} if get_adaptation(draft_id) else {}))
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
    if request.path.startswith(('/drafts', '/assess')) and g.user is None:
        if request.method == 'GET' and safe_return_path(request.path):
            session['return_after_login'] = request.path
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def register():
    error, username = None, ''
    if request.method == 'POST':
        check_csrf()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        if not re.fullmatch(r'[a-z0-9_]{3,30}', username):
            error = 'Use 3–30 letters, numbers, or underscores for your username.'
        elif not 8 <= len(password) <= 128:
            error = 'Use a password between 8 and 128 characters.'
        elif password != request.form.get('confirmation', ''):
            error = 'The passwords do not match.'
        else:
            password_hash = generate_password_hash(password)
            connection = database()
            try:
                with connection:
                    connection.execute('INSERT INTO users (username,password_hash) VALUES (?,?)', (username, password_hash))
            except IntegrityErrors:
                error = 'That username is unavailable.'
            finally:
                connection.close()
            if error is None:
                return redirect(url_for('login'))
    return render_template('auth.html', registering=True, error=error, username=username), (400 if error else 200)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
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
            destination = session.get('return_after_login', '')
            session.clear()
            session['user_id'] = user['id']
            return redirect(destination if safe_return_path(destination) else url_for('drafts'))
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


@app.get('/health')
def health():
    connection = database()
    try:
        connection.execute('SELECT 1 FROM users LIMIT 1').fetchone()
    finally:
        connection.close()
    return {'status': 'ok'}


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if production:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    if request.path.startswith(('/drafts', '/assess')) or request.path in ['/login', '/register']:
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.post('/drafts/<int:draft_id>/status')
def project_status(draft_id):
    get_draft(draft_id)
    check_csrf()
    status = request.form.get('status')
    if status not in {'planned', 'ongoing', 'completed'}:
        abort(400)
    connection = database()
    try:
        with connection:
            connection.execute('UPDATE drafts SET status=? WHERE id=? AND user_id=?', (status, draft_id, g.user['id']))
    finally:
        connection.close()
    return redirect(url_for('draft_detail', draft_id=draft_id))


@app.route('/drafts/<int:draft_id>/progress', methods=['GET', 'POST'])
def project_progress(draft_id):
    draft = get_draft(draft_id)
    values = dict(entry_date=date.today().isoformat(), observation='', measurement='', unit='', metric='', period='', entry_type='observation')
    errors = []
    if request.method == 'POST':
        check_csrf()
        values = {key: request.form.get(key, '').strip() for key in values}
        try:
            recorded = date.fromisoformat(values['entry_date'])
            if recorded > date.today():
                errors.append('Observation date cannot be in the future.')
        except ValueError:
            errors.append('Enter a valid observation date.')
        if not values['observation'] or len(values['observation']) > 3000:
            errors.append('Write an observation of 1–3000 characters.')
        if values['entry_type'] not in {'observation', 'baseline', 'follow-up'}:
            errors.append('Choose a valid entry type.')
        for key in ['unit', 'metric', 'period']:
            if len(values[key]) > 120:
                errors.append(f'{key.capitalize()} must be 120 characters or fewer.')
        if values['measurement']:
            try:
                amount = Decimal(values['measurement'])
                if not amount.is_finite() or amount < 0 or amount > Decimal('1000000000000'):
                    raise InvalidOperation
                values['measurement'] = str(amount)
            except (InvalidOperation, ValueError):
                errors.append('Measurement must be a finite non-negative number up to one trillion.')
            if not all(values[key] for key in ['unit', 'metric', 'period']):
                errors.append('For a measurement, provide its metric, unit, and measurement period.')
        elif any(values[key] for key in ['unit', 'metric', 'period']) or values['entry_type'] != 'observation':
            errors.append('Provide a measurement, or use an observation without measurement fields.')
        if not errors:
            connection = database()
            try:
                with connection:
                    connection.execute('INSERT INTO progress_entries (project_id,entry_date,observation,measurement,unit,metric,period,entry_type) VALUES (?,?,?,?,?,?,?,?)',
                        (draft_id, values['entry_date'], values['observation'], values['measurement'] or None, values['unit'], values['metric'], values['period'], values['entry_type']))
            finally:
                connection.close()
            return redirect(url_for('project_progress', draft_id=draft_id))
    connection = database()
    try:
        entries = connection.execute('SELECT * FROM progress_entries WHERE project_id=? ORDER BY entry_date,id', (draft_id,)).fetchall()
    finally:
        connection.close()
    return render_template('progress.html', draft=draft, values=values, errors=errors, entries=entries), (400 if errors else 200)


@app.route('/assess/<approach>', methods=['GET', 'POST'])
@app.route('/drafts/<int:draft_id>/assess', methods=['GET', 'POST'])
@limiter.limit('10 per minute', methods=['POST'])
def assess_approach(approach=None, draft_id=None):
    draft = get_draft(draft_id) if draft_id is not None else None
    if draft is not None:
        approach = request.form.get('approach', draft['source_id'] if draft['source_id'] in {p['id'] for p in PROJECTS} else '')
    if approach not in {p['id'] for p in PROJECTS} and not (draft is not None and request.method == 'GET' and approach == ''):
        abort(400 if request.method == 'POST' else 404)
    values = {key: 'unknown' for key in FIELDS}
    values.update(country=draft['country'] if draft else '', region='', crop='', resources='', weather_query='', weather_location='')
    errors = []
    if request.method == 'POST':
        check_csrf()
        values = {key: request.form.get(key, '').strip() for key in values}
        for key, (label, choices) in FIELDS.items():
            if values[key] not in choices:
                errors.append(f'Choose a valid value for {label.lower()}.')
        for key in ['country','region','crop','resources']:
            if len(values[key]) > 300:
                errors.append(f'{key.capitalize()} must be 300 characters or fewer.')
        if len(values['weather_query']) > 120:
            errors.append('Town search must be 120 characters or fewer.')
        if request.form.get('intent') == 'search_weather':
            session.pop('weather_locations', None)
            if len(values['weather_query']) < 3:
                errors.append('Enter at least three characters to search for a town.')
            if not errors:
                try:
                    session['weather_locations'] = search_locations(values['weather_query'])
                    if not session['weather_locations']:
                        errors.append('No matching towns. Try a nearby town, or save without weather.')
                except WeatherUnavailable as error:
                    errors.append(str(error))
            return render_template('assess.html', draft=draft, approach=approach, projects=PROJECTS,
                                   fields=FIELDS, values=values, errors=errors,
                                   locations=session.get('weather_locations', [])), (400 if errors else 200)
        location = next((item for item in session.get('weather_locations', [])
                         if item['id'] == values['weather_location']), None)
        if values['weather_location'] and location is None:
            errors.append('Search again and select a matching town, or choose no weather.')
        if not errors:
            result = assess(approach, values)
            if location:
                try:
                    result['weather'] = forecast(location)
                    result['weather_notes'] = planning_notes(approach, values, result['weather'])
                    result['limitation'] = result['limitation'].replace('No weather data was fetched.', 'Optional weather context is included separately below.')
                except WeatherUnavailable as error:
                    result['weather_error'] = str(error)

            connection = database()
            try:
                with connection:
                    cursor = connection.execute('INSERT INTO assessments (user_id,project_id,approach,inputs,result,rule_version) VALUES (?,?,?,?,?,?) RETURNING id',
                        (g.user['id'], draft_id, approach, json.dumps(values), json.dumps(result), VERSION))
                    assessment_id = cursor.fetchone()['id']
            finally:
                connection.close()
            return redirect(url_for('assessment_result', assessment_id=assessment_id))
    return render_template('assess.html', draft=draft, approach=approach, projects=PROJECTS, fields=FIELDS, values=values, errors=errors, locations=session.get('weather_locations', [])), (400 if errors else 200)


@app.get('/assessments')
def assessment_history():
    connection = database()
    try:
        records = connection.execute('SELECT * FROM assessments WHERE user_id=? ORDER BY id DESC', (g.user['id'],)).fetchall()
    finally:
        connection.close()
    return render_template('assessments.html', records=records)


@app.get('/assessments/<int:assessment_id>')
def assessment_result(assessment_id):
    connection = database()
    try:
        record = connection.execute('SELECT * FROM assessments WHERE id=? AND user_id=?', (assessment_id,g.user['id'])).fetchone()
    finally:
        connection.close()
    if record is None:
        abort(404)
    return render_template('assessment_result.html', record=record, result=json.loads(record['result']), inputs=json.loads(record['inputs']), fields=FIELDS)


PUBLIC_FIELDS = ['title','country','problem','action','outcome','lessons']


def published_stories(action):
    if action and action != 'Community project':
        return []
    connection = database()
    try:
        return connection.execute('SELECT * FROM publications WHERE published=1 AND hidden=0 ORDER BY id DESC').fetchall()
    finally:
        connection.close()


@app.route('/drafts/<int:draft_id>/publish', methods=['GET','POST'])
def publish_project(draft_id):
    draft = get_draft(draft_id)
    connection = database()
    try:
        previous = connection.execute('SELECT * FROM publications WHERE project_id=?', (draft_id,)).fetchone()
    finally:
        connection.close()
    if previous and previous['hidden']:
        return render_template('publication_blocked.html'), 403
    values = dict(previous) if previous else dict(title=draft['title'],country=draft['country'],problem=draft['problem'],action=draft['approach'],outcome='',lessons='')
    errors, preview = [], False
    if request.method == 'POST':
        check_csrf()
        values = {key: request.form.get(key,'').strip() for key in PUBLIC_FIELDS}
        for key in PUBLIC_FIELDS:
            maximum = 120 if key in ['title','country'] else 3000
            if len(values[key]) > maximum or (key in ['title','problem','action','lessons'] and not values[key]):
                errors.append(f'Check {key}: required fields must be filled and text must stay within {maximum} characters.')
        intent = request.form.get('intent')
        if intent not in ['preview','publish']:
            errors.append('Choose preview or publish.')
        if intent == 'publish' and request.form.get('consent') != 'yes':
            errors.append('Confirm permission to share this story publicly.')
        if not errors and intent == 'publish':
            connection = database()
            try:
                with connection:
                    cursor = connection.execute("""INSERT INTO publications (project_id,title,country,problem,action,outcome,lessons)
                        VALUES (?,?,?,?,?,?,?) ON CONFLICT(project_id) DO UPDATE SET
                        title=excluded.title,country=excluded.country,problem=excluded.problem,
                        action=excluded.action,outcome=excluded.outcome,lessons=excluded.lessons,
                        published=1,updated_at=CURRENT_TIMESTAMP RETURNING id""",
                        (draft_id,) + tuple(values[key] for key in PUBLIC_FIELDS))
                    publication_id = cursor.fetchone()['id']
            finally:
                connection.close()
            return redirect(url_for('community_story', publication_id=publication_id))
        preview = not errors
    return render_template('publish.html', draft=draft, values=values, errors=errors, preview=preview, fields=PUBLIC_FIELDS), (400 if errors else 200)


@app.post('/drafts/<int:draft_id>/unpublish')
def unpublish_project(draft_id):
    get_draft(draft_id)
    check_csrf()
    connection = database()
    try:
        with connection:
            connection.execute('UPDATE publications SET published=0 WHERE project_id=?', (draft_id,))
    finally:
        connection.close()
    return redirect(url_for('draft_detail', draft_id=draft_id))


@app.route('/community/<int:publication_id>', methods=['GET','POST'])
@limiter.limit('10 per minute', methods=['POST'])
def community_story(publication_id):
    connection = database()
    try:
        story = connection.execute('SELECT * FROM publications WHERE id=? AND published=1 AND hidden=0', (publication_id,)).fetchone()
    finally:
        connection.close()
    if story is None:
        abort(404)
    reported, error = False, None
    if request.method == 'POST':
        check_csrf()
        reason = request.form.get('reason','').strip()
        if not 10 <= len(reason) <= 1000:
            error = 'Explain the issue in 10–1000 characters.'
        else:
            connection = database()
            try:
                with connection:
                    connection.execute('INSERT INTO story_reports (publication_id,reason) VALUES (?,?)', (publication_id,reason))
            finally:
                connection.close()
            reported = True
    return render_template('community_story.html', story=story, reported=reported, error=error, adaptation=get_adaptation(story['project_id'])), (400 if error else 200)


@app.cli.command('moderate-story')
@click.argument('publication_id', type=int)
@click.option('--restore', is_flag=True, help='Restore a previously hidden story after review.')
def moderate_story(publication_id, restore):
    connection = database()
    try:
        with connection:
            cursor = connection.execute('UPDATE publications SET hidden=? WHERE id=?', (0 if restore else 1,publication_id))
            if cursor.rowcount == 0:
                raise click.ClickException('Story not found.')
            connection.execute('UPDATE story_reports SET resolved=1 WHERE publication_id=?', (publication_id,))
    finally:
        connection.close()
    click.echo('Story restored.' if restore else 'Story hidden pending moderation.')


@app.cli.command('review-reports')
def review_reports():
    connection = database()
    try:
        reports = connection.execute('SELECT id,publication_id,reason,created_at FROM story_reports WHERE resolved=0 ORDER BY id').fetchall()
    finally:
        connection.close()
    for report in reports:
        click.echo(f"Report {report['id']} | Story {report['publication_id']} | {report['created_at']} | {report['reason']}")



def get_adaptation(draft_id):
    """Call after ownership check, or for a currently public story's ancestry."""
    connection = database()
    try:
        record = connection.execute("""SELECT a.*,d.source_id AS documented_source_id,p.id AS available_source_id
            FROM adaptations a JOIN drafts d ON d.id=a.project_id LEFT JOIN publications p
            ON p.id=a.publication_id AND p.published=1 AND p.hidden=0
            WHERE a.project_id=?""", (draft_id,)).fetchone()
        if record is None:
            return None
        values = dict(record)
        values['documented_source'] = next((p for p in DOCUMENTED_PROJECTS if p['id'] == record['documented_source_id']), None)
        return values
    finally:
        connection.close()


def adaptation_notes(form):
    values = {key: form.get(key, '').strip() for key in ['changes','reason']}
    errors = []
    for key, value in values.items():
        if not value or len(value) > 3000:
            errors.append(f'{key.capitalize()} must contain 1–3000 characters.')
    return values, errors


@app.route('/drafts/from-community/<int:publication_id>', methods=['GET','POST'])
def adapt_community(publication_id):
    connection = database()
    try:
        story = connection.execute('SELECT * FROM publications WHERE id=? AND published=1 AND hidden=0', (publication_id,)).fetchone()
    finally:
        connection.close()
    if story is None:
        abort(404)
    values = dict(title=('Adaptation: ' + story['title'])[:120], country='',
                  problem=story['problem'], approach=story['action'], conditions='',
                  source_id='', changes='', reason='')
    errors = []
    if request.method == 'POST':
        check_csrf()
        values, errors = validate_draft(request.form)
        notes, note_errors = adaptation_notes(request.form)
        values.update(notes)
        errors += note_errors
        # Community ancestry is set by this route, never by an editable form ID.
        values['source_id'] = ''
        if not errors:
            connection = database()
            try:
                with connection:
                    cursor = connection.execute('INSERT INTO drafts (title,country,problem,approach,conditions,source_id,user_id) VALUES (?,?,?,?,?,?,?) RETURNING id',
                        tuple(values[key] for key in DRAFT_FIELDS) + (g.user['id'],))
                    draft_id = cursor.fetchone()['id']
                    cursor = connection.execute("""INSERT INTO adaptations (project_id,publication_id,source_title,changes,reason)
                        SELECT ?,id,title,?,? FROM publications WHERE id=? AND published=1 AND hidden=0""",
                        (draft_id, values['changes'], values['reason'], publication_id))
                    if cursor.rowcount != 1:
                        abort(404)
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('adapt_community.html', story=story, values=values, errors=errors), (400 if errors else 200)


@app.route('/drafts/<int:draft_id>/adaptation', methods=['GET','POST'])
def edit_adaptation(draft_id):
    draft = get_draft(draft_id)
    adaptation = get_adaptation(draft_id)
    if adaptation is None:
        abort(404)
    values = dict(changes=adaptation['changes'], reason=adaptation['reason'])
    errors = []
    if request.method == 'POST':
        check_csrf()
        values, errors = adaptation_notes(request.form)
        if not errors:
            connection = database()
            try:
                with connection:
                    connection.execute('UPDATE adaptations SET changes=?,reason=? WHERE project_id=?',
                                       (values['changes'],values['reason'],draft_id))
            finally:
                connection.close()
            return redirect(url_for('draft_detail', draft_id=draft_id))
    return render_template('adaptation_notes.html', draft=draft, values=values, errors=errors), (400 if errors else 200)



@app.route('/drafts/from-documented/<project_id>', methods=['GET','POST'])
def adapt_documented(project_id):
    project = next((p for p in DOCUMENTED_PROJECTS if p['id'] == project_id), None)
    if project is None:
        abort(404)
    values = dict(title=('Adaptation: ' + project['title'])[:120],country='',problem=project['problem'],
                  approach=project['approach'],conditions='',source_id=project_id,changes='',reason='')
    errors = []
    if request.method == 'POST':
        check_csrf()
        values, errors = validate_draft(dict(request.form) | {'source_id':project_id})
        notes, note_errors = adaptation_notes(request.form)
        values.update(notes)
        errors += note_errors
        if not errors:
            connection = database()
            try:
                with connection:
                    cursor = connection.execute('INSERT INTO drafts (title,country,problem,approach,conditions,source_id,user_id) VALUES (?,?,?,?,?,?,?) RETURNING id',
                        tuple(values[key] for key in DRAFT_FIELDS) + (g.user['id'],))
                    draft_id = cursor.fetchone()['id']
                    connection.execute('INSERT INTO adaptations (project_id,publication_id,source_title,changes,reason) VALUES (?,NULL,?,?,?)',
                                       (draft_id,project['title'],values['changes'],values['reason']))
            finally:
                connection.close()
            return redirect(url_for('draft_detail',draft_id=draft_id))
    return render_template('adapt_community.html',story=project,source_url=url_for('project_detail',project_id=project_id),
                           documented_source=True,values=values,errors=errors), (400 if errors else 200)



def safe_return_path(path):
    return isinstance(path,str) and re.fullmatch(
        r'/drafts(?:/new|/from-community/[0-9]+|/from-documented/[a-z0-9-]+|/[0-9]+(?:/(?:edit|delete|history|progress|assess|adaptation|publish))?)?|/assess/(?:rainwater|garden-mulch|water-log)', path) is not None


@app.get('/how-to-use')
def how_to_use():
    return render_template('how_to_use.html')
