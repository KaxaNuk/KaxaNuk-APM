---
description: Python Test Writing Guidelines
applyTo: "**/tests/**/*.py"
metadata:
  version: 0.2.1
---
# Test Writing Guidelines
These guidelines are meant for pytest or similar libraries that allow using the following functionalities.


## Unit Tests


### Unit Test Folder Structure
Unit tests are located in the `tests/unit` folder.
Each subfolder of this folder follows the same structure as the subfolders inside the main `src/%MY_PROJECT_NAME%`
folder, where `%MY_PROJECT_NAME%` is the name of the project.
The unit test files themselves have the suffix `_test.py` after the original file name.
Optionally, we can split a single file's tests into multiple test files, each one concerning a specific type of test.
All folders inside the `tests/unit` folder are regular Python packages, always containing an `__init__.py` file even
if it's empty.
External fixtures can be placed in a `fixtures` subfolder under the folder containing the tests that need them.


### Example Unit Test Folder Structure
```
├── src
│   └── %MY_PROJECT_NAME%
│       ├── models
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services
│       │   ├── __init__.py
│       │   └── user_service.py
│       └── utils
│           ├── __init__.py
│           └── date_utils.py
└── tests
    └── unit
        ├── __init__.py
        ├── models
        │   ├── __init__.py
        │   └── user_test.py
        ├── services
        │   ├── __init__.py
        │   ├── user_service_static_methods_test.py
        │   └── user_service_instance_methods_test.py
        └── utils
            ├── __init__.py
            ├── date_utils_test.py
            └── fixtures
                ├── __init__.py
                └── dates_example.csv
```

### Unit Test File Structure
All unit test methods in a test file are grouped into classes, each class representing a single function or method
being tested.
Each class starts with the `Test` prefix, optionally followed by `Private` if the method being tested is
private/protected, followed by the name of the function or method it tests.
Each test method starts with the `test_` prefix, followed by a short description of what makes the test unique.
We only use a single `assert` statement per test method, except in special cases where the setup of the test is
complex and requires multiple intermediate assertions between steps.
Tests need to prioritize readability and auditability over conciseness.
When using fixtures, avoid using chains of intermediate functions for transforming them into the different test case
inputs and expected outputs, as it becomes hard to understand what the test is actually doing.


#### Example Unit Test File Structure
```
# tests/unit/services/user_service_instance_methods_test.py
class TestSomeMethod:
    def test_some_method_single_digit_id(self):
        user_service = UserService()
        result = user_service.some_method(1)
        expected = 25
        
        assert result == expected
    
    # more tests...
    
class TestPrivateSomeOtherMethod:
    def test_private_some_other_method_with_string(self):
        user_service = UserService()
        result = user_service._some_other_method("hello")
        expected = "world"
        
        assert result == expected
        
    # more tests...
```
