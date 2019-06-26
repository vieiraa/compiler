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

def tokenize(string):
    temp = ""
    column = 0
    line = 0
    token_type = ''
    is_real = False
    is_id = False

    tokens = []
    for i in range(len(string)):
        try:
            if string[i] == '\n':
                line += 1
                column = 0
                continue

            elif string[i] != '}' and token_type == 'comment':
                column += 1
                continue

            elif string[i] == '}' and token_type == 'comment':
                token_type = ''
                column += 1
                continue

            elif string[i].isspace():
                column += 1
                continue

            elif string[i] == '{':
                token_type = 'comment'
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
                    raise ValueError()

                continue

            elif string[i] in [':', ';', '.', ',', '(', ')'] and token_type not in ['real', 'integer']:
                aux = string[i + 1]
                temp += string[i]
                if aux == '=':
                    continue
                else:
                    token_type = 'delimiter'

                raise ValueError()

            elif string[i] in ['=', '<', '>']:
                token_type = 'relational'
                temp += string[i]
                if temp == ':=':
                    token_type = 'assignment'
                    raise ValueError()

                aux = string[i + 1]
                if aux in ['=', '>']:
                    continue

                raise ValueError()

            elif string[i] in ['+', '-']:
                token_type = 'aditive'
                temp += string[i]
                raise ValueError()

            elif string[i] in ['*', '/']:
                token_type = 'multiplicative'
                temp += string[i]
                raise ValueError()

            elif string[i].isalnum() or string[i] == '_':
                temp += string[i]
                aux = string[i + 1]
                is_id = True
                if not aux.isalnum():
                    if temp in KEYWORDS:
                        token_type = 'keyword'
                        raise ValueError()

                    elif temp == 'and':
                        token_type = 'multiplicative'
                        raise ValueError()

                    elif temp == 'or':
                        token_type = 'aditive'
                        raise ValueError()
                
                    else:
                        token_type = 'identifier'
                        raise ValueError()

                continue

        except:
            tokens.append(Token(temp, token_type, line, column))
            column += len(temp)
            token_type = ''
            is_real = False
            is_id = False
            temp = ''
            continue

    return tokens

def main():
    string = """
program teste;
var
    valor1: integer;
    valor2: real;
    valor3: boolean;
begin
    valor2 := 10.5;
    valor1 := 10;
    valor3 := 10 <= 5;
end.
"""
    tokens = tokenize(string)
    #print("string = " + string + ", size = " + str(len(string)))
    print("tokens = " + str(tokens))

if __name__ == "__main__":
    main()
