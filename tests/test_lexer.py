# file: tests/test_lexer.py

import pytest
from src.lexer import Lexer, Token

class TestLexer:
    def test_single_tokens(self):
        """Tests tokenization of individual symbols and operators."""
        source = "+ - * / % = == != < <= > >= ( ) { } [ ] , ; : && || !"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected_types = [
            "PLUS", "MINUS", "STAR", "SLASH", "PERCENT", "EQ", "EQ_EQ", "BANG_EQ",
            "LESS", "LESS_EQ", "GREATER", "GREATER_EQ", "LPAREN", "RPAREN",
            "LBRACE", "RBRACE", "LBRACKET", "RBRACKET", "COMMA", "SEMICOLON",
            "COLON", "AND", "OR", "BANG", "EOF"
        ]
        assert [t.type for t in tokens] == expected_types

    def test_keywords(self):
        """Tests that all keywords are correctly identified."""
        # A subset of keywords to test
        source = "innit elseway loopz fam returnz gimme conste"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected_types = ["INNIT", "ELSEWAY", "LOOPZ", "FAM", "RETURNZ", "GIMME", "CONSTE", "EOF"]
        assert [t.type for t in tokens] == expected_types

    def test_variable_declaration(self):
        """Tests a simple variable declaration statement."""
        source = 'gimme myVar = 10.5;'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected = [
            Token("GIMME", "gimme", 1, 1),
            Token("IDENTIFIER", "myVar", 1, 7),
            Token("EQ", "=", 1, 13),
            Token("DIGIT", "10.5", 1, 15),
            Token("SEMICOLON", ";", 1, 19),
            Token("EOF", "", 1, 20)
        ]
        assert tokens == expected

    def test_string_literal(self):
        """Tests tokenization of a string literal."""
        source = '"hello, world!"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected = [
            Token("WORD", "hello, world!", 1, 1),
            Token("EOF", "", 1, 16)
        ]
        assert tokens == expected

    def test_comments(self):
        """Tests that comments are properly ignored."""
        source = """
        // This is a comment.
        gimme x = 5; /* This is a
                        multi-line comment */
        // Another one.
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected = [
            Token("GIMME", "gimme", 3, 9),
            Token("IDENTIFIER", "x", 3, 15),
            Token("EQ", "=", 3, 17),
            Token("DIGIT", "5", 3, 19),
            Token("SEMICOLON", ";", 3, 20),
            Token("EOF", "", 6, 9)
        ]
        # We filter out whitespace tokens for this comparison if any were to exist
        assert [t for t in tokens if t.type != "WHITESPACE"] == expected

    def test_function_declaration(self):
        """Tests a full function declaration."""
        source = 'fam add(a, b) {\n  returnz a + b;\n}'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        expected_types = [
            "FAM", "IDENTIFIER", "LPAREN", "IDENTIFIER", "COMMA", "IDENTIFIER", "RPAREN",
            "LBRACE", "RETURNZ", "IDENTIFIER", "PLUS", "IDENTIFIER", "SEMICOLON",
            "RBRACE", "EOF"
        ]
        assert [t.type for t in tokens] == expected_types
        assert tokens[8].line == 2
        assert tokens[8].col == 3

    def test_line_and_col_tracking(self):
        """Ensures line and column numbers are tracked correctly."""
        source = 'gimme a = 1;\ngimme b = 2;'
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # gimme on line 2
        assert tokens[5].type == "GIMME"
        assert tokens[5].line == 2
        assert tokens[5].col == 1

        # b on line 2
        assert tokens[6].type == "IDENTIFIER"
        assert tokens[6].value == "b"
        assert tokens[6].line == 2
        assert tokens[6].col == 7

    def test_complex_snippet(self):
        """Tests a more complex piece of code with mixed constructs."""
        source = """
        fam factorial(n) {
            innit (n < 2) {
                returnz 1;
            } elseway {
                returnz n * factorial(n - 1);
            }
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) > 20 # Just a basic check for a stream of tokens
        assert tokens[0].type == "FAM"
        assert tokens[-1].type == "EOF"
        assert tokens[6].type == "INNIT"
        assert tokens[17].type == "ELSEWAY"
