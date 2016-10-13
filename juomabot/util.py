# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import re

import dataset
from six import text_type
from sqlalchemy import select, func, update

from juomabot.excs import Problem


def levenshtein(a, b):
    'Calculates the Levenshtein distance between a and b.'
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def get_db():
    return dataset.connect()  # pragma: no cover


def normalize_name(name):
    name = text_type(name).lower().replace('.', ' ')
    return re.sub(r'\s+', ' ', name).strip()


def format_product_list(products, with_prices=False):
    if with_prices:
        formatted = [u'%s (%.2f€)' % (p['name'], p['price']) for p in products]
    else:  # pragma: no cover
        formatted = [p['name'] for p in products]
    return sorted(formatted)


def find_products(name):
    """
    Find visible products matching the name.

    :param name: The name to search by
    :type name: str
    :return: List of product data dictionaries (id, name, price)
    :rtype: list[dict[str, object]]
    """
    name = normalize_name(name)
    if not name:  # pragma: no cover
        return []
    with get_db() as db:
        products = db['product'].find(visible=True)
        matches = {}
        for p in products:
            norm_p_name = normalize_name(p['name'])
            if norm_p_name == name:  # Look for exact match
                return [p]
            if name in norm_p_name:
                matches[p['id']] = p
            if levenshtein(name, norm_p_name) < 5:
                matches[p['id']] = p

        return sorted(matches.values(), key=lambda p: p['name'])


def find_product(name):
    """
    Find a single visible product matching the name, or throw a descriptive error if that's not possible.

    :param name: The name to search by.
    :type name: str
    :return: A product dict
    :rtype: dict[str, object]
    """
    products = find_products(name)
    if not products:
        raise Problem(
            'Error: Can\'t find product <%s>.' % name,
            code='404',
            icon=':question:',
        )
    if len(products) > 1:
        raise Problem(
            'Error: More than one product matches %s: [%s]' % (name, ', '.join(p['name'] for p in products)),
            code='multiple',
            icon=':question:',
        )
    return products[0]


def get_product_names(with_prices=False):
    with get_db() as db:
        return format_product_list(
            db['product'].find(visible=True),
            with_prices=with_prices
        )


def get_billing_stats():
    with get_db() as db:
        table = db['purchase'].table
        total_col = func.sum(table.c.price)
        count_col = func.count(table.c.id)
        statement = (
            select([
                table.c.sender,
                table.c.name,
                total_col.label('total'),
                count_col.label('count'),
            ])
                .where((table.c.billed == False))
                .group_by(table.c.sender, table.c.name)
                .order_by(table.c.sender, table.c.name)
        )
        result = db.query(statement)
        report_rows = ['%(sender)s;%(name)s;%(total)s;%(count)s' % row for row in result]

    report = '\n'.join(
        ['```', 'sender;name;total;count'] + report_rows + ['```']
    )
    sig = hashlib.md5(report.encode('UTF-8')).hexdigest()
    return {
        'report': report,
        'rows': report_rows,
        'sig': sig,
    }


def bill_current(billing_date, biller="anonymous"):
    with get_db() as db:
        table = db['purchase'].table
        statement = update(table).where(table.c.billed == False).values(
            billed=True,
            billed_on=billing_date,
            billed_by=biller,
        )
        db.query(statement)


def get_per_user_stats(sender):
    sender = normalize_name(sender)
    with get_db() as db:
        table = db['purchase'].table
        total_col = func.sum(table.c.price)
        count_col = func.count(table.c.id)
        statement = select([
            table.c.name,
            total_col.label('total'),
            count_col.label('count'),
        ]).where((table.c.sender == sender) & (table.c.billed == False)).group_by(table.c.name).order_by(-total_col)
        result = db.query(statement)
        return list(dict(r) for r in result)
