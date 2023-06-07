# Python Student Testing Framework

## Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [How to use](#how-to-use)
- [Extension for Visual Studio Code](#extension-for-visual-studio-code)

## Introduction

Welcome to the Python Student Testing Framework! This README provides a brief overview of what the framework is and how to use it. The framework is designed for instructors and TAs to easily test and grade students Python code.

## Features

- Automated testing of students' code against a set of test cases
- Support for multiple test cases and multiple functions
- Ability to define custom tests and assertions
- Clear and detailed feedback for students on test results
- Display HTML report

## Installation

To use the Python Student Testing Framework, you will need to have Python installed on your machine. Then, simply clone the repository or install with `pip install school-grader`


## Contributing

The Python Student Testing Framework is an open-source project and contributions are welcome. 

## License

The Python Student Testing Framework is released under the MIT license. See the LICENSE file for more information.

## Contact

If you have any questions or issues, please create a GitHub issue or reach out to the project maintainers at marcolivier.derouin@poulet-frit.com


## How to use
Let's say you have given an assignment to your students.

### assignment1.py
```python
words = input("Please enter a list of words separated by spaces: ").split(" ")

palindrome_words = []
non_palindrome_words = []

for word in words:
    lowercase_word = word.lower()
    if lowercase_word == lowercase_word[::-1]:
        palindrome_words.append(word)
    else:
        non_palindrome_words.append(word)

print("Palindrome words:" + " ".join(palindrome_words))
print("Non-palindrome words:" + " ".join(non_palindrome_words))
```
You can write test case for this assignment using the following code.
```python
from school_grader import FileTestCase, run_tests
FileTestCase('Test #1', # Test name
             'assignment1', # File name
             ['Palindrome words:kayak', 'Non-palindrome words:hi bonjour'], # Expected output, in a list of strings, each element is a printed line
             ['kayak hi bonjour'], # Mock input, in a list of strings, each element is a input line
            )

FileTestCase('Test #2',
             'assignment1',
             ['Palindrome words:level racecar madam level', 'Non-palindrome words:'],
             ['level racecar madam level'], # This parameter is optional, if not provided, the test will input nothing
            )

FileTestCase('Test #3',
             'assignment1',
             ['Palindrome words:', 'Non-palindrome words:hello world goodbye'],
             ['hello world goodbye'],
             timeout=4, # This parameter is optional, if not provided, the test will timeout after 1 second
            )

FileTestCase('Test #4',
             'assignment1',
             ['Palindrome words:KAyak', 'Non-palindrome words:hello world goodbye'],
             ['hello world goodbye KAyak'],
             fail_message='Did you think about case sensitivity?', # This parameter is optional, if not provided, the test will fail with a default message
            )

run_tests()
```

This will generate an HTML report that will automatically open in the browser.

![HTML report](https://github.com/school-grader/school-grader/blob/main/assets/html_report1.PNG?raw=true)

If there is an error in the student code, the report will look like this.

![HTML report](https://github.com/school-grader/school-grader/blob/main/assets/html_report2.PNG?raw=true)

## Expected outputs

The expected_output list in FileTestCase can also contains an Equality class object in order to help with string comparison

### Almost equal

- `AlmostEqualString`: This class is used for almost equal string validation:
   - `expected`: The expected string value for comparison.
   - `max_distance`: The maximum Levenshtein distance allowed between the expected value and the value to test.

- `AlmostEqualNumber`: This class is used for almost equal numerical validation:
   - `expected`: The expected string value for comparison.
   - `precision`: The number of decimal places to compare for floating-point numbers.

### Equal

- `CaseInsensitiveStringEquality`: This class is used for case-insensitive string equality validation:
   - `expected`: The expected string value for comparison.

- `WhiteSpaceInsensitiveEquality`: This class is used for space-insensitive equality validation:
   - `expected`: The expected string value for comparison.

- `ContainsEquality`: This class is used for contains equality validation:
   - `expected`: The expected string value to check if it is contained in the value to test.

### Combinations of Equal classes

- `CombineEqualities()`: This function combines multiple instances of `Equal` subclasses and returns a new subclass that combines all the provided equalities.


Here is an example using CaseInsentiveStringEquality

```python
from school_grader import FileTestCase, run_tests, CaseInsensitiveStringEquality
FileTestCase('Test #1', # Test name
             'assignment1', # File name
             [CaseInsensitiveStringEquality('palindrome words:kayak'), CaseInsensitiveStringEquality('non-palindrome words:hi bonjour')], # Expected output
             ['kayak hi bonjour'], # Mock input, in a list of strings, each element is a input line
            )

run_tests() # Run all tests
```

Here is an example combining CaseInsentiveStringEquality and WhiteSpaceInsensitiveEquality

```python
from school_grader import FileTestCase, run_tests, CaseInsensitiveStringEquality, WhiteSpaceInsensitiveEquality, CombineEqualities

Insentive = CombineEqualities(CaseInsensitiveStringEquality, WhiteSpaceInsensitiveEquality)

FileTestCase('Test #1', # Test name
             'assignment1', # File name
             [Insentive('palindromewords:kayak'), Insentive('non-palindromewords:hibonjour')], # Expected output
             ['kayak hi bonjour'], # Mock input, in a list of strings, each element is a input line
            )

run_tests() # Run all tests
```
## Extension for Visual Studio Code

You can download a Visual Studio Code extension that will provide coloring when running tests.
```python
print('Hi')
```
You can run the tests with these buttons.

![Buttons](https://github.com/school-grader/school-grader/blob/main/assets/extension2.PNG?raw=true)


The result will look like this. When you hover on a test, you will see the Stack trace.

![Result](https://github.com/school-grader/school-grader/blob/main/assets/extension1.PNG?raw=true)