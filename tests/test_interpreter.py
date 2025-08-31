# file: tests/test_interpreter.py

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

def run_code(source: str, interpreter: Interpreter):
    """Helper to run a block of code through the pipeline."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter.interpret(program)

class TestInterpreter:

    def test_arithmetic(self, capsys):
        """Tests basic arithmetic operations."""
        source = "say(10 * (4 - 2) + 5 / 2);"  # Expected: 10 * 2 + 2.5 = 22.5
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip() == "22.5"

    def test_variables_and_scope(self, capsys):
        """Tests variable declaration, assignment, and scoping."""
        source = """
        gimme a = 10;
        {
            gimme a = 20;
            say(a); // Should say 20
        }
        say(a); // Should say 10
        """
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip().split('\n') == ["20.0", "10.0"]

    def test_if_statement(self, capsys):
        """Tests innit/elseway logic."""
        source = """
        gimme x = 10;
        innit (x > 5) {
            say("greater");
        } elseway {
            say("smaller");
        }
        innit (x < 5) {
            say("this should not appear");
        } elseway {
            say("smaller");
        }
        """
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip().split('\n') == ["greater", "smaller"]

    def test_while_loop(self, capsys):
        """Tests the loopz statement."""
        source = """
        gimme i = 0;
        loopz (i < 3) {
            say(i);
            i = i + 1;
        }
        """
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip().split('\n') == ["0.0", "1.0", "2.0"]

    def test_factorial_recursion(self, capsys):
        """Tests recursive function calls by implementing factorial."""
        source = """
        fam factorial(n) {
            innit (n < 2) {
                returnz 1;
            }
            returnz n * factorial(n - 1);
        }
        say(factorial(5)); // 120
        """
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip() == "120.0"

    def test_closure(self, capsys):
        """Tests that functions form closures."""
        source = """
        fam makeCounter() {
            gimme i = 0;
            fam count() {
                i = i + 1;
                returnz i;
            }
            returnz count;
        }

        gimme counter = makeCounter();
        say(counter()); // 1
        say(counter()); // 2
        """
        interpreter = Interpreter()
        run_code(source, interpreter)
        captured = capsys.readouterr()
        assert captured.out.strip().split('\n') == ["1.0", "2.0"]

    def test_list_literal(self, capsys):
        """Tests creation of a list literal."""
        source = 'say([1, "two", true]);'
        interpreter = Interpreter()
        # The default say function will use Python's print, which calls repr on lists
        # So we expect the Python representation of the list.
        run_code(source, interpreter)
        captured = capsys.readouterr()
        # Note: The interpreter creates floats for all numbers.
        assert captured.out.strip() == "[1.0, 'two', True]"
