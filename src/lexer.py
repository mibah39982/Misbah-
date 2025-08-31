# file: src/lexer.py

import json
from pathlib import Path
from typing import List, NamedTuple, Dict, Optional

class Token(NamedTuple):
    """Represents a token in the Roadman language."""
    type: str
    value: str
    line: int
    col: int

class Lexer:
    """
    The Lexer for the Roadman language.
    Splits the source code into a stream of tokens.
    """

    def __init__(self, source_code: str):
        self.source = source_code
        self.tokens: List[Token] = []
        self.current = 0
        self.line = 1
        self.col = 1
        self.keywords: Dict[str, str] = self._load_keywords()

    def _load_keywords(self) -> Dict[str, str]:
        """Returns a dictionary of language keywords."""
        # Keywords are constructs that change control flow or define structure.
        # Built-in functions like 'say' are treated as identifiers and
        # resolved in the interpreter's environment.
        keywords = {
            "innit": "INNIT",
            "elseway": "ELSEWAY",
            "loopz": "LOOPZ",
            "stopit": "STOPIT",
            "switchup": "SWITCHUP",
            "casez": "CASEZ",
            "defend": "DEFEND",
            "conste": "CONSTE",
            "gimme": "GIMME",
            "fam": "FAM",
            "returnz": "RETURNZ",
            "true": "TRUE",
            "false": "FALSE",
            # Types
            "digit": "TYPE_DIGIT",
            "word": "TYPE_WORD",
            "boola": "TYPE_BOOLA",
            "listz": "TYPE_LISTZ",
            "mapz": "TYPE_MAPZ",
        }
        return keywords

    def tokenize(self) -> List[Token]:
        """Scans the source code and returns a list of tokens."""
        while not self._is_at_end():
            self._scan_token()
        self.tokens.append(Token("EOF", "", self.line, self.col))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.col += 1
        return char

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _add_token(self, token_type: str, value: Optional[str] = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, value if value is not None else text, self.line, self.start_col))

    def _scan_token(self):
        self.start = self.current
        self.start_col = self.col
        char = self._advance()

        if char in ' \r\t':
            pass  # Ignore whitespace
        elif char == '\n':
            self.line += 1
            self.col = 1
        elif char == '/':
            if self._peek() == '/':
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._peek() == '*':
                self._advance() # consume '*'
                while not (self._peek() == '*' and self._peek_next() == '/') and not self._is_at_end():
                    if self._peek() == '\n':
                        self.line += 1
                        self.col = 1
                    self._advance()
                if not self._is_at_end():
                    self._advance() # consume '*'
                    self._advance() # consume '/'
            else:
                self._add_token("SLASH")
        elif char == '"':
            self._string()
        elif char.isdigit():
            self._number()
        elif char.isalpha() or char == '_':
            self._identifier()
        else:
            self._handle_operator_or_punct(char)

    def _handle_operator_or_punct(self, char: str):
        # Two-character tokens
        if char == '=' and self._peek() == '=': self._add_token("EQ_EQ"); self._advance()
        elif char == '!' and self._peek() == '=': self._add_token("BANG_EQ"); self._advance()
        elif char == '<' and self._peek() == '=': self._add_token("LESS_EQ"); self._advance()
        elif char == '>' and self._peek() == '=': self._add_token("GREATER_EQ"); self._advance()
        elif char == '&' and self._peek() == '&': self._add_token("AND"); self._advance()
        elif char == '|' and self._peek() == '|': self._add_token("OR"); self._advance()
        # One-character tokens
        elif char == '(': self._add_token("LPAREN")
        elif char == ')': self._add_token("RPAREN")
        elif char == '{': self._add_token("LBRACE")
        elif char == '}': self._add_token("RBRACE")
        elif char == '[': self._add_token("LBRACKET")
        elif char == ']': self._add_token("RBRACKET")
        elif char == ',': self._add_token("COMMA")
        elif char == '.': self._add_token("DOT")
        elif char == '-': self._add_token("MINUS")
        elif char == '+': self._add_token("PLUS")
        elif char == ';': self._add_token("SEMICOLON")
        elif char == '*': self._add_token("STAR")
        elif char == '%': self._add_token("PERCENT")
        elif char == '!': self._add_token("BANG")
        elif char == '=': self._add_token("EQ")
        elif char == '<': self._add_token("LESS")
        elif char == '>': self._add_token("GREATER")
        elif char == ':': self._add_token("COLON")
        else:
            # TODO: Better error handling
            print(f"[{self.line}:{self.col}] Unexpected character: {char}")

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, "IDENTIFIER")
        self._add_token(token_type)

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        self._add_token("DIGIT", self.source[self.start:self.current])

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()

        if self._is_at_end():
            # TODO: Better error handling
            print(f"[{self.line}:{self.col}] Unterminated string.")
            return

        self._advance() # The closing "
        # Trim surrounding quotes and add token.
        value = self.source[self.start + 1:self.current - 1]
        self._add_token("WORD", value)
