# file: src/repl.py

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

def run_repl():
    """Starts the Roadman interactive REPL."""
    interpreter = Interpreter()
    print("Roadman REPL v0.1")
    print("Type 'exit()' or press Ctrl+C to exit.")

    while True:
        try:
            line = input("> ")
            if line.strip().lower() == "exit()":
                break

            # For the REPL, we can process one line at a time
            if not line:
                continue

            lexer = Lexer(line)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            program = parser.parse()

            # The 'interpret' method handles execution and potential errors
            interpreter.interpret(program)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            # Catching any other unexpected errors during development
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_repl()
