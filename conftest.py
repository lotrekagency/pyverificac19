from verificac19 import service


def pytest_sessionstart(session):
    print("Updating cache... Please wait..")
    service.update_all()
