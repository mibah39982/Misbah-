# file: src/ast.py

from dataclasses import dataclass
from typing import List, Optional, Any
from src.lexer import Token

# Base classes
class NodeVisitor:
    """Base class for a visitor of AST nodes."""
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

class Node:
    """Base class for all AST nodes."""
    def accept(self, visitor):
        return visitor.visit(self)

class Statement(Node):
    """Base class for all statement nodes."""
    pass

class Expression(Node):
    """Base class for all expression nodes."""
    pass

# Expression Nodes
@dataclass
class Literal(Expression):
    token: Token
    value: Any

@dataclass
class Variable(Expression):
    token: Token  # The identifier token

@dataclass
class UnaryOp(Expression):
    operator: Token
    right: Expression

@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class Grouping(Expression):
    expression: Expression

@dataclass
class Assignment(Expression):
    name: Token
    value: Expression

@dataclass
class FunctionCall(Expression):
    callee: Expression
    paren: Token # for error reporting
    arguments: List[Expression]

@dataclass
class ListLiteral(Expression):
    elements: List[Expression]

# Statement Nodes
@dataclass
class Program(Node):
    statements: List[Statement]

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class Block(Statement):
    statements: List[Statement]

@dataclass
class VarDeclaration(Statement):
    name: Token
    initializer: Optional[Expression]
    constant: bool

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement]

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: Statement

@dataclass
class BreakStatement(Statement):
    keyword: Token

@dataclass
class FunctionDeclaration(Statement):
    name: Token
    params: List[Token]
    body: Block

@dataclass
class ReturnStatement(Statement):
    keyword: Token
    value: Optional[Expression]
