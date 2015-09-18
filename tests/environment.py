"""
Behave search automatically for module named environment.py to load hooks.
Here we use hooks from base_test (or similar test module) and perform init of all pages for current application.

Created on September 18, 2015

@author: oleg-toporkov
"""
from core import base_test
from pages import main_page, search_page


def before_all(context):
    base_test.before_all(context)


def before_feature(context, feature):
    base_test.before_feature(context, feature)


def before_scenario(context, scenario):
    base_test.before_scenario(context, scenario)

    # place here pages init
    context.main_page = main_page.MainPage(
        'tests/resources/definitions/MainPage.def.csv',
        context.browser)

    context.search_page = search_page.SearchPage(
        'tests/resources/definitions/SearchPage.def.csv',
        context.browser)


def before_step(context, step):
    base_test.before_step(context, step)


def after_all(context):
    base_test.after_all(context)


def after_feature(context, feature):
    base_test.after_feature(context, feature)


def after_scenario(context, scenario):
    base_test.after_scenario(context, scenario)


def after_step(context, step):
    base_test.after_step(context, step)
