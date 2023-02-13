from abc import abstractmethod, ABC
__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

import unittest
import json
from dataclasses import dataclass




@dataclass
class Result:
    """A class for the result of a test."""
    description: int
    status: str
    message: str    


class JSONTestResult(unittest.TextTestResult):
    """A class for the JSON result of a test."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._test_result = dict()

    def addSuccess(self, test):
        """Adds a successful test to the JSON result."""
        self._test_result[test.line_number] = Result(test.shortDescription(), "success", "Test passed").__dict__

    def addFailure(self, test, err):
        """Adds a failed test to the JSON result."""
        self._test_result[test.line_number] = Result(test.shortDescription(), "failure", self._exc_info_to_string(err, test)).__dict__
        

    def addError(self, test, err):
        """Adds an error test to the JSON result."""
        self._test_result[test.line_number] = Result(test.shortDescription(), "error", self._exc_info_to_string(err, test)).__dict__

    def print_report(self):
        """Prints the JSON result of a test."""
        print(json.dumps(self._test_result))
        
