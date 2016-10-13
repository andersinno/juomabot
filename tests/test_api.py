import pytest
from pytest import approx

from juomabot import api
from juomabot.excs import Problem
from tests.utils import get_by_product_stats


def test_duplicate_product():
    api.add_product('Battery Lime No Calories', 2.50)
    with pytest.raises(Problem):  # duplicate product
        api.add_product('Battery Lime No Calories', 2.50)


def test_invalid_price():
    api.add_product('Coca-Cola Light', 1.45)

    with pytest.raises(Problem):  # invalid price
        api.edit_product('Coca-Cola Light', "nnep")

    with pytest.raises(Problem):  # invalid price
        api.add_product('Coca-Cola Dark', 'wew lad')


def test_api():
    api.add_product('Battery Lime No Calories', 2.50)
    api.add_product('Battery', 2.50)
    api.add_product('Coca-Cola', 1.25)
    api.add_product('Coca-Cola Light', 1.45)

    api.add_purchase('pikkupomo', 'Coca-Cola')

    for x in range(10):
        api.add_purchase('akx', 'Coca-Cola')
        api.add_purchase('akx', 'Coca-Cola Light')
        api.add_purchase('akx', 'Battery')
        api.add_purchase('akx', 'Lime')
        if x == 4:
            api.edit_product('Coca-Cola Light', 1.80)

    by_product = get_by_product_stats('akx')
    assert all(r['count'] == 10 for r in by_product.values())
    assert by_product['Battery']['total'] == 2.5 * 10
    assert by_product['Battery Lime No Calories']['total'] == 2.5 * 10  # test fuzzy matching
    assert by_product['Coca-Cola Light']['total'] == approx(1.45 * 5 + 1.8 * 5)  # test price changes

    assert get_by_product_stats('pikkupomo')['Coca-Cola']['count'] == 1  # test other users also work


def test_invisible_product_is_not_purchaseable():
    api.add_product('Butter', 2.50)
    api.add_purchase('akx', 'butter')

    with pytest.raises(Problem):
        api.toggle_product_visible('Butter')
        api.add_purchase('akx', 'butter')


def test_fuzzy():
    api.add_product('coca-cola', 2)
    api.add_purchase('akx', 'cocacola')  # close enough
    api.add_purchase('akx', 'coca-cela')  # close enough
    api.add_product('coca-cola LIGHT', 2)
    api.add_purchase('akx', 'cocacola')  # close enough
    api.add_purchase('akx', 'coca-cela')  # close enough
    api.add_purchase('akx', 'coca-cola')  # exact match
    api.add_purchase('akx', 'coca-cola light')  # exact match
    stats = get_by_product_stats('akx')
    assert stats['coca-cola']['count'] == 5
    assert stats['coca-cola LIGHT']['count'] == 1
