# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import random

from juomabot import util
import six

from juomabot.cheers import cheers
from juomabot.excs import Problem

DRINK_EMOJIS = [
    ':tropical_drink:',
    ':beer:',
    ':beers:',
    ':cocktail:',
    ':wine_glass:',
]


def add_product(name, price):
    try:
        price = float(price)
    except:
        raise Problem('The price %s is invalid' % price, code='invalid_price')

    name = six.text_type(name).strip()
    if not name:  # pragma: no cover
        raise Problem('Need a name.', code='no_name')
    with util.get_db() as db:
        if list(db['product'].find(name=name)):
            raise Problem('%s: Already exists' % name, code='exists')
        product = dict(name=name.strip(), price=price, visible=True)
        id = db['product'].insert(product, ['id'])
        product = db['product'].find_one(id=id)
        return 'Added: %r' % dict(product)


def edit_product(name, price):
    try:
        price = float(price)
    except:
        raise Problem('The price %s is invalid' % price, code='invalid_price')
    with util.get_db() as db:
        product = util.find_product(name)
        product['price'] = price
        db['product'].update(product, ['id'])
        return 'Updated: %r' % dict(product)


def toggle_product_visible(name):
    with util.get_db() as db:
        product = util.find_product(name)
        product['visible'] = not product.get('visible')
        db['product'].update(product, ['id'])
        return 'Visibility set: %r' % dict(product)


def add_purchase(sender, name):
    sender = util.normalize_name(sender)
    if not name:
        raise Problem(
            '*Please give me the name of a product.*\nI know about:\n%s' % (
                '\n'.join(['* %s' % p for p in util.get_product_names(with_prices=True)])
            ),
            code='no_name',
            icon=':question:',
        )
    with util.get_db() as db:
        product = util.find_product(name)
        db['purchase'].insert(dict(
            sender=sender,
            created_on=str(datetime.datetime.now()),
            billed=False,
            billed_on='',
            billed_by='',
            price=product['price'],
            name=product['name'],
        ))
        return (
            '%s OK! Added purchase of *%s* (price: %s). %s' % (
                random.choice(DRINK_EMOJIS),
                product['name'],
                product['price'],
                cheers(),
            )
        )


def get_own_stats(sender):
    result = util.get_per_user_stats(sender)
    total = 0
    rows = []
    for row in result:
        rows.append('* %d × %s = %s e' % (row['count'], row['name'].title(), row['total']))
        total += row['total']
    if rows:
        rows.insert(0, ':point_right: *Your unbilled drinks as of %s:*' % datetime.datetime.now())
        rows.append(':moneybag: *GRAND TOTAL:* %s e' % total)
    else:
        rows = ['Found no unbilled purchases for %s. The coast is clear!' % sender]
    return '\n'.join(rows)


def get_price_list():
    return 'The drinkbot knows about:\n%s' % '\n'.join(
        ':cocktail: %s' % p for p in util.get_product_names(with_prices=True)
    )


def billing_stats():
    stats = util.get_billing_stats()
    sig = stats['sig']
    if not stats['rows']:
        raise Problem(
            ':astonished: Nothing to bill since the last billing run.',
            code='nobill',
        )
    return (
        stats['report'] +
        '\n:point_right: The report signature is `%s`. *Invoke the command with `--bill %s` to bill these.*' % (
        sig, sig)
    )


def bill(bill_sig, biller):
    stats = util.get_billing_stats()
    sig = stats['sig']
    if sig != bill_sig:
        raise Problem(
            'The report signature didn\'t match. This means someone has bought something in the meantime. Please run billing stats again...',
            code='sigmatch'
        )
    billing_date = datetime.datetime.now().isoformat()
    util.bill_current(billing_date, biller)
    return ':ok_hand: Okie-doke! Unbilled things are now marked billed with billing date <%s>.' % billing_date
