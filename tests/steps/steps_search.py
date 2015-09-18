"""
Created on September 18, 2015

@author: oleg-toporkov
"""
from behave import *
from hamcrest import *

use_step_matcher("re")


@then("I see repositories associated with this user")
def see_repositories(context):
    assert_that(len(context.search_page.get_repositories()), is_(greater_than_or_equal_to(1)))


