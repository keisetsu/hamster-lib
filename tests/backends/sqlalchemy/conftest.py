# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str

import pytest

from sqlalchemy import orm, create_engine
import datetime
import fauxfactory

from pytest_factoryboy import register

from . import factories, common

from hamsterlib.backends.sqlalchemy import objects
from hamsterlib.backends.sqlalchemy.storage import SQLAlchemyStore

from hamsterlib import Category, Activity, Fact

register(factories.AlchemyCategoryFactory)
register(factories.AlchemyActivityFactory)
register(factories.AlchemyFactFactory)


# SQLAlchemy fixtures
@pytest.fixture
def alchemy_runner(request):
    """
    Provide a dedicated mock-db bound to a session object.

    The session object we refer to here is loaded at global test start as import
    and is also used by our ``AlchemyFactories``.

    After each testrun the ``Session.remove()`` makes sure that each test gets a new
    session and there is only one at a time.

    We do not actually clear any tables (for example with ``self.session.rollback()``
    but simply provide a all new database as part of this fixture. This is surely
    wasteful but does for now.

    Note:
        [Reference](http://factoryboy.readthedocs.org/en/latest/orms.html#sqlalchemy)
    """
    engine = create_engine('sqlite:///:memory:')
    objects.metadata.bind = engine
    objects.metadata.create_all(engine)
    common.Session.configure(bind=engine)

    def fin():
        common.Session.remove()

    request.addfinalizer(fin)


@pytest.fixture
# [TODO] We propably want this to autouse=True
def alchemy_store(request, alchemy_runner):
    """
    Provide a SQLAlchemyStore that uses our test-session.

    Note:
        The engine created as part of the store.__init__() goes simply unused.
    """
    store = SQLAlchemyStore('sqlite:///:memory:', common.Session)
    return store


# We are sometimes tempted not using hamsterlib.objects at all. but as our tests
# expect them as input we need them!

# Instance sets
# Convinience fixtures that provide mulitudes of certain alchemy instances.
@pytest.fixture
def set_of_categories(alchemy_category_factory):
    """Provide a number of perstent facts at once."""
    return [alchemy_category_factory() for i in range(5)]


@pytest.fixture
def set_of_alchemy_facts(start_datetime, alchemy_fact_factory):
    """
    Provide a multitude of generic persistent facts.

    Facts have one day offset from each other and last 20 minutes each.
    """
    start = start_datetime
    result = []
    for i in range(5):
        end = start + datetime.timedelta(minutes=20)
        fact = alchemy_fact_factory(start=start, end=end)
        result.append(fact)
        start = start + datetime.timedelta(days=1)
    return result


# Fallback hamster object and factory fixtures. Unless we know how factories
# interact.
@pytest.fixture
def category_factory(request, name):
    def generate():
        return Category(name, None)
    return generate


@pytest.fixture
def category(request, category_factory):
    return category_factory()


@pytest.fixture
def activity_factory(request, name, category_factory):
    """
    Provide a ``hamsterlib.Activity`` factory.

    Note:
        * The returned activity will have a *new* category associated as well.
        * Values are randomized but *not parametrized*.
    """
    def generate():
        category = category_factory()
        return Activity(name, pk=None, category=category, deleted=False)
    return generate


@pytest.fixture
def activity(request, activity_factory):
    return activity_factory()


@pytest.fixture
def fact_factory(request, activity_factory, start_end_datetimes, description):
    """
    Provide a ``hamsterlib.Fact`` factory.

    Note:
        * The returned fact will have a *new* activity (and by consequence category)
        associated as well.
        * Values are randomized but *not parametrized*.
    """
    def generate():
        activity = activity_factory()
        start, end = start_end_datetimes
        return Fact(activity, start, end, pk=None, description=description)
    return generate


@pytest.fixture
def fact(request, fact_factory):
    return fact_factory()


# Stale fixture
#@pytest.fixture(params=[True, False])
#def existing_category_valid_parametrized(request, category_factory,
#        name_string_valid_parametrized):
#    """
#    Provide a parametrized persisent category fixture.
#
#    This fixuture will represent a wide array of potential name charsets as well
#    as a ``category=None`` version.
#    """
#
#    if request.param:
#        result = category_factory(name=name_string_valid_parametrized)
#    else:
#        result = None
#    return result
#
#
#@pytest.fixture
#def existing_category_valid_without_none_parametrized(request, category_factory,
#        name_string_valid_parametrized):
#    """
#    Provide a parametrized persisent category fixture.
#
#    This fixuture will represent a wide array of potential name charsets as well
#    but not ``category=None``.
#    """
#    return category_factory(name=name_string_valid_parametrized)


#@pytest.fixture
#def existing_activity_valid_parametrized(activity_factory,
#        name_string_valid_parametrized, deleted_valid_parametrized):
#    """
#    Provide a parametrized persistent activity fixture.
#
#    We make heavy usage of parametrized sub fixtures to generate a wide variation of
#    possible persistent activities. Please refer to each used fixtures docstring
#    for details on what is covered.
#    """
#
#    # [TODO]
#    # Parametrize category. In particular cover cases where category=None
#
#    return activity_factory(name=name_string_valid_parametrized,
#        deleted=deleted_valid_parametrized)
#

#@pytest.fixture
#def alchemy_fact_valid_parametrized(alchemy_store, fact_factory,
#        existing_activity_valid_parametrized, description_valid_parametrized,
#        tag_list_valid_parametrized):
#    fact = fact_factory(description=description_valid_parametrized,
#        tags=tag_list_valid_parametrized)
#    return fact
