import lexico as lx

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur_token = 0
    
    def next_token(self):
        ret = self.tokens[self.cur_token]
        self.cur_token += 1
        return ret

    def start(self):
        token = self.next_token()
        self.program(token)

    def program(self, token):
        if token == 'program':
            token = self.next_token()

            if token.what == 'Identifier':
                token = self.next_token()

                if token == ';':
                    token = self.next_token()
                    token = self.declaracao_variaveis(token)
                    token = self.declaracoes_subprogramas(token)
                    token = self.comando_composto(token)
                    if token != '.':
                        raise ValueError

    def declaracoes_variaveis(self, token):
        if token == 'var':
            token = self.next_token()
            token = self.lista_declaracoes_variaveis(token)

        else:
            token = self.next_token()
            
        return token

    def lista_declaracoes_variaveis(self, token):
        token = self.lista_declaracoes(token) # TODO: resolver recursao a esquerda
        token = self.lista_identificadores(token)
        if token == ':':
            token = self.tipo(token)
            if token == ';':
                return token

    def lista_identificadores(self, token):
        if token.what == 'Identifier':
            return self.next_token()
        else:
            token = self.lista_identificadores(token)
            if token == ',':
                token = self.next_token()
                if token.what == 'Identifier':
                    return self.next_token()

    def tipo(self, token):
        if token in ['integer', 'real', 'boolean']:
            return self.next_token()

        raise ValueError

    def declaracoes_subprogramas(self, token):
        token = self.declaracoes_subprogramas(token) # TODO: resolver recursao a esquerda
        token = self.declaracao_subprograma(token)

        return token

    def declaracao_subprograma(self, token):
        if token == 'procedure':
            token = self.next_token()
            if token.what == 'Identifier':
                token = self.argumentos(token)
                token = self.declaracoes_variaveis(token)
                token = self.comando_composto(token)
                
                return token
            else:
                raise ValueError
        else:
            return self.next_token()

    def argumentos(self, token):
        if token == '(':
            token = self.next_token()
            token = self.lista_parametros(token)
            if token == ')':
                return self.next_token()

        return self.next_token()

    def lista_parametros(self, token):
        token = self.lista_parametros(token) # TODO: resolver recursao a esquerda
        if token == ';':
            token = self.next_token()
            token = self.lista_identificadores(token)
            if token == ':':
                token = self.tipo(token)

                return token

    def comando_composto(self, token):
        if token == 'begin':
            token = self.next_token()
            token = self.comandos_opcionais(token)
            if token == 'end':
                return self.next_token()

    def comandos_opcionais(self, token):
        token = self.lista_comandos(token)

        return token

    def lista_comandos(self, token):
        token = self.lista_comandos(token)
        if token == ';':
            token = self.next_token()
            token = self.comando(token)

            return token

    def comando(self, token):
        if token.what == 'Identifier':
            token = self.next_token()
            if token == ':=':
                token = self.next_token()
                token = self.expressao(token)

                return token
        elif 
    
                    
