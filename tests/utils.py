from contextlib import contextmanager

import pytest

from juomabot import util
from juomabot.excs import Problem


def get_by_product_stats(user):
    return {r['name']: r for r in util.get_per_user_stats(user)}


@contextmanager
def raises_problem(code):
    with pytest.raises(Problem) as ei:
        yield ei
    assert ei.value.code == code, 'problem code was %s, not expected %s' % (ei.value.code, code)


