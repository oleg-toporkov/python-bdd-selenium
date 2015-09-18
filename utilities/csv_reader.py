"""
Created on September 18, 2015

@author: oleg-toporkov
"""
import csv
import os


class CSVReader(object):
    """
    Util class for parsing CSV files.
    """
    @staticmethod
    def read_all(path):
        """
        Parse CSV file and return all key/value pairs in dict.
        Header row must be Name,Value
        Quote character - ". Delimiter - ,
        :param path: full path to CSV file
        :return: dict with all key/values except of header row.
        """
        values = {}

        if os.path.exists(path):
            with open(path) as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
                for row in reader:
                    values[row['Name']] = row['Value']
        return values
