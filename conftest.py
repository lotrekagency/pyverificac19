from tests.setup import run_all

def pytest_sessionstart(session):
    run_all()
