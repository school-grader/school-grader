__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

import threading
import _thread
import unittest
from unittest.mock import patch
from abc import ABC, abstractmethod
from typing import List, Callable, Union
from io import StringIO
from collections import deque
import sys
import importlib.util
import re
import os
from school_grader import HTMLTestResult
from school_grader.json_test_result import JSONTestResult
import inspect
import argparse


class Equality(ABC):
    """Abstract base class for equality validation."""

    @abstractmethod
    def validate(self, unittest: unittest.TestCase, value_to_test: str, fail_message: str):
        """Validate equality between `value_to_test` and the expected value.

        Args:
            unittest: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        pass


class AlmostEqualNumber(Equality):
    """Class for almost equal numerical validation."""

    def __init__(self, expected: str, precisions: List[int]):
        """Initialize the class with the expected value and the precision values.

        Args:
            expected: The expected value as a string.
            precisions: List of precisions, where each precision specifies the maximum difference
                between the expected number and the result number that will be considered equal.
        """
        self.expected = expected
        self.precisions = precisions

    def validate(self, unittest: unittest.TestCase, value_to_test: str, fail_message: str):
        """Validate almost equal numerical equality between `value_to_test` and the expected value.

        Args:
            unittest: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        expected_numbers = list(
            map(float, re.findall(r'[-+]?\d*\.\d+|\d+', self.expected)))
        result_numbers = list(
            map(float, re.findall(r'[-+]?\d*\.\d+|\d+', value_to_test)))

        if len(self.precisions) != len(expected_numbers):
            raise AssertionError(
                "Number of precisions does not match the number of expected numbers")

        if len(expected_numbers) != len(result_numbers):
            raise AssertionError(
                f"Expected {len(expected_numbers)} numbers, but got {len(result_numbers)}")

        for expected_number, result_number, precision in zip(expected_numbers, result_numbers, self.precisions):
            unittest.assertAlmostEqual(float(expected_number), float(
                result_number), precision, fail_message)


def timeout(timeout_time):
    """
    Decorator that sets a timer for a function execution.
    If the function execution takes longer than `timeout_time` seconds,
    the main thread of the program will be interrupted.

    :param timeout_time: The number of seconds after which to interrupt the main thread.
    :return: The decorated function.
    """
    def decorator(function):
        """
        The actual decorator function that sets the timer and raises an exception
        if the function execution takes longer than `timeout_time` seconds.

        :param function: The function to be decorated.
        :return: The decorated function `inner`.
        """
        def inner(*args, **kwargs):
            """
            The decorated function that sets the timer and raises an exception
            if the function execution takes longer than `timeout_time` seconds.

            :param *args: The positional arguments passed to the decorated function.
            :param **kwargs: The keyword arguments passed to the decorated function.
            """
            timer = None
            try:
                if timeout_time is not None:
                    timer = threading.Timer(
                        timeout_time, lambda: _thread.interrupt_main())
                    timer.start()
                function(*args, **kwargs)
            except KeyboardInterrupt:
                raise TimeoutError(
                    f'Program execution did not finish within the allotted time of {timeout_time} seconds. You may be in an infinite loop.')
            finally:
                if timer:
                    timer.cancel()
        return inner
    return decorator


class TestCase(unittest.TestCase, ABC):
    """Abstract base class for test cases."""
    tests_case = []

    def __init__(self, test_name: str, timeout: float, fail_message: str):
        super().__init__()
        self.tests_case.append(self)
        self.shortDescription = lambda: test_name
        self._timeout = timeout
        self._fail_message = fail_message
        self._dirname = os.getcwd()
        self.line_number = inspect.currentframe().f_back.f_back.f_lineno

    @abstractmethod
    def runTest(self):
        """Run the test case."""
        pass


class FileTestCase(TestCase):
    """Custom test case class for testing python code"""

    def __init__(self, test_name: str, file_name: str, expected_output: List[Union[str, Equality]], mock_input: List[str] = [], timeout: float = 1, fail_message: str = None):
        """
        Initializes the test case with the given test name, file name, mock input, expected output, timeout and fail message

        :param test_name: name of the test
        :param file_name: name of the python file to be tested
        :param expected_output: list of str or Equality objects to be used as expected outputs
        :param mock_input: list of strings to be used as inputs
        :param timeout: maximum time in seconds that the test can run
        :param fail_message: message to be displayed in case of failure
        """
        super().__init__(test_name, timeout, fail_message)
        self._file_name = file_name
        self._mock_input = mock_input
        self._expected_output = expected_output

    def run_whole_file(self):
        try:
            spec = importlib.util.spec_from_file_location(
                self._file_name, os.path.join(self._dirname, f'{self._file_name}.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'File {self._file_name}.py not found. Your current working directory is {self._dirname}.')

    def override_input(self):
        queue = deque(self._mock_input)

        def fake_input(*_):
            if not queue:
                raise AssertionError("Too many input calls. Check your code")
            return queue.popleft()
        return fake_input

    def runTest(self):
        @timeout(self._timeout)
        def exec_test():
            with patch('builtins.input', self.override_input()), patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    self.run_whole_file()
                    output = fake_out.getvalue().strip().splitlines()

                    if (len(output) != len(self._expected_output)):
                        raise AssertionError(
                            f'The output of your program contains {len(output)} lines. You should have {len(self._expected_output)} lines')
                    for result, expected in zip(output, self._expected_output):
                        if isinstance(expected, str):
                            self.assertEqual(result, expected,
                                             self._fail_message)
                        else:
                            expected.validate(self, result, self._fail_message)
                finally:
                    sys.stdout = sys.__stdout__
        exec_test()


class FunctionTestCase(TestCase):
    """A basic test case class for running unit tests.

    Attributes:
        test_name (str): The name of the test case.
        result_func (Callable): A function that returns the result to be tested.
        expected_result: The expected result from the result_func.
        timeout (float): The maximum time in seconds allowed for the test to complete.
        fail_message (str, optional): A custom message to display on test failure. Default is None.
    """

    def __init__(self, test_name: str, result_func: Callable, expected_result, timeout: float = 1, fail_message: str = None):
        """Initialize the test case with the required attributes.

        Args:
            test_name (str): The name of the test case.
            result_func (Callable): A function that returns the result to be tested.
            expected_result: The expected result from the result_func.
            timeout (float): The maximum time in seconds allowed for the test to complete.
            fail_message (str, optional): A custom message to display on test failure. Default is None.
        """
        super().__init__(test_name, timeout, fail_message)
        self._result_func = result_func
        self._expected_result = expected_result

    def runTest(self):
        """Execute the test case and check the result against the expected result."""
        @timeout(self._timeout)
        def exec_test():
            """Execute the test within a time limit defined by the timeout attribute."""
            self.assertEqual(self._expected_result,
                             self._result_func(), self._fail_message)
        exec_test()


def run_tests(generate_html: bool = True):
    """
    Run all the tests in the BasicTestCase and FunctionTestCase classes.

    :param generate_html: Whether to generate an HTML report of the test results. Default is True.
    """
    if not TestCase.tests_case:
        raise ValueError("No test cases were added to the test suite.")
    
    suite = unittest.TestSuite()
    suite.addTests(TestCase.tests_case)

    parser = argparse.ArgumentParser()
    parser.add_argument('--extension', action='store_true')
    args = parser.parse_args()

    if args.extension:
        runner = unittest.TextTestRunner(resultclass=JSONTestResult)
        with patch('sys.stdout', new=StringIO()) as _:
            result = runner.run(unittest.TestSuite(TestCase.tests_case))
        result.print_report()
        return

    if generate_html:
        runner = unittest.TextTestRunner(resultclass=HTMLTestResult)
        result = runner.run(suite)
        result.generate()
    else:
        runner = unittest.TextTestRunner()
        runner.run(suite)
    
    
