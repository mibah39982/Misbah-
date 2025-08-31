# file: src/transpiler.py

import src.ast as ast

class Transpiler(ast.NodeVisitor):
    """
    Transpiles a Roadman AST into JavaScript code.
    """
    def transpile(self, program: ast.Program) -> str:
        return self.visit(program)

    def visit_Program(self, node: ast.Program) -> str:
        return "\n".join(self.visit(stmt) for stmt in node.statements)

    def visit_VarDeclaration(self, node: ast.VarDeclaration) -> str:
        keyword = "const" if node.constant else "let"
        if node.initializer:
            return f"{keyword} {node.name.value} = {self.visit(node.initializer)};"
        return f"{keyword} {node.name.value};"

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration) -> str:
        params = ", ".join(p.value for p in node.params)
        body = self.visit(node.body)
        return f"function {node.name.value}({params}) {body}"

    def visit_IfStatement(self, node: ast.IfStatement) -> str:
        condition = self.visit(node.condition)
        then_branch = self.visit(node.then_branch)
        if node.else_branch:
            else_branch = self.visit(node.else_branch)
            return f"if ({condition}) {then_branch} else {else_branch}"
        return f"if ({condition}) {then_branch}"

    def visit_WhileLoop(self, node: ast.WhileLoop) -> str:
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        return f"while ({condition}) {body}"

    def visit_ReturnStatement(self, node: ast.ReturnStatement) -> str:
        if node.value:
            return f"return {self.visit(node.value)};"
        return "return;"

    def visit_BreakStatement(self, node: ast.BreakStatement) -> str:
        return "break;"

    def visit_Block(self, node: ast.Block) -> str:
        statements = "\n  ".join(self.visit(stmt) for stmt in node.statements)
        return f"{{\n  {statements}\n}}"

    def visit_ExpressionStatement(self, node: ast.ExpressionStatement) -> str:
        return f"{self.visit(node.expression)};"

    # --- Expressions ---

    def visit_Assignment(self, node: ast.Assignment) -> str:
        value = self.visit(node.value)
        return f"{node.name.value} = {value}"

    def visit_BinaryOp(self, node: ast.BinaryOp) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_map = {"AND": "&&", "OR": "||"}
        op = op_map.get(node.operator.type, node.operator.value)
        return f"({left} {op} {right})"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        right = self.visit(node.right)
        return f"{node.operator.value}{right}"

    def visit_FunctionCall(self, node: ast.FunctionCall) -> str:
        callee_name = self.visit(node.callee)
        # Handle Roadman built-ins
        if callee_name == "say":
            callee_name = "console.log"

        args = ", ".join(self.visit(arg) for arg in node.arguments)
        return f"{callee_name}({args})"

    def visit_Variable(self, node: ast.Variable) -> str:
        return node.token.value

    def visit_Literal(self, node: ast.Literal) -> str:
        if isinstance(node.value, str):
            return f'"{node.value}"'
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        return str(node.value)

    def visit_ListLiteral(self, node: ast.ListLiteral) -> str:
        elements = ", ".join(self.visit(elem) for elem in node.elements)
        return f"[{elements}]"

    def visit_Grouping(self, node: ast.Grouping) -> str:
        return f"({self.visit(node.expression)})"

    def generic_visit(self, node, *args, **kwargs):
        raise Exception(f"No visit_{type(node).__name__} method")
