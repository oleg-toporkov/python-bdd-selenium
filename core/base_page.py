"""
Created on September 18, 2015

@author: oleg-toporkov
"""
import logging
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from decorators import log_exception
from utilities.config import Config


class BasePage(object):
    """
    Base page representation.
    Contains all actions related to UI interaction.
    All pages may be inherited from this class.
    """
    def __init__(self, browser):
        """
        :type browser: selenium.webdriver.*
        """
        self.browser = browser
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = 15

    @log_exception('Failed to get web element with xpath: {}')
    def _get_element(self, element, expected_condition=expected_conditions.presence_of_element_located, wait=None):
        """
        Function for getting WebElement from given xpath.
        Also performs highlight of that element if Config.HIGHLIGHT is True.
        :type element: str - web element xpath or can be selenium.webdriver.remote.webelement.WebElement
        :type expected_condition: selenium.webdriver.support.expected_conditions.*
        :param wait: int - element wait time, if None takes self.timeout
        :return: element: selenium.webdriver.remote.webelement.WebElement
        """
        if wait is None:
            wait = self.timeout

        if isinstance(element, str):
            self.logger.debug('Waiting {} seconds for web element with condition: {}'
                              .format(wait, expected_condition.__name__))

            wd_wait = WebDriverWait(self.browser, wait)
            element = wd_wait.until(expected_condition((By.XPATH, element)))

        if element:
            self.logger.debug('Got web element!')

            if Config.HIGHLIGHT:
                self._highlight(element)

        return element

    def _highlight(self, element):
        """
        Highlight given web element with red border using JS execution.
        WARNING: Contains time.sleep in 1 sec between scrolling to element and highlighting
        :type element: selenium.webdriver.remote.webelement.WebElement
        """
        self.execute_script(element, 'scrollIntoView(true);')
        sleep(1)
        self.execute_script(element, 'setAttribute("style", "color: red; border: 5px solid red;");')
        sleep(1)
        self.execute_script(element, 'setAttribute("style", "");')

    @log_exception('Failed to get web elements with xpath: {}')
    def get_elements(self, xpath):
        """
        Get multiple elements by xpath.
        :param xpath: str - web element xpath
        :return: tuple of selenium.webdriver.remote.webelement.WebElement
        """
        self.logger.debug('Getting web elements with xpath: {}'.format(xpath))
        self._get_element(xpath)
        elements = self.browser.find_elements_by_xpath(xpath)
        self.logger.debug('Got web elements with xpath: {}'.format(xpath))
        return elements

    @log_exception('Failed presence check of web element with xpath: {}')
    def is_present(self, xpath, wait=None, expected=True):
        """
        Presence check of web element on the UI.
        :param xpath: str - web element xpath
        :param wait: int - wait time
        :param expected: boolean - expected to find it
        :return: boolean - element presence
        """
        found = False
        expected_condition = expected_conditions.presence_of_element_located
        if not expected:
            expected_condition = expected_conditions.staleness_of

        self.logger.debug('Checking presence of web element with xpath: {}. Expected: {!s}'.format(xpath, expected))
        found = self._get_element(xpath, expected_condition, wait) is not None
        self.logger.debug('Presence check of web element with xpath: {}. Result: {!s}'.format(xpath, found))
        return found

    @log_exception('Failed visible check of web element with xpath: {}')
    def is_visible(self, xpath, wait=None, expected=True):
        """
        Visibility check of web element on the UI.
        :param xpath: str - web element xpath
        :param wait: int - wait time
        :param expected: boolean - expected to be visible
        :return: boolean - element visibility
        """
        visible = False
        expected_condition = expected_conditions.visibility_of_element_located
        if not expected:
            expected_condition = expected_conditions.invisibility_of_element_located

        self.logger.debug('Checking visibility of web element with xpath: {}. Expected: {!s}'.format(xpath, expected))
        found = self._get_element(xpath, expected_condition, wait).is_displayed()
        self.logger.debug('Visible check of web element with xpath: {}. Result: {!s}'.format(xpath, found))
        return found

    @log_exception('Failed to click web element with xpath: {}')
    def click(self, xpath):
        """
        Click web element with given xpath
        :type xpath: str - web element xpath
        """
        self.logger.info('Clicking web element with xpath: {}'.format(xpath))
        self._get_element(xpath, expected_conditions.element_to_be_clickable).click()
        self.logger.info('Clicked web element with xpath: {}'.format(xpath))

    @log_exception('Failed to type text into web element with xpath: {}')
    def type(self, xpath, text):
        """
        Type text into input field with given xpath
        :type xpath: str - web element xpath
        :type text: str - text to type
        """
        self.logger.info('Typing "{}" into field with xpath: {}'.format(text, xpath))
        self._get_element(xpath, expected_conditions.visibility_of_element_located).send_keys(text)
        self.logger.info('Typed "{}" into field with xpath: {}'.format(text, xpath))

    def execute_script(self, element, script):
        """
        Execute JavaScript on the web element
        :type element: selenium.webdriver.remote.webelement.WebElement
        :type script: str - JS script body
        :return: result of script execution
        """
        if not element:
            self.logger.error('Element is None. Cannot execute JS')
            raise ValueError('Argument element cannot be None')
        return self.browser.execute_script("return arguments[0].{}".format(script), element)

    @log_exception('Failed to mouse over web element with xpath: {}')
    def mouse_over(self, xpath):
        """
        Simulate mouse cursor over given web element.
        :type xpath: str - web element xpath
        """
        actions = ActionChains(self.browser)
        actions.move_to_element(self._get_element(xpath)).perform()
        self.logger.info('Mouse over web element with xpath: {}'.format(xpath))

    @log_exception('Failed open URL: {}')
    def open(self, url):
        """
        Open given URL in browser
        :type url: str - URL to open
        """
        self.browser.get(url)
        self.logger.info('Opened URL: {}'.format(url))

    @log_exception('Cannot switch to frame: {}')
    def switch_to_frame(self, xpath):
        """
        Switch to frame
        :param xpath: str - frame xpath
        """
        self.browser.switch_to.frame(self._get_element(xpath))

    @log_exception('Cannot switch to default frame')
    def switch_to_default_frame(self):
        """
        Switch to default frame
        """
        self.browser.switch_to.default_content()

    @log_exception('Cannot get text located: {}')
    def get_text(self, xpath):
        """
        Get text of the web element
        :param xpath: str - web element xpath
        """
        return self._get_element(xpath).text

    @log_exception('Cannot send ENTER to the web element with xpath: {}')
    def send_enter(self, xpath):
        """
        Emulate sending ENTER key from keyboard to the given web element.
        :param xpath: str - web element xpath
        """
        self._get_element(xpath).send_keys(Keys.ENTER)
