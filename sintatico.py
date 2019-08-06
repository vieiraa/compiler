import lexico as lx
import sys

DEBUG = False

def debug(name, token):
    if DEBUG:
        print('Entering', name, token)

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur_token = 0

    def next_token(self):
        ret = ''
        if self.cur_token < len(self.tokens):
            ret = self.tokens[self.cur_token]

        self.cur_token += 1
        return ret

    def start(self):
        token = self.next_token()
        return self.program(token)

    def program(self, token):

        #debug('program', token)

        if token.token == 'program':
            token = self.next_token()

            if token.what == 'Identifier':
                token = self.next_token()

                if token.token == ';':
                    token = self.next_token()
                    token = self.declaracoes_variaveis(token)
                    token = self.declaracoes_subprogramas(token)
                    token = self.comando_composto(token)

                    if token.token == '.':
                        return True
                    else:
                        raise Exception("Missing '.'")
                else:
                    raise Exception("Missing ';'")
            else:
                raise Exception(f'{token.token} is not a valid identifier.')
        else:
            raise Exception("Missing 'program' keyword.")

    def declaracoes_variaveis(self, token):
        #debug('decl vars', token)

        if token.token == 'var':
            token = self.next_token()
            token = self.lista_declaracoes_variaveis(token)
            return token

        return token

    def lista_declaracoes_variaveis(self, token):
        #debug('list decl vars', token)

        token = self.lista_identificadores(token)
        if token.token == ':':
            token = self.next_token()
            token = self.tipo(token)
            if token.token == ';':
                token = self.next_token()
                token = self._lista_declaracoes_variaveis(token)
                return token
            raise Exception('Missing ;')

        raise Exception('Expecting :')

    def _lista_declaracoes_variaveis(self, token):
        #debug('_list decl vars', token)

        token = self.lista_identificadores(token)
        if token.token == ':':
            token = self.next_token()
            token = self.tipo(token)
            if token.token == ';':
                token = self.next_token()
                token = self._lista_declaracoes_variaveis(token)
                return token

            raise Exception('Missing ;')

        return token

    def lista_identificadores(self, token):
        #debug('list ids', token)

        if token.what == 'Identifier':
            token = self.next_token()
            token = self._lista_identificadores(token)
            return token
        return token

    def _lista_identificadores(self, token):
        #debug('_list ids', token)

        if token.token == ',':
            token = self.next_token()
            if token.what == 'Identifier':
                token = self.next_token()
                token = self._lista_identificadores(token)
                return token


        return token

    def tipo(self, token):
        #debug('tipo', token)

        if token.token in ['integer', 'real', 'boolean']:
            return self.next_token()

        raise Exception('Missing type')

    def declaracoes_subprogramas(self, token):
        debug('decl subprogramas', None)

        token = self._declaracoes_subprogramas(token)

        return token

    def _declaracoes_subprogramas(self, token):
        #debug('_decl subs', token)
        token = self.declaracao_subprograma(token)
        #exit(0)
        if token.token == ';':
            token = self.next_token()
            token = self._declaracoes_subprogramas(token)
            return token

        return token

    def declaracao_subprograma(self, token):
        #debug('decl sub', token)

        if token.token == 'procedure':
            token = self.next_token()
            if token.what == 'Identifier':
                token = self.next_token()
                token = self.argumentos(token)
                token = self.declaracoes_variaveis(token)
                token = self.comando_composto(token)
                return token
            else:
                raise Exception('Invalid identifier')
        else:
            return token

    def argumentos(self, token):
        if DEBUG:
            print('args')

        if token.token == '(':
            token = self.next_token()
            token = self.lista_parametros(token)
            if token.token == ')':
                token = self.next_token()
                if token.token == ';':
                    return self.next_token()
                else:
                    raise Exception('Missing ;')

        else:
            #raise Exception('Missing (')
            return token#self.next_token()

    def lista_parametros(self, token):
        if DEBUG:
            print('list params')

        token = self.lista_identificadores(token)
        if token.token == ':':
            token = self.next_token()
            token = self.tipo(token)
            if token.token == ';':
                token = self.next_token()
                token = self.lista_parametros(token)

            return token

    def comando_composto(self, token):
        if DEBUG:
            print('com comp')

        if token.token == 'begin':
            token = self.next_token()
            token = self.comandos_opcionais(token)

            if token.token == 'end':
                return self.next_token()
            raise Exception('Missing end', token)
        return self.next_token()

    def comandos_opcionais(self, token):
        if DEBUG:
            print('com opcionais')

        token = self.lista_comandos(token)

        return token

    def lista_comandos(self, token):
        if DEBUG:
            print('list com')

        aux = self.comando(token)
        if aux is not None:
            token = aux

            token = self._lista_comandos(token)

        return token

    def _lista_comandos(self, token):
        if DEBUG:
            print('_lista comandos')
        if token.token == ';':
            token = self.next_token()

            aux = self.comando(token)
            if aux:
                token = aux

            token = self._lista_comandos(token)

        #token = self.next_token()
        return token

    def comando(self, token):
        ret = None

        try:
            if DEBUG:
                print('comando', token)

            if token.what == 'Identifier':
                token = self.next_token()
                if token.token == ':=':
                    token = self.next_token()
                    token = self.expressao(token)

                    ret = token
                    raise ValueError()
                else:
                    token = self.ativacao_procedimento(token)
                    ret = self.next_token()
                    raise ValueError()

            elif token.token == 'if':
                token = self.next_token()
                token = self.expressao(token)
                token = self.next_token()
                if token.token == 'then':
                    token = self.next_token()
                    aux = self.comando(token)
                    if aux:
                        token = aux
                    aux = self.next_token()
                    aux = self.parte_else(aux)
                    if aux:
                        token = aux

                    ret = token
                    raise ValueError()
                else:
                    raise Exception("Missing 'then' after if")
                
            elif token.token == 'case':
                token = self.next_token()
                if token.what == 'Identifier':
                    token = self.next_token()
                    if token.token == 'of':
                        token = self.next_token()
                        token = self.lista_case(token)
                        aux = self.parte_else(token)
                        if aux:
                            token = aux
                            token = self.next_token()
                        if token.token == 'end':
                            ret = self.next_token()
                            raise ValueError()
                        else:
                            raise Exception('Missing end')
                    else:
                        raise Exception('Missing of')
                else:
                    raise Exception('Expecting identifier')

            elif token.token == 'while':
                token = self.next_token()
                token = self.expressao(token)
                token = self.next_token()
                if token.token == 'do':
                    token = self.next_token()
                    token = self.comando(token)
                    ret = token
                    raise ValueError()
                else:
                    raise Exception('Missing do after while')

            elif token.token == 'begin':
                token = self.comando_composto(token)
                ret = token
                raise ValueError()

            elif token.token == ';':
                return token

        except ValueError:
            if ret.token == ';':
                return ret
            raise Exception('Missing ;')

    def lista_case(self, token):
        if token.what == 'Integer':
            token = self.next_token()
            if token.token == ':':
                token = self.next_token()
                token = self.lista_comandos(token)
                aux = self._lista_case(token)

                if aux:
                    token = aux

                return token
            else:
                raise Exception('Missing :')
        else:
            raise Exception('Expecting integer')
            

    def _lista_case(self, token):
        if token.what == 'Integer':
            token = self.next_token()
            if token.token == ':':
                token = self.next_token()
                token = self.lista_comandos(token)
                aux = self._lista_case(token)
                if aux:
                    token = aux

                return token
            else:
                raise Exception('Missing :')
        else:
            return None

    def parte_else(self, token):
        if DEBUG:
            print('else')

        if token.token == 'else':
            token = self.next_token()
            token = self.comando(token)

            return token
        else:
            return None

    def ativacao_procedimento(self, token):
        if DEBUG:
            print('ativ proc')
        if token.token == '(':
            token = self.next_token()
            token = self.lista_expressoes(token)
            return token
        return token

    def lista_expressoes(self, token):
        if DEBUG:
            print('list expr')

        token = self.expressao(token)
        token = self._lista_expressoes(token)
        return token

    def _lista_expressoes(self, token):
        if DEBUG:
            print('_lista expr')

        if token.token == ',':
            token = self.next_token()
            token = self.expressao(token)
            if token is not None:
                token = self._lista_expressoes(token)

        return token#self.next_token()

    def expressao(self, token):
        if DEBUG:
            print('expr')

        token = self.expressao_simples(token)
        token = self._expressao(token)

        return token

    def _expressao(self, token):
        if token.what == 'Relational':
            token = self.next_token()
            token = self.expressao_simples(token)
            return token

        return token#self.next_token()

    def expressao_simples(self, token):
        if DEBUG:
            print('expr simples')

        aux = self.sinal(token)
        if aux:
            #token = self.next_token('expr_simples sinal')
            token = self.termo(aux)
            return token
        else:
            token = self.termo(token)
            if token.what == 'Aditive':
                token = self.next_token()
                token = self.expressao_simples(token)

            return token
            #return token
        #return self.next_token('expr_simples')

    def sinal(self, token):
        if DEBUG:
            print('sinal')

        if token.token in ['+', '-']:
            return self.next_token()

        return None

    def termo(self, token):
        if DEBUG:
            print('termo')

        aux = self.fator(token)
        if aux:
            token = self._termo(aux)

        return token

    def _termo(self, token):
        if token.what == 'Multiplicative':
            token = self.next_token()
            token = self.fator(token)
            token = self._termo(token)

        return token

    def fator(self, token):
        if DEBUG:
            print('fator')

        if token.what == 'Identifier':
            token = self.next_token()
            token = self._fator(token)
            return token

        elif token.token in ['true', 'false']:
            return self.next_token()

        elif token.what in ['Integer', 'Real']:
            return self.next_token()

        elif token.token == '(':
            token = self.next_token()
            token = self.expressao(token)
            if token.token == ')':
                return token#self.next_token()
            raise Exception('Missing )')

        elif token.token == 'not':
            token = self.next_token()
            token = self.fator(token)
            return token

    def _fator(self, token):
        if token.token == '(':
            token = self.next_token()
            token = self.lista_expressoes(token)
            if token.token == ')':
                return self.next_token()
            raise Exception('Missing )')
        return self.next_token()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: python sintatico.py filename')
        sys.exit(0)

    with open(sys.argv[1], 'r') as infile:
        tokens = None
        try:
            tokens = lx.tokenize(infile.read())
        except Exception as ex:
            print(ex)
            exit(1)

    sin = Sintatico(tokens)
    try:
        res = sin.start()
        print('All good.')
    except Exception as ex:
        print(ex)
