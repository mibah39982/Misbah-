# file: tests/test_parser.py

import pytest
from src.lexer import Lexer
from src.parser import Parser, ParseError
import src.ast as ast

def _parse_source(source: str) -> ast.Program:
    """Helper function to lex and parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

class TestParser:
    def test_variable_declaration(self):
        """Tests parsing of variable declarations."""
        source = "gimme x = 10; conste y = true;"
        program = _parse_source(source)

        assert len(program.statements) == 2

        # Test 'gimme'
        decl1 = program.statements[0]
        assert isinstance(decl1, ast.VarDeclaration)
        assert decl1.name.value == "x"
        assert not decl1.constant
        assert isinstance(decl1.initializer, ast.Literal)
        assert decl1.initializer.value == 10.0

        # Test 'conste'
        decl2 = program.statements[1]
        assert isinstance(decl2, ast.VarDeclaration)
        assert decl2.name.value == "y"
        assert decl2.constant
        assert isinstance(decl2.initializer, ast.Literal)
        assert decl2.initializer.value is True

    def test_expression_statement(self):
        """Tests parsing of a simple expression with operator precedence."""
        source = "1 + 2 * 3;"
        program = _parse_source(source)
        stmt = program.statements[0]

        assert isinstance(stmt, ast.ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, ast.BinaryOp)
        assert expr.operator.type == "PLUS"

        # Left side should be the literal 1
        assert isinstance(expr.left, ast.Literal)
        assert expr.left.value == 1.0

        # Right side should be the multiplication
        right = expr.right
        assert isinstance(right, ast.BinaryOp)
        assert right.operator.type == "STAR"
        assert right.left.value == 2.0
        assert right.right.value == 3.0

    def test_if_statement(self):
        """Tests parsing of an if-else statement."""
        source = """
        innit (x > 5) {
            say("big");
        } elseway {
            say("small");
        }
        """
        program = _parse_source(source)
        stmt = program.statements[0]

        assert isinstance(stmt, ast.IfStatement)
        assert isinstance(stmt.condition, ast.BinaryOp)
        assert stmt.condition.operator.type == "GREATER"

        assert isinstance(stmt.then_branch, ast.Block)
        assert len(stmt.then_branch.statements) == 1

        assert isinstance(stmt.else_branch, ast.Block)
        assert len(stmt.else_branch.statements) == 1

    def test_function_declaration(self):
        """Tests parsing of a function declaration."""
        source = "fam add(a, b) { returnz a + b; }"
        program = _parse_source(source)
        stmt = program.statements[0]

        assert isinstance(stmt, ast.FunctionDeclaration)
        assert stmt.name.value == "add"
        assert len(stmt.params) == 2
        assert stmt.params[0].value == "a"
        assert stmt.params[1].value == "b"

        assert isinstance(stmt.body, ast.Block)
        assert len(stmt.body.statements) == 1
        return_stmt = stmt.body.statements[0]
        assert isinstance(return_stmt, ast.ReturnStatement)

    def test_function_call(self):
        """Tests parsing of a function call."""
        source = "myFunc(1, 2);"
        program = _parse_source(source)
        stmt = program.statements[0]

        assert isinstance(stmt, ast.ExpressionStatement)
        call = stmt.expression
        assert isinstance(call, ast.FunctionCall)
        assert isinstance(call.callee, ast.Variable)
        assert call.callee.token.value == "myFunc"
        assert len(call.arguments) == 2

    def test_parse_error(self):
        """Tests that the parser raises an error on invalid syntax."""
        source = "gimme x = ;"
        with pytest.raises(ParseError, match=r"Expect expression."):
            # We have to manually call here to catch the exception
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            # The print in the parser will still fire, this is expected for now.
            Parser(tokens).parse()

    def test_list_literal(self):
        """Tests parsing of a list literal."""
        source = "[1, \"two\", true];"
        program = _parse_source(source)
        stmt = program.statements[0]

        assert isinstance(stmt, ast.ExpressionStatement)
        list_literal = stmt.expression
        assert isinstance(list_literal, ast.ListLiteral)
        assert len(list_literal.elements) == 3
        assert isinstance(list_literal.elements[0], ast.Literal)
        assert list_literal.elements[0].value == 1.0
        assert isinstance(list_literal.elements[1], ast.Literal)
        assert list_literal.elements[1].value == "two"
        assert isinstance(list_literal.elements[2], ast.Literal)
        assert list_literal.elements[2].value is True
