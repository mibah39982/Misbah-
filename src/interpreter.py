# file: src/interpreter.py

from typing import Any, List, Callable
import time
import src.ast as ast
from src.lexer import Token

# --- Return Exception ---
class Return(Exception):
    """Exception used to unwind the stack for return statements."""
    def __init__(self, value: Any):
        self.value = value

# --- Callables ---
class RoadmanCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        raise NotImplementedError

class RoadmanFunction(RoadmanCallable):
    def __init__(self, declaration: ast.FunctionDeclaration, closure: 'Environment'):
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.value, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body.statements, environment)
        except Return as r:
            return r.value

        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.value}>"

# --- Environment ---
class Environment:
    """Manages variable scopes."""
    def __init__(self, enclosing: 'Environment' = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: Token, value: Any):
        if name.value in self.values:
            self.values[name.value] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name.value}'.")

    def get(self, name: Token) -> Any:
        if name.value in self.values:
            return self.values[name.value]
        if self.enclosing:
            return self.enclosing.get(name)
        raise RuntimeError(f"Undefined variable '{name.value}'.")

class Interpreter(ast.NodeVisitor):
    """
    The Roadman Interpreter. Executes the AST.
    Uses the visitor pattern.
    """
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        # Define native functions
        class Say(RoadmanCallable):
            def arity(self): return 1
            def call(self, interpreter, arguments): print(arguments[0])

        self.globals.define("say", Say())

    def interpret(self, program: ast.Program):
        try:
            for statement in program.statements:
                self._execute(statement)
        except RuntimeError as e:
            print(e)

    def _execute(self, stmt: ast.Statement):
        stmt.accept(self)

    def _evaluate(self, expr: ast.Expression) -> Any:
        return expr.accept(self)

    def visit_Program(self, node: ast.Program):
        for stmt in node.statements:
            self._execute(stmt)

    def visit_ExpressionStatement(self, stmt: ast.ExpressionStatement):
        self._evaluate(stmt.expression)

    def visit_VarDeclaration(self, stmt: ast.VarDeclaration):
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)
        self.environment.define(stmt.name.value, value)

    def visit_Block(self, stmt: ast.Block):
        self._execute_block(stmt.statements, Environment(self.environment))

    def visit_FunctionDeclaration(self, stmt: ast.FunctionDeclaration):
        function = RoadmanFunction(stmt, self.environment)
        self.environment.define(stmt.name.value, function)

    def visit_ReturnStatement(self, stmt: ast.ReturnStatement):
        value = None
        if stmt.value:
            value = self._evaluate(stmt.value)
        raise Return(value)

    def _execute_block(self, statements: List[ast.Statement], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous

    def visit_IfStatement(self, stmt: ast.IfStatement):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def visit_WhileLoop(self, stmt: ast.WhileLoop):
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def visit_Variable(self, expr: ast.Variable) -> Any:
        return self.environment.get(expr.token)

    def visit_Assignment(self, expr: ast.Assignment) -> Any:
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_Literal(self, expr: ast.Literal) -> Any:
        return expr.value

    def visit_Grouping(self, expr: ast.Grouping) -> Any:
        return self._evaluate(expr.expression)

    def visit_UnaryOp(self, expr: ast.UnaryOp) -> Any:
        right = self._evaluate(expr.right)
        op_type = expr.operator.type
        if op_type == "MINUS":
            self._check_number_operand(expr.operator, right)
            return -float(right)
        if op_type == "BANG":
            return not self._is_truthy(right)
        return None # Should be unreachable

    def visit_UnaryOp(self, expr: ast.UnaryOp) -> Any:
        right = self._evaluate(expr.right)
        op_type = expr.operator.type
        if op_type == "MINUS":
            self._check_number_operand(expr.operator, right)
            return -float(right)
        if op_type == "BANG":
            return not self._is_truthy(right)
        return None # Should be unreachable

    def visit_FunctionCall(self, expr: ast.FunctionCall) -> Any:
        callee = self._evaluate(expr.callee)

        arguments = []
        for arg in expr.arguments:
            arguments.append(self._evaluate(arg))

        if not isinstance(callee, RoadmanCallable):
            raise RuntimeError("Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_ListLiteral(self, expr: ast.ListLiteral) -> Any:
        return [self._evaluate(elem) for elem in expr.elements]

    def visit_BinaryOp(self, expr: ast.BinaryOp) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        op_type = expr.operator.type

        # Arithmetic
        if op_type == "MINUS":
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if op_type == "PLUS":
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise RuntimeError(f"{expr.operator.value}: Operands must be two numbers or two strings.")
        if op_type == "SLASH":
            self._check_number_operands(expr.operator, left, right)
            if right == 0: raise RuntimeError("Division by zero.")
            return float(left) / float(right)
        if op_type == "STAR":
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        if op_type == "PERCENT":
            self._check_number_operands(expr.operator, left, right)
            return float(left) % float(right)

        # Comparison
        if op_type == "GREATER": return left > right
        if op_type == "GREATER_EQ": return left >= right
        if op_type == "LESS": return left < right
        if op_type == "LESS_EQ": return left <= right
        if op_type == "BANG_EQ": return not self._is_equal(left, right)
        if op_type == "EQ_EQ": return self._is_equal(left, right)

        return None # Should be unreachable

    def _is_truthy(self, obj: Any) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return obj
        if isinstance(obj, float): return obj != 0
        if isinstance(obj, str): return len(obj) > 0
        return True

    def _is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def _check_number_operand(self, op: Token, operand: Any):
        if isinstance(operand, float): return
        raise RuntimeError(f"{op.value}: Operand must be a number.")

    def _check_number_operands(self, op: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"{op.value}: Operands must be numbers.")
