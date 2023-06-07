__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

from school_grader.html_test_result import HTMLTestResult
from school_grader.json_test_result import JSONTestResult
from school_grader.test_case import FileTestCase, FunctionTestCase, run_tests, TestCase, timeout
from school_grader.equality import Equality, AlmostEqualNumber, AlmostEqualString, CaseInsensitiveStringEquality, WhiteSpaceInsensitiveEquality, ContainsEquality, CombineEqualities
