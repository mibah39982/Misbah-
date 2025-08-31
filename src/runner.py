# file: src/runner.py

import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

def run_file(filepath: str):
    """Reads a Roadman file and executes it."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        sys.exit(1)

    interpreter = Interpreter()
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    program = parser.parse()

    # Check for parse errors before interpreting
    # A more robust implementation would have the parser return errors
    # instead of printing them. For now, this is a basic check.
    if any(isinstance(e, str) and e.startswith("[line") for e in program.statements):
         print("Execution halted due to parsing errors.")
         sys.exit(1)

    interpreter.interpret(program)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.runner <filepath>")
        sys.exit(1)

    run_file(sys.argv[1])
