"""Check database readiness; optionally run a hosted workflow verification."""
import os


def on_starting(server):
    from app import app
    if app.config.get('DATABASE_URL'):
        with app.test_client() as client:
            if client.get('/health').status_code != 200:
                raise RuntimeError('Hosted database readiness check failed.')
        server.log.info('AdaptTrail persistent database readiness check passed.')
        if os.environ.get('VERIFY_HOSTED') == '1':
            from hosted_verify import verify
            verify()
            server.log.info('AdaptTrail hosted verification passed: accounts, ownership, persistence, editing, deletion, logout, and cleanup.')
