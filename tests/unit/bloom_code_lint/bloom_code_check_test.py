"""
Unit tests for the Bloom Code checker script.
"""
import pathlib
import textwrap

import pytest

from bloom_code_check import (
    RuleFunction,
    build_context,
    check_comprehension_layout,
    check_declaration_order,
    check_docstring_summary_line,
    check_exit_statement_spacing,
    check_from_imports,
    check_future_imports,
    check_implicit_string_concatenation,
    check_import_aliases,
    check_multiple_calls_per_line,
    check_nested_functions,
    check_one_item_per_line,
    check_raise_inline_message,
    check_short_names,
    check_source,
    check_tuple_parentheses,
    check_tuple_returns,
    check_type_hints,
    check_variable_reassignment,
    main,
)


def codes_for(
    rule_function: RuleFunction,
    source: str,
) -> list[str]:
    """
    Run a single rule over dedented source and return the violation codes found.
    """
    dedented_source = textwrap.dedent(source)
    local_packages = frozenset(['my_project'])
    context = build_context(
        dedented_source,
        'example.py',
        local_packages,
    )
    violations = rule_function(context)
    codes = [
        violation.code
        for violation
        in violations
    ]

    return codes


class TestCheckNestedFunctions:
    def test_inner_function_is_reported(self) -> None:
        source = '''
            def outer():
                def inner():
                    return 1
                return inner()
        '''
        result = codes_for(
            check_nested_functions,
            source,
        )
        expected = ['BLOOM001']

        assert result == expected

    def test_method_inside_class_is_not_reported(self) -> None:
        source = '''
            class Thing:
                def method(self):
                    return 1
        '''
        result = codes_for(
            check_nested_functions,
            source,
        )
        expected = []

        assert result == expected


class TestCheckImportAliases:
    def test_from_import_alias_is_reported(self) -> None:
        source = '''
            from my_project.models import User as U
        '''
        result = codes_for(
            check_import_aliases,
            source,
        )
        expected = ['BLOOM002']

        assert result == expected

    def test_module_alias_is_reported(self) -> None:
        source = '''
            import numpy as np
        '''
        result = codes_for(
            check_import_aliases,
            source,
        )
        expected = ['BLOOM002']

        assert result == expected

    def test_plain_import_is_not_reported(self) -> None:
        source = '''
            import pathlib
        '''
        result = codes_for(
            check_import_aliases,
            source,
        )
        expected = []

        assert result == expected


class TestCheckFromImports:
    def test_local_package_from_import_is_allowed(self) -> None:
        source = '''
            from my_project.models import User
        '''
        result = codes_for(
            check_from_imports,
            source,
        )
        expected = []

        assert result == expected

    def test_relative_from_import_is_allowed(self) -> None:
        source = '''
            from .models import User
        '''
        result = codes_for(
            check_from_imports,
            source,
        )
        expected = []

        assert result == expected

    def test_standard_library_from_import_is_reported(self) -> None:
        source = '''
            from pathlib import Path
        '''
        result = codes_for(
            check_from_imports,
            source,
        )
        expected = ['BLOOM003']

        assert result == expected


class TestCheckFutureImports:
    def test_future_import_is_reported(self) -> None:
        source = '''
            from __future__ import annotations
        '''
        result = codes_for(
            check_future_imports,
            source,
        )
        expected = ['BLOOM004']

        assert result == expected


class TestCheckShortNames:
    def test_short_loop_target_is_reported(self) -> None:
        source = '''
            for i in range(3):
                print(i)
        '''
        result = codes_for(
            check_short_names,
            source,
        )
        expected = ['BLOOM005']

        assert result == expected

    def test_short_parameter_is_reported(self) -> None:
        source = '''
            def compute(x: int) -> int:
                return x
        '''
        result = codes_for(
            check_short_names,
            source,
        )
        expected = ['BLOOM005']

        assert result == expected

    def test_two_character_variable_is_reported(self) -> None:
        source = '''
            df = 1
        '''
        result = codes_for(
            check_short_names,
            source,
        )
        expected = ['BLOOM005']

        assert result == expected

    def test_underscore_placeholder_is_allowed(self) -> None:
        source = '''
            first, _ = pair
        '''
        result = codes_for(
            check_short_names,
            source,
        )
        expected = []

        assert result == expected


class TestCheckVariableReassignment:
    def test_assignment_in_exclusive_branches_is_allowed(self) -> None:
        source = '''
            def compute(flag):
                if flag:
                    total = 1
                elif flag is None:
                    total = 2
                else:
                    total = 3
                return total
        '''
        result = codes_for(
            check_variable_reassignment,
            source,
        )
        expected = []

        assert result == expected

    def test_augmented_assignment_is_reported(self) -> None:
        source = '''
            def compute():
                total = 1
                total += 1
                return total
        '''
        result = codes_for(
            check_variable_reassignment,
            source,
        )
        expected = ['BLOOM006']

        assert result == expected

    def test_reassigned_local_is_reported(self) -> None:
        source = '''
            def compute():
                total = 1
                total = total + 1
                return total
        '''
        result = codes_for(
            check_variable_reassignment,
            source,
        )
        expected = ['BLOOM006']

        assert result == expected

    def test_single_assignment_is_allowed(self) -> None:
        source = '''
            def compute():
                total = 1
                other = 2
                return total
        '''
        result = codes_for(
            check_variable_reassignment,
            source,
        )
        expected = []

        assert result == expected


class TestCheckTupleReturns:
    def test_single_value_return_is_allowed(self) -> None:
        source = '''
            def compute():
                return 1
        '''
        result = codes_for(
            check_tuple_returns,
            source,
        )
        expected = []

        assert result == expected

    def test_tuple_return_is_reported(self) -> None:
        source = '''
            def compute():
                return (1, 2)
        '''
        result = codes_for(
            check_tuple_returns,
            source,
        )
        expected = ['BLOOM007']

        assert result == expected


class TestCheckImplicitStringConcatenation:
    def test_adjacent_literals_are_reported(self) -> None:
        source = '''
            message = (
                "hello "
                "world"
            )
        '''
        result = codes_for(
            check_implicit_string_concatenation,
            source,
        )
        expected = ['BLOOM008']

        assert result == expected

    def test_joined_strings_are_allowed(self) -> None:
        source = '''
            message = "".join(["hello ", "world"])
        '''
        result = codes_for(
            check_implicit_string_concatenation,
            source,
        )
        expected = []

        assert result == expected


class TestCheckDeclarationOrder:
    def test_internal_function_before_public_is_reported(self) -> None:
        source = '''
            def _helper():
                return 1


            def public():
                return 2
        '''
        result = codes_for(
            check_declaration_order,
            source,
        )
        expected = ['BLOOM009']

        assert result == expected

    def test_non_alphabetical_public_functions_are_reported(self) -> None:
        source = '''
            def zebra():
                return 1


            def apple():
                return 2
        '''
        result = codes_for(
            check_declaration_order,
            source,
        )
        expected = ['BLOOM009']

        assert result == expected

    def test_property_before_public_method_is_allowed(self) -> None:
        source = '''
            class Thing:
                def __init__(self):
                    self.value = 1

                @property
                def value_doubled(self):
                    return self.value * 2

                def apply(self):
                    return 1

                def _shield(self):
                    return 2

                def __hide(self):
                    return 3
        '''
        result = codes_for(
            check_declaration_order,
            source,
        )
        expected = []

        assert result == expected

    def test_public_method_before_constructor_is_reported(self) -> None:
        source = '''
            class Thing:
                def run(self):
                    return 1

                def __init__(self):
                    self.value = 1
        '''
        result = codes_for(
            check_declaration_order,
            source,
        )
        expected = ['BLOOM009']

        assert result == expected


class TestCheckOneItemPerLine:
    def test_multi_argument_call_on_one_line_is_reported(self) -> None:
        source = '''
            compute(1, 2)
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = ['BLOOM010']

        assert result == expected

    def test_multi_element_list_on_one_line_is_reported(self) -> None:
        source = '''
            values = [1, 2]
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = ['BLOOM010']

        assert result == expected

    def test_multi_name_from_import_on_one_line_is_reported(self) -> None:
        source = '''
            from my_project.models import User, Account
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = ['BLOOM010']

        assert result == expected

    def test_multi_parameter_definition_on_one_line_is_reported(self) -> None:
        source = '''
            def compute(first, second):
                return first
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = ['BLOOM010']

        assert result == expected

    def test_one_item_per_line_layout_is_allowed(self) -> None:
        source = '''
            values = [
                1,
                2,
            ]
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = []

        assert result == expected

    def test_single_argument_call_is_allowed(self) -> None:
        source = '''
            compute(1)
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = []

        assert result == expected

    def test_type_parameter_list_inside_subscript_is_allowed(self) -> None:
        source = '''
            Handler = typing.Callable[[str, int], bool]
        '''
        result = codes_for(
            check_one_item_per_line,
            source,
        )
        expected = []

        assert result == expected


class TestCheckTypeHints:
    def test_missing_parameter_hint_is_reported(self) -> None:
        source = '''
            def compute(value) -> int:
                return value
        '''
        result = codes_for(
            check_type_hints,
            source,
        )
        expected = ['BLOOM011']

        assert result == expected

    def test_missing_return_hint_is_reported(self) -> None:
        source = '''
            def compute(value: int):
                return value
        '''
        result = codes_for(
            check_type_hints,
            source,
        )
        expected = ['BLOOM011']

        assert result == expected

    def test_self_parameter_needs_no_hint(self) -> None:
        source = '''
            class Thing:
                def compute(self) -> int:
                    return 1
        '''
        result = codes_for(
            check_type_hints,
            source,
        )
        expected = []

        assert result == expected


class TestCheckMultipleCallsPerLine:
    def test_nested_calls_on_one_line_are_reported(self) -> None:
        source = '''
            value = outer(inner(1))
        '''
        result = codes_for(
            check_multiple_calls_per_line,
            source,
        )
        expected = ['BLOOM012']

        assert result == expected

    def test_nested_calls_on_separate_lines_are_allowed(self) -> None:
        source = '''
            value = outer(
                inner(1)
            )
        '''
        result = codes_for(
            check_multiple_calls_per_line,
            source,
        )
        expected = []

        assert result == expected


class TestCheckRaiseInlineMessage:
    def test_literal_message_in_raise_is_reported(self) -> None:
        source = '''
            raise ValueError("bad value")
        '''
        result = codes_for(
            check_raise_inline_message,
            source,
        )
        expected = ['BLOOM013']

        assert result == expected

    def test_message_variable_in_raise_is_allowed(self) -> None:
        source = '''
            message = "bad value"
            raise ValueError(message)
        '''
        result = codes_for(
            check_raise_inline_message,
            source,
        )
        expected = []

        assert result == expected


class TestCheckTupleParentheses:
    def test_bare_tuple_assignment_is_reported(self) -> None:
        source = '''
            pair = 1, 2
        '''
        result = codes_for(
            check_tuple_parentheses,
            source,
        )
        expected = ['BLOOM014']

        assert result == expected

    def test_loop_target_unpacking_is_allowed(self) -> None:
        source = '''
            for key, value in pairs:
                print(key)
        '''
        result = codes_for(
            check_tuple_parentheses,
            source,
        )
        expected = []

        assert result == expected

    def test_parenthesized_tuple_is_allowed(self) -> None:
        source = '''
            pair = (1, 2)
        '''
        result = codes_for(
            check_tuple_parentheses,
            source,
        )
        expected = []

        assert result == expected


class TestCheckExitStatementSpacing:
    def test_block_directly_after_docstring_is_allowed(self) -> None:
        source = '''
            def compute(flag):
                """
                Compute the thing.
                """
                if flag:
                    return 1

                return 2
        '''
        result = codes_for(
            check_exit_statement_spacing,
            source,
        )
        expected = []

        assert result == expected

    def test_block_with_exit_needs_blank_line_after(self) -> None:
        source = '''
            def compute(flag):
                if flag:
                    return 1
                total = 2

                return total
        '''
        result = codes_for(
            check_exit_statement_spacing,
            source,
        )
        expected = ['BLOOM015']

        assert result == expected

    def test_return_after_blank_line_is_allowed(self) -> None:
        source = '''
            def compute():
                total = 1

                return total
        '''
        result = codes_for(
            check_exit_statement_spacing,
            source,
        )
        expected = []

        assert result == expected

    def test_return_as_only_statement_is_allowed(self) -> None:
        source = '''
            def compute():
                return 1
        '''
        result = codes_for(
            check_exit_statement_spacing,
            source,
        )
        expected = []

        assert result == expected

    def test_return_directly_after_code_is_reported(self) -> None:
        source = '''
            def compute():
                total = 1
                return total
        '''
        result = codes_for(
            check_exit_statement_spacing,
            source,
        )
        expected = ['BLOOM015']

        assert result == expected


class TestCheckComprehensionLayout:
    def test_single_line_comprehension_is_reported(self) -> None:
        source = '''
            values = [item for item in items if item]
        '''
        result = codes_for(
            check_comprehension_layout,
            source,
        )
        expected = ['BLOOM016']

        assert result == expected

    def test_split_comprehension_is_allowed(self) -> None:
        source = '''
            values = [
                item
                for item
                in items
                if item
            ]
        '''
        result = codes_for(
            check_comprehension_layout,
            source,
        )
        expected = []

        assert result == expected


class TestCheckDocstringSummaryLine:
    def test_one_line_docstring_is_allowed(self) -> None:
        source = '''
            def compute():
                """Compute the thing."""
                return 1
        '''
        result = codes_for(
            check_docstring_summary_line,
            source,
        )
        expected = []

        assert result == expected

    def test_summary_on_opening_line_is_reported(self) -> None:
        source = '''
            def compute():
                """Compute the thing.

                More detail here.
                """
                return 1
        '''
        result = codes_for(
            check_docstring_summary_line,
            source,
        )
        expected = ['BLOOM017']

        assert result == expected

    def test_summary_on_own_line_is_allowed(self) -> None:
        source = '''
            def compute():
                """
                Compute the thing.
                """
                return 1
        '''
        result = codes_for(
            check_docstring_summary_line,
            source,
        )
        expected = []

        assert result == expected


class TestCheckSource:
    def test_syntax_error_is_reported_as_violation(self) -> None:
        violations = check_source(
            'def broken(:\n',
            'example.py',
            frozenset(),
        )
        result = violations[0].code
        expected = 'BLOOM000'

        assert result == expected

    def test_violations_are_sorted_by_line(self) -> None:
        source = textwrap.dedent('''
            def compute():
                total = 1
                return total


            import numpy as np
        ''')
        violations = check_source(
            source,
            'example.py',
            frozenset(),
        )
        result = [
            violation.line
            for violation
            in violations
        ]
        expected = sorted(result)

        assert result == expected


class TestMain:
    def test_clean_file_returns_zero(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        clean_file = tmp_path / 'clean.py'
        clean_file.write_text(
            'import pathlib\n',
            encoding='utf-8',
        )
        clean_path = str(clean_file)
        result = main([clean_path])
        expected = 0

        assert result == expected

    def test_output_is_ascii_only(
        self,
        tmp_path: pathlib.Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        dirty_file = tmp_path / 'dirty.py'
        dirty_file.write_text(
            'import numpy as np\n',
            encoding='utf-8',
        )
        dirty_path = str(dirty_file)
        main([dirty_path])
        captured = capsys.readouterr()
        result = captured.out.isascii()
        expected = True

        assert result == expected

    def test_violating_file_returns_one(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        dirty_file = tmp_path / 'dirty.py'
        dirty_file.write_text(
            'import numpy as np\n',
            encoding='utf-8',
        )
        dirty_path = str(dirty_file)
        result = main([dirty_path])
        expected = 1

        assert result == expected
