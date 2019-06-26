import re

class Token:
    def __init__(self, token, what, line, column):
        self.token = token
        self.line = line
        self.column = column
        self.what = what

    def __repr__(self):
        return f"\n<{self.line}:{self.column} | {self.token} | {self.what}>"

    def __str__(self):
        return f"\n<{self.line}:{self.column} | {self.token} | {self.what}>"

KEYWORDS = ['program', 'var', 'integer', 'real',
            'boolean', 'procedure', 'begin', 'end',
            'if', 'then', 'else', 'while', 'do', 'not']

def tokenize(buffer):
    temp = ""
    column = 0
    line = 0
    is_if = ''
    aux = ''
    token_type = ''
    
    tokens = []
    i = 0
    for i in range(len(buffer)):
        try:
            if buffer[i] == '\n':
                line += 1
                column = 0
                continue

            elif buffer[i] != '}' and token_type == 'comment':
                column += 1
                continue

            elif buffer[i] == '}' and token_type == 'comment':
                column += 1
                token_type = ''
                continue

            elif buffer[i].isspace():
                column += 1
                continue

            elif buffer[i] == '{':
                column += 1
                token_type = 'comment'
                continue

            elif buffer[i].isnumeric():
                aux = buffer[i + 1]
                temp += buffer[i]
                column += 1
                token_type = 'integer'

                if aux == '.':
                    token_type = 'real'
                    temp += aux
                                        
                if not aux.isnumeric():
                    raise ValueError()

                continue

            elif buffer[i] in [':', ';', '.', ',', '(', ')'] and token_type not in ['real', 'integer']:
                column += 1
                temp += buffer[i]
                token_type = 'delimiter'
                print(buffer[i])
                if buffer[i] == ':':
                    print('oi')
                    aux = buffer[i + 1]
                    if aux == '=':
                        token_type = 'assignment'
                        column += 1
                        temp += aux
                        raise ValueError()
                    
                raise ValueError()

            elif buffer[i] in ['=', '<', '>'] and not token_type == 'assignment':
                token_type = 'relational'
                column += 1
                temp += buffer[i]
                aux = buffer[i + 1]
                if aux in ['=', '>']:
                    temp += aux
                    column += 1
                    raise ValueError()

                raise ValueError()

            elif buffer[i] in ['+', '-']:
                token_type = 'aditive'
                column += 1
                temp += buffer[i]
                raise ValueError()

            elif buffer[i] in ['*', '/']:
                token_type = 'multiplicative'
                column += 1
                temp += buffer[i]
                raise ValueError()

            elif buffer[i].isalnum() or buffer[i] == '_':
                temp += buffer[i]
                aux = buffer[i + 1]
                column += 1
                if temp in KEYWORDS:
                    token_type = 'keyword'
                    raise ValueError()

                elif temp == 'and':
                    token_type = 'multiplicative'
                    raise ValueError()

                elif temp == 'or':
                    token_type = 'aditive'
                    raise ValueError()
                
                elif not aux.isalnum():
                    token_type = 'identifier'
                    raise ValueError()

                continue

        except:
            print(temp == '>')
            tokens.append(Token(temp, token_type, line, column))
            column += len(temp)
            temp = ""
            continue

    return tokens

def main():
    buffer = """
    program teste; {programa exemplo}
    var
        valor1: integer;
        valor2: real;
    begin
        valor1 := 10 <> 2;
    end.
"""
    tokens = tokenize(buffer)
    print("buffer = " + buffer + ", size = " + str(len(buffer)))
    print("tokens = " + str(tokens))

if __name__ == "__main__":
    main()
