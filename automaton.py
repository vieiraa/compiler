KEYWORDS = ['program', 'var', 'integer', 'real',
            'boolean', 'procedure', 'begin', 'end',
            'if', 'then', 'else', 'while', 'do', 'not']

aux_c = ''
row = 1
column = 1

class Token:
    def __init__(self, tok, what, row, col):
        self.token = tok
        self.row = row
        self.col = col
        self.what = what

    def __repr__(self):
        return f"<{self.row}:{self.col} | {self.token} | {self.what}>\n"

    def __str__(self):
        return f"<{self.row}:{self.col} | {self.token} | {self.what}>\n"

class State:
    def __init__(self, name, accepting):
        self.name = name
        self.accepting = accepting

    def read(self, char, next_char):
        pass

class StartState(State):
    def __init__(self):
        self.aux = ''
        super().__init__('Start', False)

    def read(self, char, next_char):
        global row
        global column

        if char == '\n':
            row += 1
            column = 1
            return '', self

        if char.isspace():
            column += 1
            return '', self
        
        if char == '{':
            return '', CommentState(row, column)

        if char == '\n' or char.isspace():
            return '', self

        if char.isnumeric() and (next_char.isnumeric() or next_char == '.'):
            return char, IntegerState()

        if char.isnumeric() and not (next_char.isnumeric() or next_char == '.'):
            return char, TokenFoundState('Integer')

        if char in ['(', ')', ',', '.', ';']:
            return char, TokenFoundState('Delimiter')

        if char == ':':
            if next_char == '=':
                return char, DelimiterState()
            return char, TokenFoundState('Delimiter')

        if char in ['+', '-']:
            return char, TokenFoundState('Aditive')

        if char in ['*', '/']:
            return char, TokenFoundState('Multiplicative')

        if (char.isalpha() or char == '_') and (next_char.isalnum() or next_char == '_'):
            return char, IdentifierState()
        
        if (char.isalpha() or char == '_') and not (next_char.isalnum() or next_char == '_'):
            return char, TokenFoundState('Identifier')
        
        if char in ['=', '<', '>']:
            return char, RelationalState(char)

class IntegerState(State):
    def __init__(self):
        super().__init__('Integer', False)

    def read(self, char, next_char):
        if char == '.' and next_char.isnumeric():
            return char, RealState()

        if char == '.' and not next_char.isnumeric():
            return char, TokenFoundState('Real')

        if char.isnumeric() and next_char.isnumeric():
            return char, self

        if char.isnumeric() and not next_char.isnumeric():
            return char, TokenFoundState(self.name)

class RealState(State):
    def __init__(self):
        super().__init__('Real', False)

    def read(self, char, next_char):
        global aux_c
        if char in ['e', 'E'] and aux_c.isnumeric():
            return char, PowerState1()

        if char.isnumeric() and next_char.isnumeric():
            return char, self
        
        if char.isnumeric() and not next_char.isnumeric():
            return char, TokenFoundState(self.name)

class PowerState1(State):
    def __init__(self):
        super().__init__('Power', False)

    def read(self, char, next_char):
        if char in ['+', '-']:
            self.numbers = True
            return char, PowerState2()

class PowerState2(State):
    def __init__(self):
        super().__init__('Power', False)

    def read(self, char, next_char):
        if char.isnumeric() and next_char.isnumeric():
            return char, self
        if char.isnumeric() and not next_char.isnumeric():
            return char, TokenFoundState('Real')

class IdentifierState(State):
    def __init__(self):
        super().__init__('Identifier', False)

    def read(self, char, next_char):
        if char.isalnum() and (next_char.isalnum() or next_char == '_'):
            return char, self

        return char, TokenFoundState(self.name)

class DelimiterState(State):
    def __init__(self):
        super().__init__('Delimiter', False)

    def read(self, char, next_char):
        if char == '=':
            return char, TokenFoundState('Assignment')

        return '', TokenFoundState(self.name)

class RelationalState(State):
    def __init__(self, what):
        super().__init__('Relational', False)
        self.what = what

    def read(self, char, next_char):
        if self.what == '<':
            if next_char in ['=', '<', '>']:
                return char, self
            return char, TokenFoundState(self.name)

        if self.what == '>':
            if next_char == '=':
                return char, self
            return char, TokenFoundState(self.name)

        return '', TokenFoundState(self.name)

class CommentState(State):
    def __init__(self, row, col):
        super().__init__('Comment', False)
        self.s_row = row
        self.s_col = col

    def read(self, char, next_char):
        global row, column
        if char != '}':
            if char.isspace():
                column += 1
            elif char == '\n':
                row += 1
                column = 1
            return '', self
        self.s_row = 0
        self.s_col = 0
        return StartState()

class TokenFoundState(State):
    def __init__(self, name):
        super().__init__(name, True)

class Automaton:
    def __init__(self, start=StartState()):
        self.start = start

    def tokenize(self, string):
        state = self.start
        temp = ''
        tokens = []
        what = ''
        global row, column
        for i, c in enumerate(string):
            try:
                if c == '}' and state.name == 'Comment':
                    state = self.start
                    continue
                
                if i == len(string) - 1:
                    aux = string[i]
                else:
                    aux = string[i + 1]

                global aux_c
                if i == len(string) - 2:
                    aux_c = string[i + 1]
                elif i == len(string) - 1:
                    aux_c = string[i]
                else:
                    aux_c = string[i + 2]

                char, state = state.read(c, aux)
                temp += char
                if row == 10:
                    print(temp)

                if state.accepting:
                    temp = temp.strip()
                    what = state.name
                    if temp in KEYWORDS:
                        what = 'Keyword'

                    elif temp == 'or':
                        what = 'Aditive'

                    elif temp == 'and':
                        what = 'Multiplicative'

                    tokens.append(Token(temp.strip(), what, row, column))

                    column += len(temp)

                    temp = ''
                    state = self.start
            except:
                print('Invalid symbol: ', c)
                exit(0)

        if state.name == 'Comment':
            print(f'Not closed comment starting at {state.s_row}:{state.s_col}')


        return tokens
