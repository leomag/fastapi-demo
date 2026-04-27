import pytest


@pytest.fixture
def sample_fixture():
    return "Hello, World!"


class FakeDBSession:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commits += 1


@pytest.fixture
def fake_db():
    return FakeDBSession()


def pytest_addoption(parser):
    parser.addoption("--myoption", action="store", default="default_value", help="My custom option")
