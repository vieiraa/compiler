KEYWORDS = ['program', 'var', 'integer', 'real',
            'boolean', 'procedure', 'begin', 'end',
            'if', 'then', 'else', 'while', 'do', 'not']

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

class State:
    def __init__(self, name, accepting):
        self.name = name
        self.accepting = accepting
        self.line = 0
        self.column = 0

    def read(self, char, next_char):
        pass

class StartState(State):
    def __init__(self):
        self.aux = ''
        super().__init__('Start', False)

    def read(self, char, next_char):
        if char.isspace():
            self.column += 1
            return self

        if char == '\n':
            self.line += 1
            self.column = 0
            return self

        if char.isnumeric():
            return IntegerState()

        if char in ['(', ')', ',', '.', ';']:
            return TokenFoundState('Delimiter')

        if char == ':':
            if next_char == '=':
                return DelimiterState()
            return TokenFoundState('Delimiter')

        if char in ['+', '-']:
            return TokenFoundState('Aditive')

        if char in ['*', '/']:
            return TokenFoundState('Multiplicative')

        if char.isalpha() or char == '_':
            return IdentifierState()

        if char in ['=', '<', '>']:
            return RelationalState(char)

class IntegerState(State):
    def __init__(self):
        super().__init__('Integer', False)

    def read(self, char, next_char):
        if char == '.' or next_char == '.':
            return RealState()

        if next_char.isnumeric():
            return self

        if not next_char.isnumeric() or next_char != '.':
            return TokenFoundState(self.name)

class RealState(State):
    def __init__(self):
        super().__init__('Real', False)

    def read(self, char, next_char):
        if char in ['e', 'E'] or next_char in ['e', 'E']:
            return PowerState1()

        if next_char.isnumeric():
            return self

        return TokenFoundState(self.name)

class PowerState1(State):
    def __init__(self):
        super().__init__('Power', False)

    def read(self, char, next_char):
        if char in ['+', '-'] or next_char in ['+', '-']:
            self.numbers = True
            return PowerState2()

class PowerState2(State):
    def __init__(self):
        super().__init__('Power', False)

    def read(self, char, next_char):
        if next_char.isnumeric():
            return self

        return TokenFoundState('Real')

class IdentifierState(State):
    def __init__(self):
        super().__init__('Identifier', False)

    def read(self, char, next_char):
        if char.isalnum() and (next_char.isalnum() or next_char == '_'):
            return self

        return TokenFoundState(self.name)

class DelimiterState(State):
    def __init__(self):
        super().__init__('Delimiter', False)

    def read(self, char, next_char):
        if char == '=':
            return TokenFoundState('Assignment')

        return TokenFoundState(self.name)

class RelationalState(State):
    def __init__(self, what):
        super().__init__('Relational', False)
        self.what = what

    def read(self, char, next_char):
        if self.what == '<':
            if next_char in ['=', '<', '>']:
                return self
            return TokenFoundState(self.name)

        if self.what == '>':
            if next_char == '=':
                return self
            return TokenFoundState(self.name)

        return TokenFoundState(self.name)

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
        line = 0
        column = 0
        what = ''
        for i in range(len(string)):
            c = string[i]

            if c == '\n':
                line += 1
                column = 0
                continue

            temp += c
            if i == len(string) - 1:
                aux = string[i]
            else:
                aux = string[i + 1]

            state = state.read(c, aux)
            if state.accepting:
                what = state.name
                if temp in KEYWORDS:
                    what = 'Keyword'

                elif temp == 'or':
                    what = 'Aditive'

                elif temp == 'and':
                    what = 'Multiplicative'

                tokens.append(Token(temp.strip(), what, line, column))

                column += len(temp)

                temp = ''
                state = self.start

        return tokens
