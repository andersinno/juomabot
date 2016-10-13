import dataset
import pytest

from juomabot import util


@pytest.fixture(autouse=True)
def instrument_db(request, monkeypatch):
    """
    Instrument the database to create a new SQLite database per test.
    """
    database = dataset.connect('sqlite:///:memory:')
    monkeypatch.setattr(util, 'get_db', lambda: database)
