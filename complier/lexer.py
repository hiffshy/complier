import re

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.position = (line, column)

TOKEN_SPEC = [
    ('PRINTF', r'printf\b'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('SEMICOLON', r';'),
    ('STRING', r'"([^"\\]|\\.)*"'),
    ('COMMA', r','),
    ('FORMAT_SPEC', r'%[disfcuoxp]'),
    ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('WHITESPACE', r'\s+'),
    ('ERROR', r'.')
]

def tokenize(code):
    tokens = []
    line = 1
    line_start = 0

    for match in re.finditer(
        '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC),
        code
    ):
        kind = match.lastgroup
        value = match.group()
        start_pos = match.start()

        if kind == 'WHITESPACE':
            line += value.count('\n')
            line_start = match.end()
            continue

        column = start_pos - line_start + 1
        if kind == 'ERROR':
            tokens.append(Token('ERROR', value, line, column))
        else:
            tokens.append(Token(kind, value, line, column))

    return tokens