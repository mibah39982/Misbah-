# file: src/parser.py

from typing import List, Optional
from src.lexer import Token
import src.ast as ast

class ParseError(Exception):
    pass

class Parser:
    """
    The Parser for the Roadman language. It constructs an AST from a token stream.
    Implements a recursive descent parser.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ast.Program:
        """
        Parses the token stream and returns the Program AST node.
        Raises ParseError on failure.
        """
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return ast.Program(statements=statements)

    # --- Statement Parsers ---

    def _declaration(self) -> ast.Statement:
        if self._match("CONSTE"):
            return self._var_declaration(constant=True)
        if self._match("GIMME"):
            return self._var_declaration(constant=False)
        if self._match("FAM"):
            return self._function_declaration()
        return self._statement()

    def _var_declaration(self, constant: bool) -> ast.Statement:
        name = self._consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self._match("EQ"):
            initializer = self._expression()
        self._consume("SEMICOLON", "Expect ';' after variable declaration.")
        return ast.VarDeclaration(name=name, initializer=initializer, constant=constant)

    def _function_declaration(self) -> ast.Statement:
        name = self._consume("IDENTIFIER", "Expect function name.")
        self._consume("LPAREN", "Expect '(' after function name.")
        parameters = []
        if not self._check("RPAREN"):
            parameters.append(self._consume("IDENTIFIER", "Expect parameter name."))
            while self._match("COMMA"):
                parameters.append(self._consume("IDENTIFIER", "Expect parameter name."))
        self._consume("RPAREN", "Expect ')' after parameters.")
        self._consume("LBRACE", "Expect '{' before function body.")
        body = self._block()
        return ast.FunctionDeclaration(name=name, params=parameters, body=ast.Block(body))

    def _statement(self) -> ast.Statement:
        if self._match("INNIT"): return self._if_statement()
        if self._match("LOOPZ"): return self._while_statement()
        if self._match("RETURNZ"): return self._return_statement()
        if self._match("STOPIT"): return self._break_statement()
        if self._match("LBRACE"): return ast.Block(self._block())
        return self._expression_statement()

    def _if_statement(self) -> ast.Statement:
        self._consume("LPAREN", "Expect '(' after 'innit'.")
        condition = self._expression()
        self._consume("RPAREN", "Expect ')' after if condition.")
        then_branch = self._statement()
        else_branch = None
        if self._match("ELSEWAY"):
            else_branch = self._statement()
        return ast.IfStatement(condition, then_branch, else_branch)

    def _while_statement(self) -> ast.Statement:
        self._consume("LPAREN", "Expect '(' after 'loopz'.")
        condition = self._expression()
        self._consume("RPAREN", "Expect ')' after loop condition.")
        body = self._statement()
        return ast.WhileLoop(condition, body)

    def _return_statement(self) -> ast.Statement:
        keyword = self._previous()
        value = None
        if not self._check("SEMICOLON"):
            value = self._expression()
        self._consume("SEMICOLON", "Expect ';' after return value.")
        return ast.ReturnStatement(keyword, value)

    def _break_statement(self) -> ast.Statement:
        keyword = self._previous()
        self._consume("SEMICOLON", "Expect ';' after 'stopit'.")
        return ast.BreakStatement(keyword)

    def _block(self) -> List[ast.Statement]:
        statements = []
        while not self._check("RBRACE") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume("RBRACE", "Expect '}' after block.")
        return statements

    def _expression_statement(self) -> ast.Statement:
        expr = self._expression()
        self._consume("SEMICOLON", "Expect ';' after expression.")
        return ast.ExpressionStatement(expr)

    # --- Expression Parsers (by precedence) ---

    def _expression(self) -> ast.Expression:
        return self._assignment()

    def _assignment(self) -> ast.Expression:
        expr = self._logical_or()
        if self._match("EQ"):
            equals = self._previous()
            value = self._assignment()
            if isinstance(expr, ast.Variable):
                return ast.Assignment(name=expr.token, value=value)
            self._error(equals, "Invalid assignment target.")
        return expr

    def _logical_or(self) -> ast.Expression:
        expr = self._logical_and()
        while self._match("OR"):
            operator = self._previous()
            right = self._logical_and()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _logical_and(self) -> ast.Expression:
        expr = self._equality()
        while self._match("AND"):
            operator = self._previous()
            right = self._equality()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _equality(self) -> ast.Expression:
        expr = self._comparison()
        while self._match("BANG_EQ", "EQ_EQ"):
            operator = self._previous()
            right = self._comparison()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _comparison(self) -> ast.Expression:
        expr = self._term()
        while self._match("GREATER", "GREATER_EQ", "LESS", "LESS_EQ"):
            operator = self._previous()
            right = self._term()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _term(self) -> ast.Expression:
        expr = self._factor()
        while self._match("MINUS", "PLUS"):
            operator = self._previous()
            right = self._factor()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _factor(self) -> ast.Expression:
        expr = self._unary()
        while self._match("SLASH", "STAR", "PERCENT"):
            operator = self._previous()
            right = self._unary()
            expr = ast.BinaryOp(expr, operator, right)
        return expr

    def _unary(self) -> ast.Expression:
        if self._match("BANG", "MINUS"):
            operator = self._previous()
            right = self._unary()
            return ast.UnaryOp(operator, right)
        return self._call()

    def _call(self) -> ast.Expression:
        expr = self._primary()
        while True:
            if self._match("LPAREN"):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _finish_call(self, callee: ast.Expression) -> ast.Expression:
        arguments = []
        if not self._check("RPAREN"):
            arguments.append(self._expression())
            while self._match("COMMA"):
                # Simplified: no arbitrary expression arguments for now
                arguments.append(self._expression())
        paren = self._consume("RPAREN", "Expect ')' after arguments.")
        return ast.FunctionCall(callee, paren, arguments)

    def _primary(self) -> ast.Expression:
        if self._match("FALSE"): return ast.Literal(self._previous(), False)
        if self._match("TRUE"): return ast.Literal(self._previous(), True)
        # In Roadman, keywords are used for types, so we might need a different token for 'null'
        # For now, let's assume no null keyword.

        if self._match("DIGIT"):
            return ast.Literal(self._previous(), float(self._previous().value))
        if self._match("WORD"):
            return ast.Literal(self._previous(), self._previous().value)

        if self._match("IDENTIFIER"):
            return ast.Variable(self._previous())

        if self._match("LPAREN"):
            expr = self._expression()
            self._consume("RPAREN", "Expect ')' after expression.")
            return ast.Grouping(expr)

        if self._match("LBRACKET"):
            return self._list_literal()

        raise self._error(self._peek(), "Expect expression.")

    def _list_literal(self) -> ast.Expression:
        elements = []
        if not self._check("RBRACKET"):
            elements.append(self._expression())
            while self._match("COMMA"):
                elements.append(self._expression())
        self._consume("RBRACKET", "Expect ']' after list elements.")
        return ast.ListLiteral(elements)

    # --- Helper Methods ---

    def _match(self, *types: str) -> bool:
        for t_type in types:
            if self._check(t_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: str, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, token_type: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == "EOF"

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, token: Token, message: str) -> ParseError:
        error_msg = f"[line {token.line}:{token.col}] Error"
        if token.type == "EOF":
            error_msg += " at end"
        else:
            error_msg += f" at '{token.value}'"
        error_msg += f": {message}"
        return ParseError(error_msg)

    def _synchronize(self):
        self._advance()
        while not self._is_at_end():
            if self._previous().type == "SEMICOLON":
                return

            # These tokens often start a new statement
            if self._peek().type in ["FAM", "INNIT", "LOOPZ", "RETURNZ", "GIMME", "CONSTE"]:
                return

            self._advance()
