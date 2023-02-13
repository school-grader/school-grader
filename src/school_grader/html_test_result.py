__author__ = "Marc-Olivier Derouin"
__email__ = "marcolivier.derouin@poulet-frit.com"

from abc import ABC, abstractmethod
from typing import List
import unittest
import webbrowser


HTML_BEGIN = """<html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            table {
                border-radius: 10px;
                width: 100%;
                margin: 40px auto;
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
                text-align: center;
                border-spacing: 0;
            }
            table tr:first-child td {
                border-top: 0;
            }

            table tr td:first-child {
                border-left: 0;
            }

            table tr:last-child td {
                border-bottom: 0;
            }

            table tr td:last-child {
                border-right: 0;
            }
            th, td {
                border: solid 1px #68706a29;
                padding: 20px;
                font-size: 16px;
                font-weight: 500;
                color: #333;
                text-align: center;
                vertical-align: middle;
            }
            th {
                background-color: #ddd;
                font-weight: bold;
            }
            pre {
                background-color: #f6f8fa;
                border-radius: 10px;
                font-size: 85%;
                line-height: 1.45;
                overflow: auto;
                padding: 16px;
                text-align: left;
                margin: 20px 0;
            }
            body {
                padding: 20px;
                background-color: #f2f2f2;
                font-family: 'Roboto', sans-serif;
            }
            .error {
                background-color: #FFE844;
            }
            .pass {
                background-color: #A6FB88;
            }
            .fail {
                background-color: #FF4444;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Test name</th>
                <th>Directory</th>
                <th>Result</th>
                <th>Stack trace</th>
            </tr>"""

HTML_END = """</table>
    </body>
</html>"""


def sanitize_html(html_string: str):
    return html_string.replace("<", "&lt;").replace(">", "&gt;")


class HTMLResult(ABC):
    """An abstract class for the HTML result of a test."""

    def __init__(self, test):
        self._test = test

    @abstractmethod
    def generate_html(self):
        """Generates the HTML result of a test."""
        return f"""
        <tr>
            <td><b>{sanitize_html(self._test.shortDescription())}</b></td>
            <td><b>{sanitize_html(self._test._dirname)}</b></td>"""


class HTMLSuccessResult(HTMLResult):
    """A class for the HTML result of a successful test."""

    def __init__(self, test):
        super().__init__(test)

    def generate_html(self):
        """Generates the HTML result of a successful test."""
        return f"""
        {super().generate_html()}
            <td class="pass"><b>PASS</b></td>
            <td></td>
        </tr>
        """


class HTMLFailureResult(HTMLResult):
    """A class for the HTML result of a failed test."""

    def __init__(self, test, stack_trace: str):
        super().__init__(test)
        self._stack_trace = stack_trace

    def generate_html(self):
        """Generates the HTML result of a failed test."""
        return f"""
        {super().generate_html()}
            <td class="fail"><b>FAIL</b></td>
            <td><pre>{sanitize_html(self._stack_trace)}</pre></td>
        </tr>
        """


class HTMLErrorResult(HTMLResult):
    """A class for the HTML result of a failed test."""

    def __init__(self, test, stack_trace: str):
        super().__init__(test)
        self._stack_trace = stack_trace

    def generate_html(self):
        """Generates the HTML result of a failed test."""
        return f"""
        {super().generate_html()}
            <td class="error"><b>ERROR</b></td>
            <td><pre>{sanitize_html(self._stack_trace)}</pre></td>
        </tr>
        """


class HTMLTestResult(unittest.TextTestResult):
    """A class for the HTML result of a test."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._test_result: List[HTMLResult] = []

    def addSuccess(self, test):
        """Adds a successful test to the HTML result."""
        self._test_result.append(HTMLSuccessResult(test))

    def addFailure(self, test, err):
        """Adds a failed test to the HTML result."""
        self._test_result.append(HTMLFailureResult(
            test, self._exc_info_to_string(err, test)))

    def addError(self, test, err):
        """Adds an error test to the HTML result."""
        self._test_result.append(HTMLErrorResult(
            test, self._exc_info_to_string(err, test)))

    def generate(self):
        """Generates the HTML result of a test."""
        html_content = HTML_BEGIN
        for result in self._test_result:
            html_content += result.generate_html()
        html_content += HTML_END
        with open("results.html", "w") as f:
            f.write(html_content)
        webbrowser.open("results.html", new=2)
