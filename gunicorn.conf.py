"""Refuse to serve a hosted app whose persistent database is unavailable."""
def on_starting(server):
    from app import app
    if app.config.get('DATABASE_URL'):
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code != 200:
                raise RuntimeError('Hosted database readiness check failed.')
        server.log.info('AdaptTrail persistent database readiness check passed.')
