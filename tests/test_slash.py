import re

import pytest

from juomabot.command import run_command, ADMIN_PASSWORD
from tests.utils import raises_problem


def test_slash_add_and_stats(regular_products):
    resp = run_command('akx', 'lime')  # single substring
    assert all(bit in resp for bit in ('Added', 'Battery Lime'))
    resp = run_command('akx', 'battery')  # exact match
    assert all(bit in resp for bit in ('Added', 'Battery'))

    run_command('akx', 'light')  # substring again

    with raises_problem('no_name'):
        run_command('akx', '')

    with raises_problem('multiple'):
        run_command('akx', 'batt')

    stats_resp = run_command('akx', '--stats')
    assert stats_resp.count('Battery') == 2
    assert stats_resp.count('Battery Lime') == 1
    assert stats_resp.count('Coca-Cola') == 1


@pytest.mark.parametrize('method', ('no_name', 'explicit'))
def test_product_lists(regular_products, method):
    message = None
    if method == 'no_name':
        with raises_problem('no_name') as ei:
            run_command('akx', '')
        message = ei.value.as_slack()
    elif method == 'explicit':
        message = run_command('akx', '-l')
    assert 'Battery' in message
    assert 'Coca-Cola' in message
    assert 'Pepper' in message


def test_admin_product_mgmt(regular_products):
    # Try to add a product without the password:
    with raises_problem('not-an-admin'):
        run_command('ubermaster', '-a --price 10 Moët & Chandon')
    # Add it with the password:
    run_command('ubermaster', '-a -p %s --price 10 Moët & Chandon' % ADMIN_PASSWORD)
    # Test that it's drinkable :champagne:
    run_command('akx', 'Chandon')
    # Oops, adjust the price:
    run_command('ubermaster', '-e -p %s --price 100 Chandon' % ADMIN_PASSWORD)
    # Buy some more:
    run_command('akx', 'Chandon')
    # Look at the budget to ensure the price change took...
    assert '110' in run_command('akx', '--stats')

    # Run out of stock:
    run_command('ubermaster', '-t -p %s Chandon' % ADMIN_PASSWORD)

    with raises_problem('404'):
        # Can't buy it anymore :(
        run_command('akx', 'Chandon')


def test_help(regular_products):
    resp = run_command('foo', '-h')
    # it should list all of our commands...
    assert '--add' in resp
    assert '--password' in resp
    assert '--price' in resp


def test_billing(regular_products):
    products = ('Battery', 'Coca-Cola')
    users = ('akx', 'pikkupomo')
    for product in products:
        for user in users:
            for n in range(5):
                run_command(user, product)

    resp = run_command('master', '-p %s --billing-stats' % ADMIN_PASSWORD)
    # Check that things appear in the report
    assert all(resp.count(user) == 2 for user in users)
    assert all(resp.count(product) == 2 for product in products)

    with raises_problem('sigmatch'):  # Wrong signature...
        run_command('master', '-p %s --bill foofoo' % ADMIN_PASSWORD)

    bill_command = re.search('--bill [a-f0-9]+', resp).group(0)
    resp = run_command('master', '-p %s %s' % (ADMIN_PASSWORD, bill_command))
    assert 'marked billed' in resp

    # Then verify that everything has actually been billed

    with raises_problem('nobill'):
        resp = run_command('master', '-p %s --billing-stats' % ADMIN_PASSWORD)

    for user in users:
        assert 'no unbilled' in run_command(user, '--stats')
