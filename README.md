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
- Visual Studio Code extension

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
```
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
```
from school_grader import FileTestCase, Equal, run_test
FileTestCase('Test #1',
             'assignment1',
             ['kayak hi bonjour'],
             ['Palindrome words:kayak',
              'Non-palindrome words:hi bonjour']
             )

FileTestCase('Test #2',
             'assignment1',
             ['level racecar madam level'],
             ['Palindrome words:level racecar madam level',
              'Non-palindrome words:']
             )

FileTestCase('Test #3',
             'assignment1',
             ['hello world goodbye'],
             ['Palindrome words:',
              'Non-palindrome words:hello world goodbye']
             )

run_tests()
```

This will generate an HTML report that will automatically open in the browser.

![HTML report](https://github.com/school-grader/school-grader/blob/main/assets/html_report1.PNG?raw=true)

If there is an error in the student code, the report will look like this.

![HTML report](https://github.com/school-grader/school-grader/blob/main/assets/html_report2.PNG?raw=true)

You can also test for float variables.

The second parameter in AlmostEqualNumber define the number of decimal places to check in order to perform the comparison
### assignment2.py
```
import math
# Start your softmax here
numbers = [int(number) for number in input("Please enter a list of numbers: ").split(" ")]
denominator = sum([math.exp(number) for number in numbers])
result = [str(math.exp(number)/denominator) for number in numbers]
print(" ".join(result))
```
You can write test case for this assignment using the following code.
```
from school_grader import FileTestCase, AlmostEqualNumber, run_test
file="assignment2"

FileTestCase(
    test_name="Exemple1", 
    filename=file, 
    mock_input=["1 2 3 4 1 2 3"], 
    expected_output=[AlmostEqualNumber("0.023640543021591385 0.06426165851049616 0.17468129859572226 0.4748329997443803 0.023640543021591385 0.06426165851049616 0.17468129859572226", [5 for _ in range(7)])]
)

FileTestCase(
    test_name="Exemple2", 
    filename=file, 
    mock_input=["-4 0 4"], 
    expected_output=[AlmostEqualNumber("0.0003293204389638929 0.017980286735531547 0.9816903928255045", [5 for _ in range(3)])]
)

FileTestCase(
    test_name="Exemple3", 
    filename=file, 
    mock_input=["0 0 0"], 
    expected_output=[AlmostEqualNumber("0.3333333333333333 0.3333333333333333 0.3333333333333333", [5 for _ in range(3)])]
)

FileTestCase(
    test_name="Exemple4", 
    filename=file, 
    mock_input=["1 0 1 0 1 0 1"], 
    expected_output=[AlmostEqualNumber("0.19593864937345473 0.0720818008353937 0.19593864937345473 0.0720818008353937 0.19593864937345473 0.0720818008353937 0.19593864937345473", [5 for _ in range(7)])]
)

run_tests()
```
## Extension for Visual Studio Code

You can download a Visual Studio Code extension that will provide coloring when running tests.
### assignment3.py
```
print('Hi')
```
You can run the tests with these buttons.
![Buttons](https://github.com/school-grader/school-grader/blob/main/assets/extension2.PNG?raw=true)


The result will look like this. When you hover on a test, you will see the Stack trace.
![Result](https://github.com/school-grader/school-grader/blob/main/assets/extension1.PNG?raw=true)
