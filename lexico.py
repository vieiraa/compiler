import sys
import re

KEYWORDS = '^(program|var|integer|real|boolean|procedure|begin|end|if|then|else|while|do|not|case|of)\\b'
IDENTIFIER = '^[a-z]\w*\\b'
INTEGER = '^\d+(?!\.)'
REAL = '^\d+\.\d*(e(\+|-)\d*)?'
DELIMITER = '^(\.|,|;|:(?!=)|\(|\))'
ASSIGNMENT = '^:='
RELATIONAL = '^((?<!:)=|<(?!(=|>))|>(?!=)|<=|>=|<>)'
ADITIVE = '^(\+|-|or)'
MULTIPLICATIVE = '^(\*|/|and)'
COMMENT = '{.*?}'
BOOLEAN = '^(true|false)\\b'

PATTERNS = {
    'Keyword': KEYWORDS,
    'Real': REAL,
    'Integer': INTEGER,
    'Delimiter': DELIMITER,
    'Assignment': ASSIGNMENT,
    'Relational': RELATIONAL,
    'Aditive': ADITIVE,
    'Multiplicative': MULTIPLICATIVE,
    'Boolean': BOOLEAN,
    'Identifier': IDENTIFIER,
    'Comment': COMMENT
}

class Token:
    def __init__(self, tok, what, row):
        self.token = tok
        self.row = row
        self.what = what

    def __repr__(self):
        return f"<{self.row} | {self.token} | {self.what}>\n"

    def __str__(self):
        return f"<{self.row} | {self.token} | {self.what}>\n"

def tokenize(code):
    code = re.sub(PATTERNS['Comment'], '', code, flags=re.DOTALL)
    code = [line.strip() for line in code.split('\n') if line != '']
    tokens = []

    for i, line in enumerate(code):
        j = 0
        while j < len(line):
            j += next_col(line[j], line[j:], i, j, tokens)

    return tokens

def next_col(char, line, row, col, tokens):
    if re.match(r'\s', char):
        return 1

    if re.match('{', char):
        raise Exception('Unclosed comment')

    for key, value in PATTERNS.items():
        result = re.match(value, line, flags=re.IGNORECASE)

        if result:
            tokens.append(Token(result.group(0), key, row))
            return result.span()[1]

    raise Exception(f'Invalid symbol: {line}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: python lexico.py filename')
        sys.exit(0)

    with open(sys.argv[1], 'r') as infile:
        code = infile.read()
        tokens = tokenize(code)
        print(tokens)
