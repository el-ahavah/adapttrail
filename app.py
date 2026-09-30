"""AdaptTrail's first pages. All examples are fictional demonstration data."""
from flask import Flask, abort, render_template, request

app = Flask(__name__)
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
