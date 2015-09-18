"""
Created on September 18, 2015

@author: oleg-toporkov
"""
from datetime import datetime
import logging.config
import os

from utilities.config import Config


class Logger(object):

    @staticmethod
    def configure_logging():
        """
        Perform logging configuration from file named log.ini in root folder.
        """
        if not os.path.exists(Config.LOG_DIR):
            os.mkdir(Config.LOG_DIR)
            
        logging.config.fileConfig('log.ini', defaults={'logdir': Config.LOG_DIR,
                                                       'datetime': str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f'))})

    @staticmethod
    def create_test_folder(test_id):
        test_id = test_id.replace(' ', '_')
        report_dir = '{}/{}'.format(Config.LOG_DIR, test_id)

        if not os.path.exists(report_dir):
            os.mkdir(report_dir)
