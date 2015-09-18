"""
This module contains all hooks + some calls for allure reports
Order of execution in Behave see below.

before_all
for feature in all_features:
    before_feature
    for outline in feature.scenarios:
        for scenario in outline.scenarios:
            before_scenario
            for step in scenario.steps:
                before_step
                    step.run()
                after_step
            after_scenario
    after_feature
after_all

Allure basic call order:
    allure = AllureImpl('./reports')  # this clears ./reports
    allure.star_suite('demo')
    allure.start_case('test_one')
    allure.stop_case(Status.PASSED)
    allure.start_case('test_two')
    allure.start_step('a demo step')
    allure.attach('some file', 'a quick brown fox..', AttachmentType.TEXT)
    allure.stop_step()
    allure.stop_case(Status.FAILED, 'failed for demo', 'stack trace goes here')
    allure.stop_suite()  # this writes XML into ./reports


Created on September 18, 2015

@author: oleg-toporkov
"""
from allure.common import AllureImpl
from allure.constants import AttachmentType, Label
from allure.structure import TestLabel
from allure.utils import LabelsList

import logging
import re
import sys

from utilities.config import Config
from utilities.log import Logger


def before_all(context):
    """
    Before all hook.
    Set config variables for whole run, setup logging, init allure.
    context.config.userdata is a dict with values from behave commandline.
    Example: -D foo=bar will store value in config.userdata['foo'].
    Will be executed once at the beginning of the test run.
    Context injected automatically by Behave.
    :type context: behave.runner.Context
    """
    if context.config.userdata:
        Config.BROWSER = context.config.userdata.get('browser', Config.BROWSER).lower()
        Config.APP_URL = context.config.userdata.get('url', Config.APP_URL).lower()
        Config.REUSE = context.config.userdata.get('reuse', Config.REUSE).lower()
        Config.HIGHLIGHT = context.config.userdata.get('highlight', Config.HIGHLIGHT).lower()

    Logger.configure_logging()
    logger = logging.getLogger(__name__)

    allure_report_path = '{}/allure_report'.format(Config.LOG_DIR)

    try:
        context.allure = AllureImpl(allure_report_path)
    except Exception:
        logger.error('Failed to init allure at: {}'.format(allure_report_path))
        raise


def after_all(context):
    """
    After all hook.
    Empty for now.
    Will be executed once at the beginning of the test run.
    Context injected automatically by Behave.
    :type context: behave.runner.Context
    """
    pass


def before_feature(context, feature):
    """
    Before feature hook.
    Init variables and allure suite.
    Will be executed for every .feature file.
    Context and feature injected automatically by Behave
    :type context: behave.runner.Context
    :type feature: behave.model.Feature
    """
    logger = logging.getLogger(__name__)

    context.browser = None
    context.picture_num = 0

    try:
        context.allure.start_suite(feature.name, feature.description,
                                   labels=LabelsList([TestLabel(name=Label.FEATURE, value=feature.name)]))
    except Exception:
        logger.error('Failed to init allure suite with name: {}'.format(feature.name))
        raise


def after_feature(context, feature):
    """
    After feature hook.
    Shut down allure test suite.
    Will be executed after every .feature file.
    Context and feature injected automatically by Behave
    :type context: behave.runner.Context
    :type feature: behave.model.Feature
    """
    logger = logging.getLogger(__name__)

    try:
        context.allure.stop_suite()
    except Exception:
        logger.error('Failed to stop allure suite with name: {}'.format(feature.name))
        raise


def before_scenario(context, scenario):
    """
    Before scenario hook.
    Create folder for screenshot, open browser, set Full HD resolution and place browser in test context.
    Also start allure test case.
    Will be executed in the beginning of every scenario in .feature file.
    Context and scenario injected automatically by Behave
    :type context: behave.runner.Context
    :type scenario: behave.model.Scenario
    """
    Logger.create_test_folder(scenario.name)
    logger = logging.getLogger(__name__)

    try:
        context.allure.start_case(scenario.name,
                                  labels=LabelsList([TestLabel(name=Label.FEATURE, value=scenario.feature.name)]))
    except Exception:
        logger.error('Failed to init allure test with name: {}'.format(scenario.name))
        raise

    context.test_name = scenario.name

    if context.browser is None:
        try:
            # use in constructor service_args=['--webdriver-logfile=path_to_log'] to debug deeper...
            context.browser = Config.browser_types[Config.BROWSER]()
            context.browser.set_window_size(1920, 1080)
        except Exception:
            logger.error('Failed to start browser: {}'.format(Config.BROWSER))
            raise
    logger.info('Start of test: {}'.format(scenario.name))


def after_scenario(context, scenario):
    """
    After scenario hook.
    Close browser in case it don't needed anymore.
    Make screenshot when test result = failed.
    And stop allure test case.
    Will be executed after every scenario in .feature file.
    Context and scenario injected automatically by Behave
    :type context: behave.runner.Context
    :type scenario: behave.model.Scenario
    """
    logger = logging.getLogger(__name__)

    if scenario.status.lower() == 'failed':
        _screenshot = '{}/{}/__Fail.png'.format(Config.LOG_DIR, scenario.name.replace(' ', '_'))

        try:
            context.browser.save_screenshot(_screenshot)
        except Exception:
            logger.error('Failed to take screenshot to: {}'.format(Config.LOG_DIR))
            raise
        try:
            with open(_screenshot, 'rb') as _file:
                context.allure.attach('{} fail'.format(scenario.name), _file.read(), AttachmentType.PNG)
        except Exception:
            logger.error('Failed to attach to report screenshot: {}'.format(_screenshot))
            raise

    if not Config.REUSE:
        try:
            context.browser.quit()
        except Exception:
            logger.error('Failed to close browser: {}'.format(Config.BROWSER))
            raise
        context.browser = None

    try:
        _status = scenario.status
        if _status == 'skipped':
            _status = 'canceled'  # according to allure statuses
        context.allure.stop_case(_status,
                                 getattr(context, 'last_error_message', None),
                                 getattr(context, 'last_traceback', None))
    except Exception:
        logger.error('Failed to stop allure test with name: {}'.format(scenario.name))
        raise

    logger.info('End of test: {}. Status: {} !!!\n\n\n'.format(scenario.name, scenario.status.upper()))


def before_step(context, step):
    """
    Before step hook.
    Call allure reporting for current step.
    Will be executed before every test step.
    Context and step injected automatically by Behave
    :type context: behave.runner.Context
    :type step: behave.model.Step
    """
    logger = logging.getLogger(__name__)

    try:
        context.allure.start_step(step.name)
    except Exception:
        logger.error('Failed to init allure step with name: {}'.format(step.name))
        raise


def after_step(context, step):
    """
    After step hook.
    Perform screenshot with step name and order num.
    Stop allure step.
    Context and step injected automatically by Behave
    :type context: behave.runner.Context
    :type step: behave.model.Step
    """
    logger = logging.getLogger(__name__)
    step_name = re.sub('[^A-Za-z0-9]+', '_', step.name)
    _screenshot = '{}/{}/{}__{}__.png'.format(Config.LOG_DIR,
                                              context.test_name.replace(' ', '_'),
                                              context.picture_num, step_name)
    try:
        if context.browser is not None:
            context.browser.save_screenshot(_screenshot)
            context.picture_num += 1
    except Exception:
        logger.error('Failed to take screenshot to: {}'.format(Config.LOG_DIR))
        logger.error('Screenshot name: {}'.format(step_name))
        raise

    try:
        with open(_screenshot, 'rb') as _file:
            context.allure.attach('{}_{}'.format(context.test_name, step.name), _file.read(), AttachmentType.PNG)
    except Exception:
        logger.error('Failed to attach to report screenshot: {}'.format(_screenshot))
        raise

    try:
        context.allure.stop_step()
    except Exception:
        logger.error('Failed to stop allure step with name: {}'.format(step.name))
        raise

    if step.status == 'failed':  # get last traceback and error message
        context.last_traceback = step.error_message
        try:
            context.last_error_message = step.error_message.split('ERROR:')[1]
        except IndexError:
            context.last_error_message = step.error_message
