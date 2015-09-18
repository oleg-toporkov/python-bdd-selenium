"""
Created on September 18, 2015

@author: oleg-toporkov
"""
import os

from core.base_page import BasePage
from utilities.csv_reader import CSVReader


class SearchPage(BasePage):
    """
    Search page representation.
    Class for UI actions related to this page
    """
    def __init__(self, locators_path, browser):
        """
        :type locators_path: str - path to *.def.csv file with locators for this page
        :type browser: selenium.webdriver.firefox.webdriver.WebDriver
        """
        self.locators = CSVReader.read_all(os.path.abspath(locators_path))
        super(SearchPage, self).__init__(browser)

    def get_repositories(self):
        return self.get_elements(self.locators['Title repository'])
