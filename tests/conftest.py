import pytest

from juomabot import api


@pytest.fixture
def regular_products():
    api.add_product('Battery Lime No Calories', 2.50)
    api.add_product('Battery', 2.50)
    api.add_product('Coca-Cola', 1.25)
    api.add_product('Coca-Cola Light', 1.45)
    api.add_product('Dr. Pepper', 1.55)


@pytest.fixture
def client():
    from juomabot.wsgi import application
    return application.test_client()
