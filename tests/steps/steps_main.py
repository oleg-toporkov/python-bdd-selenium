"""
Created on September 18, 2015

@author: oleg-toporkov
"""
from behave import *
from hamcrest import *

from utilities.config import Config

use_step_matcher('re')


@then("I see '(.*)' in title")
def see_title(context, title):
    assert_that(context.browser.title, contains_string(title))


@given("I open Github URL in browser")
def open_github(context):
    context.main_page.open(Config.APP_URL)


@when("I search '(.*)' text")
def search_text(context, text):
    context.main_page.submit_search(text)
