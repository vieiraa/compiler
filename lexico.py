import sys
import fileinput

class Token:
    def __init__(self, tok, what, line, column):
        self.token = tok
        self.line = line
        self.column = column
        self.what = what

    def __repr__(self):
        return f"<{self.line}:{self.column} | {self.token} | {self.what}>\n"

    def __str__(self):
        return f"<{self.line}:{self.column} | {self.token} | {self.what}>\n"

class TokenFoundException(Exception):
    pass

class InvalidSymbolError(Exception):
    pass

KEYWORDS = ['program', 'var', 'integer', 'real',
            'boolean', 'procedure', 'begin', 'end',
            'if', 'then', 'else', 'while', 'do', 'not']

def tokenize(string):
    temp = ""
    column = 0
    line = 0
    token_type = ''
    is_real = False
    is_id = False
    comment = None

    tokens = []
    for i in range(len(string)):
        try:
            if string[i] == '\n':
                line += 1
                column = 0
                continue

            if comment is not None:
                if string[i] == '}':
                    column += 1
                    comment = None
                    continue
                column += 1
                continue

            elif string[i] == '{' and comment is None:
                comment = Token('comment', 'comment', line, column)
                continue

            elif string[i].isspace():
                column += 1
                continue

            elif string[i].isnumeric():
                aux = string[i + 1]
                temp += string[i]

                if aux == '.':
                    token_type = 'real'
                    temp += aux
                    is_real = True
                    continue

                elif not is_real and not is_id:
                    token_type = 'integer'

                elif is_id:
                    token_type = 'identifier'

                if not aux.isnumeric():
                    raise TokenFoundException

                continue

            elif string[i] in [':', ';', '.', ',', '(', ')'] and token_type not in ['real', 'integer']:
                aux = string[i + 1]
                temp += string[i]
                if temp == ':' and aux == '=':
                    continue
                else:
                    token_type = 'delimiter'

                raise TokenFoundException

            elif string[i] in ['=', '<', '>']:
                token_type = 'relational'
                temp += string[i]
                if temp == ':=':
                    token_type = 'assignment'
                    raise TokenFoundException

                aux = string[i + 1]
                if temp != '=' and aux in ['=', '>']:
                    continue

                raise TokenFoundException

            elif string[i] in ['+', '-']:
                token_type = 'aditive'
                temp += string[i]
                raise TokenFoundException

            elif string[i] in ['*', '/']:
                token_type = 'multiplicative'
                temp += string[i]
                raise TokenFoundException

            elif string[i].isalnum() or string[i] == '_':
                temp += string[i]
                aux = string[i + 1]
                is_id = True
                if not aux.isalnum():
                    if temp in KEYWORDS:
                        token_type = 'keyword'
                        raise TokenFoundException

                    elif temp == 'and':
                        token_type = 'multiplicative'
                        raise TokenFoundException

                    elif temp == 'or':
                        token_type = 'aditive'
                        raise TokenFoundException

                    else:
                        token_type = 'identifier'
                        raise TokenFoundException

                continue

            if token_type == '':
                raise InvalidSymbolError

        except TokenFoundException:
            tokens.append(Token(temp, token_type, line, column))
            column += len(temp)
            token_type = ''
            is_real = False
            is_id = False
            temp = ''
            continue

        except InvalidSymbolError:
            print('Invalid symbol: ' + string[i])
            exit(0)

    if comment is not None:
        print(f'Non-closed comment starting at {comment.line}:{comment.column}')
        exit(1)

    return tokens

if __name__ == "__main__":
    tokens = []
    if len(sys.argv) != 2:
        print(f'Usage: python lexico.py filename')
        sys.exit(0)

    with open(sys.argv[1], 'r') as infile:
        tokens = tokenize(infile.read())

    with open('table.txt', 'w') as outfile:
        for token in tokens:
            outfile.write(str(token))
