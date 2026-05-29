---
description: Python Bloom Code Style Guide
applyTo: "**/*.py"
metadata:
  version: 1.2.3
---
# Python "Bloom Code" Style Guide
This is a strict superset of PEP 8 meant for code legibility, maintainability, and verifiability.
Its principal objective is maximizing reading speed and quick understanding for someone unfamiliar with the codebase.
The main ideas are:
- Organize all code in a predictable manner, for example by grouping declarations based on a common characteristic
    and then alphabetically within each group.
- Avoid abbreviations, acronyms, aliases, and mnemonics.
- Use line breaks judiciously to separate logical concepts within a statement and reduce visual clutter.


## Structure
Functions in a module must be organized in blocks in this order:
1. Public functions
2. Internal functions (starting with a single underscore)

Methods in classes must be organized in blocks in this order:
1. Abstract methods (if it's an abstract class)
2. Constructor
3. Public Properties
4. Protected Properties (starting with a single underscore)
5. Private Properties (starting with two underscores)
6. Public methods
7. Protected methods (starting with a single underscore)
8. Private methods (starting with two underscores)

Within each block, functions and methods should be ordered alphabetically by their name.

EXTREMELY IMPORTANT: Nested/inner functions (i.e. one function defined inside another function or method) are ABSOLUTELY FORBIDDEN.
Never declare a function inside another function or method!


## Import Restrictions
Import aliases are forbidden.
Using `from module import x` is only allowed for local application/library specific imports. All other standard library
and third party libraries must import the module itself and use qualified names for any module contents.
Do not use `from __future__` imports. For annotation references that would require them use quotes instead.


## Additional Restrictions
Always use meaningful variable names, and avoid any variable names with less than 3 characters.
Avoid reassigning new values to existing variables, as each variable models a distinct concept, and preserving the full
trace of intermediate objects simplifies debugging.

Add precise type-hints to all function parameters and returns.
Do not include the parameter and return types in the docstrings when the function is already type-hinted.

Tuples always need to be defined with parentheses.
Never use implicit string concatenation by leaving only whitespace between strings. Always use the `join` method instead.

Avoid returning tuples from functions and methods when trying to encapsulate different return type values. Instead,
rethink your approach to see if the logic can be instead separated into multiple functions that each return a single
value. If separating in infeasible, return either a dictionary or a dataclass instead.

To choose between a dictionary and a dataclass for return types, use a dataclass for static structures with fixed
attributes, and a dictionary for dynamic structures with variable keys.

Any construct necessarily or optionally delimited by parentheses, brackets, or braces, which includes 2 or more items
separated by commas, logical operators, or arithmetic operators must have each item on a separate line with the
appropriate indent. Examples of this construct type include: lists, tuples, dictionaries, sets, function arguments and
parameters, and `from` imports.

Strive to have at most one function/method/operator call per line. When chaining nested calls, each call must be on its
own line with the appropriate indent, as shown in the following example:
```python
my_var = my_func(
    my_other_func(
        my_third_func(
            my_arg,
            my_other_arg,
        )
    )
)
```

Function-exit statements (`return`, `yield`, and `raise`) should be given visual prominence as follows:
- Any conditional or iteration block that contains a function-exit statement should have one blank line before it if
    the preceding code, comment, or block originates from the same indent level, and always one blank line after it.
- If the code or comment line directly preceding a function-exit statement is at the same indent level as that exit
    statement, a blank line should be inserted between them for visual separation.

Comprehensions and generators should separate in different lines the output expression, the `for` loop, and the `if` clause.

The opening summary line in a multiline docstring should start in its own line.

When raising an exception, always put the error message in an intermediate variable (for example `msg`) and then use
that variable in the exception call to make the trace more readable.
