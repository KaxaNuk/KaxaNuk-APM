"""
Bloom Code checker.

Mechanically verifies the lintable subset of the KaxaNuk "Bloom Code" style guide
and prints one line per violation with a remediation hint. Console output is ASCII only.

Usage:
    python bloom_code_check.py <path> [<path> ...] [--local-package NAME ...]

Exit code 0 when every file is clean, 1 when any violation was found.
"""
import argparse
import ast
import dataclasses
import io
import pathlib
import sys
import tokenize
import typing

TRY_STAR_TYPE = getattr(
    ast,
    'TryStar',
    ast.Try,
)
COMPOUND_STATEMENT_TYPES = (
    ast.AsyncFor,
    ast.AsyncWith,
    ast.For,
    ast.If,
    ast.Match,
    ast.Try,
    TRY_STAR_TYPE,
    ast.While,
    ast.With,
)
EXCLUSIVE_BRANCH_TYPES = (
    ast.If,
    ast.Match,
    ast.Try,
    TRY_STAR_TYPE,
)
COMPREHENSION_TYPES = (
    ast.DictComp,
    ast.GeneratorExp,
    ast.ListComp,
    ast.SetComp,
)
DOCUMENTED_NODE_TYPES = (
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.FunctionDef,
    ast.Module,
)
FUNCTION_DEFINITION_TYPES = (
    ast.AsyncFunctionDef,
    ast.FunctionDef,
)
IGNORED_TOKEN_TYPES = frozenset([
    tokenize.COMMENT,
    tokenize.NL,
])
MINIMUM_NAME_LENGTH = 3
PROPERTY_DECORATOR_NAMES = frozenset([
    'deleter',
    'getter',
    'property',
    'setter',
])
RULE_MESSAGES = {
    'BLOOM000': 'syntax error; fix the file before checking style',
    'BLOOM001': 'nested function definition; move it to module level as an internal (underscore-prefixed) function',
    'BLOOM002': 'import alias; import the module itself and use its qualified name',
    'BLOOM003': "'from x import y' on a non-local module; use 'import x' and qualify names (declare local packages with --local-package)",
    'BLOOM004': "'from __future__' import; quote forward references instead",
    'BLOOM005': 'name shorter than 3 characters; use a meaningful name',
    'BLOOM006': 'variable reassigned; bind a new name for each distinct concept',
    'BLOOM007': 'function returns a tuple; split into single-value functions or return a dataclass or dict',
    'BLOOM008': 'implicit string concatenation; use str.join instead',
    'BLOOM009': 'declaration out of order; blocks are public then internal (methods: abstract, __init__, properties public/protected/private, methods public/protected/private), alphabetical within each block',
    'BLOOM010': 'construct with 2+ comma-separated items on one line; put each item on its own line',
    'BLOOM011': 'missing type hint on a parameter or on the return value',
    'BLOOM012': 'more than one call on a line; put each nested call on its own line',
    'BLOOM013': 'raise with an inline message; assign the message to a variable (for example msg) first',
    'BLOOM014': 'tuple without parentheses; always parenthesize tuples',
    'BLOOM015': 'return/yield/raise, or a block containing one, without the required blank line before or after it',
    'BLOOM016': 'comprehension on one line; put the output expression, each for clause and the if clause on separate lines',
    'BLOOM017': 'multiline docstring summary on the opening line; start the summary on its own line',
}
SCOPE_NODE_TYPES = (
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.FunctionDef,
    ast.Lambda,
)
STATEMENT_LIST_FIELDS = (
    'body',
    'finalbody',
    'orelse',
)
FSTRING_END_TOKEN = getattr(
    tokenize,
    'FSTRING_END',
    -1,
)
FSTRING_START_TOKEN = getattr(
    tokenize,
    'FSTRING_START',
    -1,
)
TSTRING_END_TOKEN = getattr(
    tokenize,
    'TSTRING_END',
    -1,
)
TSTRING_START_TOKEN = getattr(
    tokenize,
    'TSTRING_START',
    -1,
)
STRING_END_TOKEN_TYPES = frozenset([
    tokenize.STRING,
    FSTRING_END_TOKEN,
    TSTRING_END_TOKEN,
])
STRING_START_TOKEN_TYPES = frozenset([
    tokenize.STRING,
    FSTRING_START_TOKEN,
    TSTRING_START_TOKEN,
])


@dataclasses.dataclass(frozen=True)
class BoundName:
    """
    A name bound by an assignment, a parameter, a loop target or an except clause.
    """
    line: int
    name: str


@dataclasses.dataclass(
    frozen=True,
    order=True,
)
class Violation:
    """
    One style violation, sortable by line then code.
    """
    line: int
    code: str
    message: str


@dataclasses.dataclass(frozen=True)
class FileViolation:
    """
    A violation attached to the file it was found in.
    """
    path: pathlib.Path
    violation: Violation


@dataclasses.dataclass(frozen=True)
class SourceContext:
    """
    Everything a rule needs to inspect one source file.
    """
    filename: str
    lines: tuple[str, ...]
    local_packages: frozenset[str]
    source: str
    tree: ast.Module


RuleFunction = typing.Callable[[SourceContext], list[Violation]]


def build_context(
    source: str,
    filename: str,
    local_packages: frozenset[str],
) -> SourceContext:
    """
    Parse source into the context shared by every rule. Raises SyntaxError on invalid code.
    """
    tree = ast.parse(
        source,
        filename=filename,
    )
    split_lines = source.splitlines()
    lines = tuple(split_lines)

    return SourceContext(
        filename=filename,
        lines=lines,
        local_packages=local_packages,
        source=source,
        tree=tree,
    )


def check_comprehension_layout(context: SourceContext) -> list[Violation]:
    """
    BLOOM016: output expression, for clauses and if clause of a comprehension on separate lines.
    """
    violations = [
        _violation(
            'BLOOM016',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _is_compact_comprehension(node)
    ]

    return violations


def check_declaration_order(context: SourceContext) -> list[Violation]:
    """
    BLOOM009: functions and methods grouped in the prescribed blocks, alphabetical within each.
    """
    module_functions = [
        statement
        for statement
        in context.tree.body
        if _is_function_definition(statement)
    ]
    module_violations = _order_violations(
        module_functions,
        _module_function_rank,
    )
    classes = [
        node
        for node
        in ast.walk(context.tree)
        if _is_class_definition(node)
    ]
    class_violations = [
        violation
        for class_node
        in classes
        for violation
        in _class_order_violations(class_node)
    ]

    return module_violations + class_violations


def check_docstring_summary_line(context: SourceContext) -> list[Violation]:
    """
    BLOOM017: the summary of a multiline docstring starts on its own line.
    """
    documented_nodes = [
        node
        for node
        in ast.walk(context.tree)
        if _is_documented_node(node)
    ]
    violations = [
        _violation(
            'BLOOM017',
            node.body[0].lineno,
        )
        for node
        in documented_nodes
        if _has_summary_on_opening_line(node)
    ]

    return violations


def check_exit_statement_spacing(context: SourceContext) -> list[Violation]:
    """
    BLOOM015: blank line before an exit statement, and around a block that contains one.
    """
    violations = [
        violation
        for statements
        in _iter_statement_lists(context.tree)
        for violation
        in _statement_list_spacing_violations(
            statements,
            context.lines,
        )
    ]

    return violations


def check_file(
    path: pathlib.Path,
    local_packages: frozenset[str],
) -> list[Violation]:
    """
    Read one file and run every rule over it.
    """
    source = path.read_text(encoding='utf-8')
    filename = str(path)

    return check_source(
        source,
        filename,
        local_packages,
    )


def check_from_imports(context: SourceContext) -> list[Violation]:
    """
    BLOOM003: 'from x import y' is only allowed for local application packages.
    """
    violations = [
        _violation(
            'BLOOM003',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _is_foreign_from_import(
            node,
            context.local_packages,
        )
    ]

    return violations


def check_future_imports(context: SourceContext) -> list[Violation]:
    """
    BLOOM004: no 'from __future__' imports.
    """
    violations = [
        _violation(
            'BLOOM004',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _is_future_import(node)
    ]

    return violations


def check_implicit_string_concatenation(context: SourceContext) -> list[Violation]:
    """
    BLOOM008: no adjacent string literals joined by whitespace only.
    """
    reader = io.StringIO(context.source)
    token_stream = tokenize.generate_tokens(reader.readline)
    significant_tokens = [
        token
        for token
        in token_stream
        if token.type not in IGNORED_TOKEN_TYPES
    ]
    violations = [
        _violation(
            'BLOOM008',
            current.start[0],
        )
        for previous, current
        in zip(
            significant_tokens,
            significant_tokens[1:],
        )
        if previous.type in STRING_END_TOKEN_TYPES and current.type in STRING_START_TOKEN_TYPES
    ]

    return violations


def check_import_aliases(context: SourceContext) -> list[Violation]:
    """
    BLOOM002: no import aliases.
    """
    violations = [
        _violation(
            'BLOOM002',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _has_import_alias(node)
    ]

    return violations


def check_multiple_calls_per_line(context: SourceContext) -> list[Violation]:
    """
    BLOOM012: at most one call per line.
    """
    call_lines = [
        node.lineno
        for node
        in ast.walk(context.tree)
        if _is_call(node)
    ]
    repeated_lines = {
        line
        for line
        in call_lines
        if call_lines.count(line) > 1
    }
    violations = [
        _violation(
            'BLOOM012',
            line,
        )
        for line
        in sorted(repeated_lines)
    ]

    return violations


def check_nested_functions(context: SourceContext) -> list[Violation]:
    """
    BLOOM001: no function defined inside another function or method.
    """
    violations = [
        _violation(
            'BLOOM001',
            inner.lineno,
        )
        for outer
        in _iter_function_definitions(context.tree)
        for inner
        in ast.walk(outer)
        if inner is not outer and _is_function_definition(inner)
    ]

    return violations


def check_one_item_per_line(context: SourceContext) -> list[Violation]:
    """
    BLOOM010: constructs with two or more comma-separated items put each item on its own line.
    """
    parents = _build_parent_map(context.tree)
    violations = [
        _violation(
            'BLOOM010',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _breaks_one_item_per_line(
            node,
            parents,
        )
    ]

    return violations


def check_raise_inline_message(context: SourceContext) -> list[Violation]:
    """
    BLOOM013: exception messages go through an intermediate variable.
    """
    violations = [
        _violation(
            'BLOOM013',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _has_inline_raise_message(node)
    ]

    return violations


def check_short_names(context: SourceContext) -> list[Violation]:
    """
    BLOOM005: bound names are at least three characters long ('_' placeholder allowed).
    """
    violations = [
        _violation(
            'BLOOM005',
            bound_name.line,
        )
        for bound_name
        in _bound_names(context.tree)
        if _is_short_name(bound_name.name)
    ]

    return violations


def check_source(
    source: str,
    filename: str,
    local_packages: frozenset[str],
) -> list[Violation]:
    """
    Run every rule over one source string and return the violations sorted by line.
    """
    try:
        context = build_context(
            source,
            filename,
            local_packages,
        )
    except SyntaxError as error:
        line = error.lineno or 1
        detail = error.msg or 'invalid syntax'
        message = ''.join([
            RULE_MESSAGES['BLOOM000'],
            ' (',
            detail,
            ')',
        ])

        return [
            Violation(
                line=line,
                code='BLOOM000',
                message=message,
            ),
        ]

    violations = [
        violation
        for rule
        in _all_rules()
        for violation
        in rule(context)
    ]

    return sorted(violations)


def check_tuple_parentheses(context: SourceContext) -> list[Violation]:
    """
    BLOOM014: tuple literals are parenthesized (unpacking targets and subscripts excluded).
    """
    parents = _build_parent_map(context.tree)
    violations = [
        _violation(
            'BLOOM014',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _is_bare_tuple(
            node,
            parents,
            context.source,
        )
    ]

    return violations


def check_tuple_returns(context: SourceContext) -> list[Violation]:
    """
    BLOOM007: functions do not return tuples.
    """
    violations = [
        _violation(
            'BLOOM007',
            node.lineno,
        )
        for node
        in ast.walk(context.tree)
        if _is_tuple_return(node)
    ]

    return violations


def check_type_hints(context: SourceContext) -> list[Violation]:
    """
    BLOOM011: every parameter (except self/cls) and every return value is type-hinted.
    """
    method_ids = _method_node_ids(context.tree)
    violations = [
        _violation(
            'BLOOM011',
            function.lineno,
        )
        for function
        in _iter_function_definitions(context.tree)
        if _is_missing_type_hints(
            function,
            method_ids,
        )
    ]

    return violations


def check_variable_reassignment(context: SourceContext) -> list[Violation]:
    """
    BLOOM006: a variable is assigned once per scope.
    """
    scopes = [context.tree] + _iter_function_definitions(context.tree)
    violations = [
        violation
        for scope
        in scopes
        for violation
        in _reassignment_violations(scope)
    ]

    return violations


def main(argv: list[str] | None = None) -> int:
    """
    Command-line entry point. Prints violations and returns the process exit code.
    """
    parser = _build_argument_parser()
    arguments = parser.parse_args(argv)
    python_files = _collect_python_files(arguments.paths)
    working_directory = pathlib.Path.cwd()
    detected_packages = _detect_local_packages(working_directory)
    declared_packages = frozenset(arguments.local_packages)
    local_packages = detected_packages | declared_packages
    file_violations = [
        FileViolation(
            path=python_file,
            violation=violation,
        )
        for python_file
        in python_files
        for violation
        in check_file(
            python_file,
            local_packages,
        )
    ]
    for file_violation in file_violations:
        formatted = _format_violation(file_violation)
        print(formatted)
    file_count = len(python_files)
    violation_count = len(file_violations)

    if violation_count > 0:
        print(f'[x] {violation_count} Bloom Code violation(s) in {file_count} file(s)')

        return 1

    print(f'[ok] {file_count} file(s) clean')

    return 0


def _all_parameters(function: ast.AST) -> list[ast.arg]:
    """
    Every parameter of a function in declaration order, including *args and **kwargs.
    """
    arguments = function.args
    optional_parameters = [
        arguments.vararg,
        arguments.kwarg,
    ]
    present_optional = [
        parameter
        for parameter
        in optional_parameters
        if parameter is not None
    ]

    return arguments.posonlyargs + arguments.args + arguments.kwonlyargs + present_optional


def _all_rules() -> list[RuleFunction]:
    """
    Every rule function, in reporting order.
    """
    rules: list[RuleFunction] = [
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
        check_tuple_parentheses,
        check_tuple_returns,
        check_type_hints,
        check_variable_reassignment,
    ]

    return rules


def _assignment_targets(statement: ast.AST) -> list[BoundName]:
    """
    Names bound by an assignment statement (plain, annotated or augmented).
    """
    if _is_plain_assignment(statement):
        targets = statement.targets
    elif _is_single_target_assignment(statement):
        targets = [statement.target]
    else:
        targets = []
    name_nodes = [
        name_node
        for target
        in targets
        for name_node
        in _name_nodes(target)
    ]
    bound_names = [
        BoundName(
            line=name_node.lineno,
            name=name_node.id,
        )
        for name_node
        in name_nodes
    ]

    return bound_names


def _block_spacing_violations(
    statements: list[ast.stmt],
    index: int,
    lines: tuple[str, ...],
) -> list[Violation]:
    """
    Blank line required before and after a compound statement that contains an exit statement.
    """
    statement = statements[index]
    is_compound = isinstance(
        statement,
        COMPOUND_STATEMENT_TYPES,
    )

    if not is_compound or not _contains_exit_statement(statement):
        return []

    has_blank_before = _is_blank_line(
        lines,
        statement.lineno - 1,
    )
    has_blank_after = _is_blank_line(
        lines,
        statement.end_lineno + 1,
    )
    has_code_before = _has_code_before(
        statements,
        index,
    )
    is_last = index == len(statements) - 1
    missing_before = has_code_before and not has_blank_before
    missing_after = not is_last and not has_blank_after

    if missing_before or missing_after:
        return [
            _violation(
                'BLOOM015',
                statement.lineno,
            ),
        ]

    return []


def _bound_names(tree: ast.Module) -> list[BoundName]:
    """
    Every name bound anywhere in the module: stored names, parameters and except aliases.
    """
    stored_names = [
        BoundName(
            line=node.lineno,
            name=node.id,
        )
        for node
        in ast.walk(tree)
        if _is_stored_name(node)
    ]
    parameter_names = [
        BoundName(
            line=node.lineno,
            name=node.arg,
        )
        for node
        in ast.walk(tree)
        if _is_parameter(node)
    ]
    handler_names = [
        BoundName(
            line=node.lineno,
            name=node.name,
        )
        for node
        in ast.walk(tree)
        if _is_named_except_handler(node)
    ]

    return stored_names + parameter_names + handler_names


def _breaks_one_item_per_line(
    node: ast.AST,
    parents: dict[int, ast.AST],
) -> bool:
    """
    True when a multi-item construct keeps two items on one line or an item on the opening line.
    """
    items = _multi_item_children(
        node,
        parents,
    )

    if len(items) < 2:
        return False

    item_lines = [
        item.lineno
        for item
        in items
    ]

    return not _items_on_own_lines(
        node.lineno,
        item_lines,
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    """
    Command-line interface definition.
    """
    parser = argparse.ArgumentParser(
        description='Check Python files against the lintable subset of the Bloom Code style guide.',
    )
    parser.add_argument(
        'paths',
        help='Files or directories to check (directories are searched recursively for *.py).',
        nargs='+',
    )
    parser.add_argument(
        '--local-package',
        action='append',
        default=[],
        dest='local_packages',
        help="Top-level package name whose 'from x import y' imports are allowed. Repeatable.",
    )

    return parser


def _build_parent_map(tree: ast.Module) -> dict[int, ast.AST]:
    """
    Map from id(child node) to its parent node.
    """
    parents = {
        id(child): parent
        for parent
        in ast.walk(tree)
        for child
        in ast.iter_child_nodes(parent)
    }

    return parents


def _class_order_violations(class_node: ast.ClassDef) -> list[Violation]:
    """
    Ordering violations among the methods of one class.
    """
    methods = [
        statement
        for statement
        in class_node.body
        if _is_function_definition(statement)
    ]

    return _order_violations(
        methods,
        _method_rank,
    )


def _collect_python_files(paths: list[str]) -> list[pathlib.Path]:
    """
    Expand the command-line paths into a sorted, de-duplicated list of Python files.
    """
    python_files = [
        python_file
        for path_string
        in paths
        for python_file
        in _python_files_under(
            pathlib.Path(path_string)
        )
    ]
    unique_files = set(python_files)

    return sorted(unique_files)


def _comprehension_output(node: ast.AST) -> ast.AST:
    """
    The output expression of a comprehension (the key for dict comprehensions).
    """
    if _is_dict_comprehension(node):
        return node.key

    return node.elt


def _contains_exit_statement(statement: ast.AST) -> bool:
    """
    True when any statement inside the given one is an exit statement.
    """
    contains = any(
        _is_exit_statement(node)
        for node
        in ast.walk(statement)
    )

    return contains


def _decorator_name(decorator: ast.AST) -> str:
    """
    Bare name of one decorator expression, ignoring call parentheses and attribute owners.
    """
    if _is_call(decorator):
        return _decorator_name(decorator.func)

    if _is_attribute(decorator):
        return decorator.attr

    if _is_name(decorator):
        return decorator.id

    return ''


def _decorator_names(function: ast.AST) -> frozenset[str]:
    """
    Bare names of a function's decorators ('property', 'setter', 'abstractmethod', ...).
    """
    names = [
        _decorator_name(decorator)
        for decorator
        in function.decorator_list
    ]

    return frozenset(names)


def _dedupe_by_name(bound_names: list[BoundName]) -> list[BoundName]:
    """
    Keep the first binding of each name, preserving order.
    """
    unique = [
        bound_name
        for index, bound_name
        in enumerate(bound_names)
        if not _name_seen_before(
            bound_names,
            index,
        )
    ]

    return unique


def _detect_local_packages(root: pathlib.Path) -> frozenset[str]:
    """
    Top-level packages and modules found directly under the working directory or its src/ folder.
    """
    candidate_bases = [
        root,
        root / 'src',
    ]
    existing_bases = [
        base
        for base
        in candidate_bases
        if base.is_dir()
    ]
    package_names = {
        child.stem
        for base
        in existing_bases
        for child
        in base.iterdir()
        if _is_package_or_module(child)
    }

    return frozenset(package_names)


def _dict_items(node: ast.Dict) -> list[ast.AST]:
    """
    One representative node per dict entry: the key, or the value for '**' spreads.
    """
    items = [
        key if key is not None else value
        for key, value
        in zip(
            node.keys,
            node.values,
        )
    ]

    return items


def _direct_statement_lists(node: ast.AST) -> typing.Iterator[list[ast.stmt]]:
    """
    Statement lists directly owned by a node (bodies, else branches, handlers, match cases).
    """
    for field_name in STATEMENT_LIST_FIELDS:
        value = getattr(
            node,
            field_name,
            None,
        )

        if _is_statement_list(value):
            yield value

    handlers = getattr(
        node,
        'handlers',
        [],
    )

    for handler in handlers:
        yield handler.body

    cases = getattr(
        node,
        'cases',
        [],
    )

    for case in cases:
        yield case.body


def _exit_spacing_violations(
    statements: list[ast.stmt],
    index: int,
    lines: tuple[str, ...],
) -> list[Violation]:
    """
    Blank line required directly before an exit statement that follows code at the same level.
    """
    statement = statements[index]

    if not _is_exit_statement(statement):
        return []

    has_code_before = _has_code_before(
        statements,
        index,
    )
    has_blank_before = _is_blank_line(
        lines,
        statement.lineno - 1,
    )

    if has_code_before and not has_blank_before:
        return [
            _violation(
                'BLOOM015',
                statement.lineno,
            ),
        ]

    return []


def _format_violation(file_violation: FileViolation) -> str:
    """
    One report line: path:line: CODE message.
    """
    violation = file_violation.violation
    parts = [
        str(file_violation.path),
        ':',
        str(violation.line),
        ': ',
        violation.code,
        ' ',
        violation.message,
    ]

    return ''.join(parts)


def _has_code_before(
    statements: list[ast.stmt],
    index: int,
) -> bool:
    """
    True when a statement other than a leading docstring precedes the given index.
    """
    if index == 0:
        return False

    if index > 1:
        return True

    return not _is_docstring_statement(statements[0])


def _has_import_alias(node: ast.AST) -> bool:
    """
    True for an import statement where any imported name carries an 'as' alias.
    """
    if not _is_import_statement(node):
        return False

    has_alias = any(
        alias.asname is not None
        for alias
        in node.names
    )

    return has_alias


def _has_inline_raise_message(node: ast.AST) -> bool:
    """
    True for 'raise Error("literal")' or 'raise Error(f"...")'.
    """
    if not _is_raise(node):
        return False

    if node.exc is None or not _is_call(node.exc):
        return False

    has_literal = any(
        _is_string_expression(argument)
        for argument
        in node.exc.args
    )

    return has_literal


def _has_summary_on_opening_line(node: ast.AST) -> bool:
    """
    True for a multiline docstring whose text starts right after the opening quotes.
    """
    docstring = ast.get_docstring(
        node,
        clean=False,
    )

    if docstring is None:
        return False

    return '\n' in docstring and not docstring.startswith('\n')


def _is_attribute(node: ast.AST) -> bool:
    """
    True for an attribute access node.
    """
    return isinstance(
        node,
        ast.Attribute,
    )


def _is_bare_tuple(
    node: ast.AST,
    parents: dict[int, ast.AST],
    source: str,
) -> bool:
    """
    True for a loaded tuple literal written without parentheses (subscripts excluded).
    """
    if not _is_tuple(node):
        return False

    if not _is_load_context(node):
        return False

    node_id = id(node)
    parent = parents.get(node_id)

    if _is_subscript(parent):
        return False

    segment = ast.get_source_segment(
        source,
        node,
    )

    if segment is None:
        return False

    return not segment.startswith('(')


def _is_blank_line(
    lines: tuple[str, ...],
    line_number: int,
) -> bool:
    """
    True when the 1-based line is blank or outside the file.
    """
    if line_number < 1 or line_number > len(lines):
        return True

    content = lines[line_number - 1]

    return content.strip() == ''


def _is_call(node: ast.AST) -> bool:
    """
    True for a call expression.
    """
    return isinstance(
        node,
        ast.Call,
    )


def _is_class_definition(node: ast.AST) -> bool:
    """
    True for a class definition.
    """
    return isinstance(
        node,
        ast.ClassDef,
    )


def _is_compact_comprehension(node: ast.AST) -> bool:
    """
    True for a comprehension whose output, for clauses and if clauses share lines.
    """
    if not _is_comprehension(node):
        return False

    output = _comprehension_output(node)
    generators = node.generators
    first_generator = generators[0]

    if output.end_lineno >= first_generator.target.lineno:
        return True

    consecutive_pairs = zip(
        generators,
        generators[1:],
    )
    generators_share_line = any(
        current.target.lineno <= previous.iter.end_lineno
        for previous, current
        in consecutive_pairs
    )

    if generators_share_line:
        return True

    ifs_share_line = any(
        condition.lineno <= generator.iter.end_lineno
        for generator
        in generators
        for condition
        in generator.ifs
    )

    return ifs_share_line


def _is_comprehension(node: ast.AST) -> bool:
    """
    True for list, set, dict or generator comprehensions.
    """
    return isinstance(
        node,
        COMPREHENSION_TYPES,
    )


def _is_dict_comprehension(node: ast.AST) -> bool:
    """
    True for a dict comprehension.
    """
    return isinstance(
        node,
        ast.DictComp,
    )


def _is_docstring_statement(node: ast.AST) -> bool:
    """
    True for an expression statement that is a string literal.
    """
    if not _is_expression_statement(node):
        return False

    return _is_string_expression(node.value)


def _is_documented_node(node: ast.AST) -> bool:
    """
    True for nodes that may carry a docstring.
    """
    return isinstance(
        node,
        DOCUMENTED_NODE_TYPES,
    )


def _is_exclusive_branch_statement(node: ast.AST) -> bool:
    """
    True for statements whose child blocks are mutually exclusive paths (if/try/match).
    """
    return isinstance(
        node,
        EXCLUSIVE_BRANCH_TYPES,
    )


def _is_exit_statement(node: ast.AST) -> bool:
    """
    True for return, raise, or a bare yield / yield from statement.
    """
    is_return = _is_return(node)
    is_raise = _is_raise(node)

    if is_return or is_raise:
        return True

    if not _is_expression_statement(node):
        return False

    return _is_yield(node.value)


def _is_expression_statement(node: ast.AST) -> bool:
    """
    True for an expression used as a statement.
    """
    return isinstance(
        node,
        ast.Expr,
    )


def _is_foreign_from_import(
    node: ast.AST,
    local_packages: frozenset[str],
) -> bool:
    """
    True for an absolute 'from x import y' whose top-level package is not local.
    """
    if not _is_from_import(node):
        return False

    if node.level > 0:
        return False

    module = node.module or ''
    top_level = module.split('.')[0]

    if top_level == '__future__':
        return False

    return top_level not in local_packages


def _is_from_import(node: ast.AST) -> bool:
    """
    True for a 'from ... import ...' statement.
    """
    return isinstance(
        node,
        ast.ImportFrom,
    )


def _is_function_definition(node: ast.AST) -> bool:
    """
    True for a sync or async function definition.
    """
    return isinstance(
        node,
        FUNCTION_DEFINITION_TYPES,
    )


def _is_future_import(node: ast.AST) -> bool:
    """
    True for 'from __future__ import ...'.
    """
    if not _is_from_import(node):
        return False

    return node.module == '__future__'


def _is_import_statement(node: ast.AST) -> bool:
    """
    True for either import statement form.
    """
    return isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    )


def _is_inside_subscript(
    node: ast.AST,
    parents: dict[int, ast.AST],
) -> bool:
    """
    True when the node is a subscript slice or a list/tuple nested inside one (type parameters).
    """
    node_id = id(node)
    parent = parents.get(node_id)

    if parent is None:
        return False

    if _is_subscript(parent):
        return True

    is_nested_literal = isinstance(
        parent,
        (
            ast.List,
            ast.Tuple,
        ),
    )

    if not is_nested_literal:
        return False

    return _is_inside_subscript(
        parent,
        parents,
    )


def _is_load_context(node: ast.AST) -> bool:
    """
    True when an expression node is read rather than assigned to.
    """
    return isinstance(
        node.ctx,
        ast.Load,
    )


def _is_missing_type_hints(
    function: ast.AST,
    method_ids: frozenset[int],
) -> bool:
    """
    True when any checked parameter or the return value lacks an annotation.
    """
    is_method = id(function) in method_ids
    decorators = _decorator_names(function)
    skips_first_parameter = is_method and 'staticmethod' not in decorators
    parameters = _all_parameters(function)
    checked_parameters = parameters[1:] if skips_first_parameter else parameters
    missing_parameter = any(
        parameter.annotation is None
        for parameter
        in checked_parameters
    )
    missing_return = function.returns is None

    return missing_parameter or missing_return


def _is_name(node: ast.AST) -> bool:
    """
    True for a bare name expression.
    """
    return isinstance(
        node,
        ast.Name,
    )


def _is_named_except_handler(node: ast.AST) -> bool:
    """
    True for 'except Error as name'.
    """
    if not isinstance(
        node,
        ast.ExceptHandler,
    ):
        return False

    return node.name is not None


def _is_out_of_order(
    previous: ast.AST,
    current: ast.AST,
    rank_function: typing.Callable[[ast.AST], int],
) -> bool:
    """
    True when 'current' belongs to an earlier block than 'previous', or breaks alphabetical order.
    """
    previous_rank = rank_function(previous)
    current_rank = rank_function(current)

    if current_rank < previous_rank:
        return True

    return current_rank == previous_rank and current.name < previous.name


def _is_package_or_module(path: pathlib.Path) -> bool:
    """
    True for a directory with __init__.py or a .py file.
    """
    if path.is_dir():
        init_file = path / '__init__.py'

        return init_file.exists()

    return path.suffix == '.py'


def _is_parameter(node: ast.AST) -> bool:
    """
    True for a function parameter node.
    """
    return isinstance(
        node,
        ast.arg,
    )


def _is_plain_assignment(node: ast.AST) -> bool:
    """
    True for 'a = b'.
    """
    return isinstance(
        node,
        ast.Assign,
    )


def _is_raise(node: ast.AST) -> bool:
    """
    True for a raise statement.
    """
    return isinstance(
        node,
        ast.Raise,
    )


def _is_return(node: ast.AST) -> bool:
    """
    True for a return statement.
    """
    return isinstance(
        node,
        ast.Return,
    )


def _is_short_name(name: str) -> bool:
    """
    True for names below the minimum length, except the '_' placeholder.
    """
    if name == '_':
        return False

    return len(name) < MINIMUM_NAME_LENGTH


def _is_single_target_assignment(node: ast.AST) -> bool:
    """
    True for annotated or augmented assignments.
    """
    return isinstance(
        node,
        (
            ast.AnnAssign,
            ast.AugAssign,
        ),
    )


def _is_statement_list(value: object) -> bool:
    """
    True for a non-empty list of statements.
    """
    if not isinstance(
        value,
        list,
    ):
        return False

    if not value:
        return False

    return isinstance(
        value[0],
        ast.stmt,
    )


def _is_stored_name(node: ast.AST) -> bool:
    """
    True for a name being assigned to.
    """
    if not _is_name(node):
        return False

    return isinstance(
        node.ctx,
        ast.Store,
    )


def _is_string_expression(node: ast.AST) -> bool:
    """
    True for a string literal or an f-string.
    """
    if isinstance(
        node,
        ast.JoinedStr,
    ):
        return True

    if not isinstance(
        node,
        ast.Constant,
    ):
        return False

    return isinstance(
        node.value,
        str,
    )


def _is_subscript(node: ast.AST | None) -> bool:
    """
    True for a subscript expression.
    """
    return isinstance(
        node,
        ast.Subscript,
    )


def _is_tuple(node: ast.AST) -> bool:
    """
    True for a tuple literal.
    """
    return isinstance(
        node,
        ast.Tuple,
    )


def _is_tuple_return(node: ast.AST) -> bool:
    """
    True for 'return a, b' or 'return (a, b)'.
    """
    if not _is_return(node):
        return False

    if node.value is None:
        return False

    return _is_tuple(node.value)


def _is_yield(node: ast.AST) -> bool:
    """
    True for a yield or yield from expression.
    """
    return isinstance(
        node,
        (
            ast.Yield,
            ast.YieldFrom,
        ),
    )


def _items_on_own_lines(
    opening_line: int,
    item_lines: list[int],
) -> bool:
    """
    True when no item sits on the opening line and no two items share a line.
    """
    all_below_opening = all(
        line > opening_line
        for line
        in item_lines
    )
    unique_lines = set(item_lines)
    unique_count = len(unique_lines)
    item_count = len(item_lines)

    return all_below_opening and unique_count == item_count


def _iter_function_definitions(tree: ast.AST) -> list[ast.AST]:
    """
    Every function definition in the tree, outermost first.
    """
    functions = [
        node
        for node
        in ast.walk(tree)
        if _is_function_definition(node)
    ]

    return functions


def _iter_statement_lists(tree: ast.AST) -> typing.Iterator[list[ast.stmt]]:
    """
    Every statement list anywhere in the tree.
    """
    for node in ast.walk(tree):
        yield from _direct_statement_lists(node)


def _list_bindings(statements: list[ast.stmt]) -> list[BoundName]:
    """
    Names bound by a statement list, in order, without entering nested scopes.
    """
    bound_names = [
        bound_name
        for statement
        in statements
        for bound_name
        in _statement_bindings(statement)
    ]

    return bound_names


def _method_node_ids(tree: ast.Module) -> frozenset[int]:
    """
    Ids of the function nodes that are direct members of a class body.
    """
    method_ids = {
        id(statement)
        for node
        in ast.walk(tree)
        if _is_class_definition(node)
        for statement
        in node.body
        if _is_function_definition(statement)
    }

    return frozenset(method_ids)


def _method_rank(function: ast.AST) -> int:
    """
    Block index of a method: abstract, __init__, properties (3 visibilities), methods (3 visibilities).
    """
    decorators = _decorator_names(function)
    name = function.name

    if 'abstractmethod' in decorators:
        return 0

    if name == '__init__':
        return 1

    visibility = _visibility(name)
    is_property = bool(decorators & PROPERTY_DECORATOR_NAMES)

    if is_property:
        return 2 + visibility

    return 5 + visibility


def _module_function_rank(function: ast.AST) -> int:
    """
    Block index of a module-level function: public first, then internal.
    """
    return _visibility(function.name)


def _multi_item_children(
    node: ast.AST,
    parents: dict[int, ast.AST],
) -> list[ast.AST]:
    """
    The comma-separated items of a construct covered by the one-item-per-line rule.
    """
    if _is_call(node):
        return node.args + node.keywords

    if _is_function_definition(node):
        return _all_parameters(node)

    if _is_from_import(node):
        return node.names

    if isinstance(
        node,
        ast.Dict,
    ):
        return _dict_items(node)

    if isinstance(
        node,
        ast.Set,
    ):
        return node.elts

    is_sequence_literal = isinstance(
        node,
        (
            ast.List,
            ast.Tuple,
        ),
    )

    if not is_sequence_literal:
        return []

    in_subscript = _is_inside_subscript(
        node,
        parents,
    )
    is_loaded = _is_load_context(node)
    is_excluded = in_subscript or not is_loaded

    if is_excluded:
        return []

    return node.elts


def _name_nodes(target: ast.AST) -> list[ast.Name]:
    """
    Plain name nodes inside an assignment target, flattening tuple/list unpacking.
    """
    if _is_name(target):
        return [target]

    if isinstance(
        target,
        (
            ast.List,
            ast.Tuple,
        ),
    ):
        nested = [
            name_node
            for element
            in target.elts
            for name_node
            in _name_nodes(element)
        ]

        return nested

    return []


def _name_seen_before(
    bound_names: list[BoundName],
    index: int,
) -> bool:
    """
    True when the name at 'index' was already bound earlier in the same scope.
    """
    earlier_names = {
        bound_name.name
        for bound_name
        in bound_names[:index]
    }

    return bound_names[index].name in earlier_names


def _order_violations(
    functions: list[ast.AST],
    rank_function: typing.Callable[[ast.AST], int],
) -> list[Violation]:
    """
    One violation per function that breaks block or alphabetical order relative to its predecessor.
    """
    consecutive_pairs = zip(
        functions,
        functions[1:],
    )
    violations = [
        _violation(
            'BLOOM009',
            current.lineno,
        )
        for previous, current
        in consecutive_pairs
        if _is_out_of_order(
            previous,
            current,
            rank_function,
        )
    ]

    return violations


def _python_files_under(path: pathlib.Path) -> list[pathlib.Path]:
    """
    All *.py files under a directory, or the path itself when it is a file.
    """
    if path.is_dir():
        found = path.rglob('*.py')

        return sorted(found)

    return [path]


def _reassignment_violations(scope: ast.AST) -> list[Violation]:
    """
    Violations for names assigned more than once within one scope.
    """
    bound_names = _list_bindings(scope.body)
    violations = [
        _violation(
            'BLOOM006',
            bound_name.line,
        )
        for index, bound_name
        in enumerate(bound_names)
        if _name_seen_before(
            bound_names,
            index,
        )
    ]

    return violations


def _statement_bindings(statement: ast.stmt) -> list[BoundName]:
    """
    Names bound by one statement and its child blocks; exclusive branches count once per name.
    """
    direct = _assignment_targets(statement)

    if isinstance(
        statement,
        SCOPE_NODE_TYPES,
    ):
        return direct

    child_lists = list(
        _direct_statement_lists(statement)
    )
    nested = [
        bound_name
        for statements
        in child_lists
        for bound_name
        in _list_bindings(statements)
    ]

    if _is_exclusive_branch_statement(statement):
        return direct + _dedupe_by_name(nested)

    return direct + nested


def _statement_list_spacing_violations(
    statements: list[ast.stmt],
    lines: tuple[str, ...],
) -> list[Violation]:
    """
    Exit-statement spacing violations within one statement list.
    """
    exit_violations = [
        violation
        for index, statement
        in enumerate(statements)
        for violation
        in _exit_spacing_violations(
            statements,
            index,
            lines,
        )
    ]
    block_violations = [
        violation
        for index, statement
        in enumerate(statements)
        for violation
        in _block_spacing_violations(
            statements,
            index,
            lines,
        )
    ]

    return exit_violations + block_violations


def _violation(
    code: str,
    line: int,
) -> Violation:
    """
    Build a violation from its code and line, looking up the canonical message.
    """
    return Violation(
        line=line,
        code=code,
        message=RULE_MESSAGES[code],
    )


def _visibility(name: str) -> int:
    """
    0 for public (dunders included), 1 for protected (_x), 2 for private (__x).
    """
    has_dunder_prefix = name.startswith('__')
    has_dunder_suffix = name.endswith('__')
    is_dunder = has_dunder_prefix and has_dunder_suffix

    if is_dunder:
        return 0

    if name.startswith('__'):
        return 2

    if name.startswith('_'):
        return 1

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
