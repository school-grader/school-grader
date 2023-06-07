__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

import threading
import _thread
import unittest
from unittest.mock import patch
from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Union
from io import StringIO
from collections import deque
import sys
import importlib.util
import os
import inspect
import argparse
from school_grader.html_test_result import HTMLTestResult
from school_grader.json_test_result import JSONTestResult
from school_grader.equality import Equality


def timeout(timeout_time: Optional[int]):
    """
    Decorator that sets a timer for a function execution.
    If the function execution takes longer than `timeout_time` seconds,
    the main thread of the program will be interrupted.

    Args:
        timeout_time (int or float): The number of seconds after which to interrupt the main thread.

    Returns:
        callable: The decorated function.
    """
    def decorator(function: Callable):
        """
        The actual decorator function that sets the timer and raises an exception
        if the function execution takes longer than `timeout_time` seconds.

        Args:
            function: The function to be decorated.

        Returns:
            The decorated function `inner`.
        """
        def inner(*args, **kwargs):
            """
            The decorated function that sets the timer and raises an exception
            if the function execution takes longer than `timeout_time` seconds.

            Args:
                *args: The positional arguments passed to the decorated function.
                **kwargs: The keyword arguments passed to the decorated function.
            """
            timer = None
            try:
                if timeout_time is not None:
                    timer = threading.Timer(timeout_time, lambda: _thread.interrupt_main())
                    timer.start()
                function(*args, **kwargs)
            except KeyboardInterrupt:
                raise TimeoutError(f'Program execution did not finish within the allotted time of {timeout_time} seconds. You may be in an infinite loop.')
            finally:
                if timer is not None:
                    timer.cancel()
        return inner
    return decorator


class TestCase(unittest.TestCase, ABC):
    """Abstract base class for test cases."""
    tests_case = []

    def __init__(self, test_name: str, timeout_time: float, fail_message: str):
        super().__init__()
        self.tests_case.append(self)
        self.shortDescription = lambda: test_name
        self._timeout_time = timeout_time
        self._fail_message = fail_message
        self._dirname = os.getcwd()
        self.line_number = inspect.currentframe().f_back.f_back.f_lineno

    @abstractmethod
    def runTest(self) -> None:
        """Run the test case."""
        pass


class FileTestCase(TestCase):
    """Custom test case class for testing python code"""

    def __init__(self, test_name: str, file_name: str, expected_output: List[Union[str, Equality]], mock_input: List[str] = [], timeout_time: float = 1, fail_message: str = None):
        """
        Initializes the test case with the given attributes.

        Args:
            test_name (str): Name of the test.
            file_name (str): Name of the Python file to be tested.
            expected_output (list[str] or list[Equality]): List of str or Equality objects to be used as expected outputs.
            mock_input (list[str]): List of strings to be used as inputs.
            timeout_time (int or float): Maximum time in seconds that the test can run.
            fail_message (str): Message to be displayed in case of failure.

        Returns:
            None
        """
        super().__init__(test_name, timeout_time, fail_message)
        self._file_name = file_name
        self._mock_input = mock_input
        self._expected_output = expected_output

    def run_whole_file(self) -> None:
        """
        Run the whole file.

        Returns:
            None
        """
        try:
            spec = importlib.util.spec_from_file_location(self._file_name, os.path.join(self._dirname, f'{self._file_name}.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File {self._file_name}.py not found. Your current working directory is {self._dirname}.') from e

    def override_input(self) -> Callable[[], str]:
        """
        Override the input function to use the mock input.

        Returns:
            A function that returns the next mock input.
        """
        queue = deque(self._mock_input)
        def fake_input(*_, **__) -> str:
            if not queue:
                raise AssertionError("Too many input calls. Check your code")
            return queue.popleft()
        return fake_input

    def runTest(self):
        """
        Run the test case.

        Returns:
            None
        """
        @timeout(self._timeout_time)
        def exec_test():
            """
            Execute the test case.

            Returns:
                None
            """
            with patch('builtins.input', self.override_input()), patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    self.run_whole_file()
                    output = fake_out.getvalue().strip().splitlines()

                    if (len(output) != len(self._expected_output)):
                        raise AssertionError(f'The output of your program contains {len(output)} lines. You should have {len(self._expected_output)} lines')
                    for result, expected in zip(output, self._expected_output):
                        if isinstance(expected, str):
                            self.assertEqual(result, expected,self._fail_message)
                        elif isinstance(expected, Equality):
                            expected.validate(self, result, self._fail_message)
                        else:
                            raise TypeError(f'Expected output should be a string or an Equality object. Got {type(expected)} instead.')
                finally:
                    sys.stdout = sys.__stdout__
        exec_test()


class FunctionTestCase(TestCase):
    """A basic test case class for running unit tests."""

    def __init__(self, test_name: str, result_func: Callable, expected_result, timeout_time: float = 1, fail_message: str = None):
        """
        Initialize the test case with the required attributes.

        Args:
            test_name (str): The name of the test case.
            result_func (function): A function that returns the result to be tested.
            expected_result: The expected result from the result_func.
            timeout_time (int or float): The maximum time in seconds allowed for the test to complete.
            fail_message (str, optional): A custom message to display on test failure. Default is None.

        Returns:
            None
        """
        super().__init__(test_name, timeout_time, fail_message)
        self._result_func = result_func
        self._expected_result = expected_result

    def runTest(self):
        """Execute the test case and check the result against the expected result."""
        @timeout(self._timeout_time)
        def exec_test():
            """Execute the test within a time limit defined by the timeout attribute."""
            self.assertEqual(self._expected_result, self._result_func(), self._fail_message)
        exec_test()


def run_tests(generate_html: bool = True):
    """
    Run all the tests in the BasicTestCase and FunctionTestCase classes.

    Args:
        generate_html (bool): Whether to generate an HTML report of the test results. Default is True.

    Returns:
        bool: The value of the `generate_html` parameter indicating whether an HTML report is generated.
    """
    if not TestCase.tests_case:
        raise ValueError("No test cases were added to the test suite.")
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--extension', action='store_true')
    args = parser.parse_args()

    suite = unittest.TestSuite()
    suite.addTests(TestCase.tests_case)

    def json_runner() -> None:
        """
        Run the test suite and generate a JSON report of the results.

        Args:
            None

        Returns:
            None
        """
        with patch('sys.stdout', new=StringIO()) as _:
            runner = unittest.TextTestRunner(resultclass=JSONTestResult)
            result: JSONTestResult = runner.run(suite)
        result.print_report()

    def html_runner() -> None:
        """
        Run the test suite and generate an HTML report of the results.

        Args:
            None

        Returns:
            None
        """
        runner = unittest.TextTestRunner(resultclass=HTMLTestResult)
        result: HTMLTestResult = runner.run(suite)
        result.generate()

    def text_runner() -> None:
        """
        Run the test suite and generate a text report of the results.

        Args:
            None

        Returns:
            None
        """
        runner = unittest.TextTestRunner()
        runner.run(suite)
    
    if args.extension:
        json_runner()
        return

    if generate_html:
        html_runner()
    else:
        text_runner()
