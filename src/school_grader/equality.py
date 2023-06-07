__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

import re
from typing import List, Tuple
import unittest
from abc import ABC, abstractmethod


class Equality(ABC):
    """Abstract base class for equality definitions"""

    def __init__(self, expected: str):
        """Initialize the class with the expected value.

        Args:
            expected: The expected value as a string.
        """
        self.expected = expected

    @abstractmethod
    def validate(self, test_case: unittest.TestCase, value_to_test: str, fail_message: str) -> None:
        """Validate equality between `value_to_test` and the expected value.

        Args:
            test_case: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        pass


class AlmostEqual(Equality):
    """Abstract base class for almost equal validation."""
    pass


class AlmostEqualString(AlmostEqual):
    """Class for almost equal string validation."""

    def __init__(self, expected: str, max_distance: int = 2):
        """Initialize the class with the expected value and the Levenshtein distance.

        Args:
            expected: The expected value as a string.
            distance: The Levenshtein distance. Defaults to 2.
        """
        super().__init__(expected)
        self.max_distance = max_distance

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Calculate the Levenshtein distance between two strings.

        Args:
            s1: The first string.
            s2: The second string.

        Returns:
            The Levenshtein distance between `s1` and `s2`.
        """
        # Create a matrix with dimensions (length of s1 + 1) x (length of s2 + 1)
        matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]

        # Initialize the first row and column of the matrix
        for i in range(len(s1) + 1):
            matrix[i][0] = i
        for j in range(len(s2) + 1):
            matrix[0][j] = j

        # Fill in the rest of the matrix
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,           # deletion
                    matrix[i][j - 1] + 1,           # insertion
                    matrix[i - 1][j - 1] + cost     # substitution
                )

        # The final value in the bottom-right corner of the matrix is the Levenshtein distance
        return matrix[-1][-1]

    def validate(self, test_case: unittest.TestCase, value_to_test: str, fail_message: str) -> None:
        """Validate almost equal string equality between `value_to_test` and the expected value.

        Args:
            test_case: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        test_case.assertLessEqual(AlmostEqualString._levenshtein(value_to_test, self.expected), self.max_distance, fail_message)


class AlmostEqualNumber(AlmostEqual):
    """Class for almost equal numerical validation."""

    def __init__(self, expected: str, precision: int = 7):
        """Initialize the class with the expected value and the precision values.

        Args:
            expected: The expected value as a string.
            precisions: The number of decimal places to compare. Defaults to 7.
        """
        super().__init__(expected)
        self.precision = precision

    def validate(self, test_case: unittest.TestCase, value_to_test: str, fail_message: str) -> None:
        """Validate almost equal numerical equality between `value_to_test` and the expected value.

        Args:
            test_case: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        expected_numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|\d+', self.expected)))
        result_numbers = list(map(float, re.findall(r'[-+]?\d*\.\d+|\d+', value_to_test)))

        if len(expected_numbers) != len(result_numbers):
            raise AssertionError(f"Expected {len(expected_numbers)} numbers, but got {len(result_numbers)}")

        for expected_number, result_number in zip(expected_numbers, result_numbers):
            test_case.assertAlmostEqual(float(expected_number), float(result_number), self.precision, fail_message)


class Equal(Equality):
    """Abstract base class for equality validation."""
    @staticmethod
    @abstractmethod
    def alter_expected_and_value_to_test(expected: str, value_to_test: str) -> Tuple[str, str]:
        """Alter the expected and value_to_test values before running the equality check.

        Args:
            value_to_test: The value to test for equality.

        Returns:
            A tuple containing the expected and value_to_test values after alteration.
        """
        pass

    def validate(self, test_case: unittest.TestCase, value_to_test: str, fail_message: str) -> None:
        """Validate after altering .

        Args:
            test_case: Instance of `unittest.TestCase` to run the equality check.
            value_to_test: The value to test for equality.
            fail_message: The message to display if the equality check fails.
        """
        expected, value_to_test = self.alter_expected_and_value_to_test(self.expected, value_to_test)
        test_case.assertEqual(expected, value_to_test, fail_message)

def CombineEqualities(*equalities: List[Equal]) -> Equal:
    """Combine multiple equalities into a single equality.

    Args:
        *equalities: The equalities to combine.

    Returns:
        A single equality that combines all of the provided equalities.
    """
    class CombinedEquality(Equal):
        """Class for combined equality validation."""

        def __init__(self, expected: str):
            """Initialize the class with the expected string value.

            Args:
                expected: The expected string value.
            """
            super().__init__(expected)

        @staticmethod
        def alter_expected_and_value_to_test(expected: str, value_to_test: str) -> Tuple[str, str]:
            """Alter the expected and value_to_test values before running the equality check.

            Args:
                value_to_test: The value to test for equality.

            Returns:
                A tuple containing the expected and value_to_test values after alteration.
            """
            for equality in equalities:
                if not isinstance(equality, Equal):
                    raise TypeError(f"Expected an instance of Equal, but got {type(equality)}")
                expected, value_to_test = equality.alter_expected_and_value_to_test(expected, value_to_test)
            return expected, value_to_test
    return CombinedEquality


class CaseInsensitiveStringEquality(Equal):
    """Class for case-insensitive string equality validation."""

    def __init__(self, expected: str):
        """Initialize the class with the expected string value.

        Args:
            expected: The expected string value.
        """
        super().__init__(expected)

    @staticmethod
    def alter_expected_and_value_to_test(expected: str, value_to_test: str) -> Tuple[str, str]:
        """Alter the expected and value_to_test values before running the equality check by converting both to lowercase.

        Args:
            expected: The expected value.
            value_to_test: The value to test for equality.

        Returns:
            A tuple containing the expected and value_to_test values after alteration by converting both to lowercase.
        """
        return expected.lower(), value_to_test.lower()


class WhiteSpaceInsensitiveEquality(Equal):
    """Class for space-insensitive equality validation."""

    def __init__(self, expected: str):
        """Initialize the class with the expected string value.

        Args:
            expected: The expected string value.
        """
        super().__init__(expected)

    @staticmethod
    def alter_expected_and_value_to_test(expected: str, value_to_test: str) -> Tuple[str, str]:
        """Alter the expected and value_to_test values before running the equality check by removing all whitespace.

        Args:
            expected: The expected value.
            value_to_test: The value to test for equality.

        Returns:
            A tuple containing the expected and value_to_test values after alteration by removing all whitespace.
        """
        return re.sub(r"\s+", "", expected), re.sub(r"\s+", "", value_to_test)


class ContainsEquality(Equal):
    """Class for contains equality validation. Checks if the expected value is contained in the value to test."""

    def __init__(self, expected: str):
        """Initialize the class with the expected string value.

        Args:
            expected: The expected string value. This value will be checked to see if it is contained in the value to test.
        """
        super().__init__(expected)

    @staticmethod
    def _find_largest_substring(word: str, target: str) -> str:
        word_length = len(word)
        target_length = len(target)

        # Create a table to store the lengths of common substrings
        table: List[List[int]] = [[0] * (target_length + 1) for _ in range(word_length + 1)]

        # Variables to track the longest common substring and its length
        max_length = 0
        end_index = 0

        # Fill the table using dynamic programming
        for i in range(1, word_length + 1):
            for j in range(1, target_length + 1):
                if word[i - 1] == target[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                    if table[i][j] > max_length:
                        max_length = table[i][j]
                        end_index = i

        # Extract the longest common substring
        largest_substring = word[end_index - max_length:end_index]
        return largest_substring

    @staticmethod
    def alter_expected_and_value_to_test(expected: str, value_to_test: str) -> Tuple[str, str]:
        """Alter the expected and value_to_test values before running the equality check by keeping only the expected value if it is contained in the value to test.

        Args:
            expected: The expected value.
            value_to_test: The value to test for equality.

        Returns:
            A tuple containing the expected and value_to_test values after alteration by keeping only the expected value if it is contained in the value to test.
        """
        if expected in value_to_test:
            return expected, expected
        else:
            # Return the biggest substring of the value to test that is contained in the expected value.
            return expected, ContainsEquality._find_largest_substring(value_to_test, expected)
