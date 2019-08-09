import lexico as lx
import sys

DEBUG = False
DEBUG_STACK = True

class SyntaxError(Exception):
    pass

class ScopeError(Exception):
    pass

class TypeError(Exception):
    pass

def debug(name, token):
    if DEBUG:
        print('Entering', name, token)

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        if not self.search_scope(item, inner=True):
            self.stack.append(item)
        else:
            raise ScopeError(f'Name {item} already in use in this scope')

    def pop(self):
        return self.stack.pop()

    def open_scope(self):
        self.stack.append('$')

    def close_scope(self):
        aux = self.stack.pop()

        while aux != '$':
            aux = self.stack.pop()

    def search_scope(self, item, inner=False):
        for token in reversed(self.stack):
            if inner:
                if token == '$':
                    return None
            if token == item:
                return token

        return None


    def __str__(self):
        return str(self.stack)

    def __repr__(self):
        return str(self.stack)

class Type:
    def __init__(self, token, type_):
        self.token = token
        self.type_ = type_

    def __repr__(self):
        return f'{self.token} - {self.type_}'

    def __eq__(self, other):
        if isinstance(other, Type):
            return (self.token == other.token) and (self.type_ == other.type_)
        elif isinstance(other, str):
            return self.token == other

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur_token = 0
        self.var_stack = Stack()
        self.proc_stack = Stack()
        self.type_stack = Stack()
        self.aux_type_stack = []
        self.working_and = None
        self.working_or = None
        self.working_type = None
        self.working_var = None
        self.working_exp = None

    def debug_scope_stack(self):
        if DEBUG_STACK:
            print(self.var_stack)

    def check_scope(self, item):
        if not self.var_stack.search_scope(item):
            raise ScopeError(f'Name {item} does not exist in this scope')

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
            self.var_stack.open_scope()
            self.type_stack.open_scope()
            token = self.next_token()

            if token.what == 'Identifier':
                self.var_stack.push(token.token)
                self.type_stack.push(Type(token.token, 'program'))
                token = self.next_token()

                if token.token == ';':
                    token = self.next_token()
                    token = self.declaracoes_variaveis(token)
                    token = self.declaracoes_subprogramas(token)
                    token = self.comando_composto(token)

                    if token.token == '.':
                        self.var_stack.close_scope()
                        return True
                    else:
                        raise SyntaxError("Missing '.'")
                else:
                    raise SyntaxError("Missing ';'")
            else:
                raise SyntaxError(f'{token.token} is not a valid identifier.')
        else:
            raise SyntaxError("Missing 'program' keyword.")

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
            raise SyntaxError('Missing ;')

        raise SyntaxError('Expecting :')

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

            raise SyntaxError('Missing ;')

        return token

    def lista_identificadores(self, token):
        #debug('list ids', token)

        if token.what == 'Identifier':
            self.aux_type_stack.append(token.token)
            self.var_stack.push(token.token)
            token = self.next_token()
            token = self._lista_identificadores(token)
            return token

        return token

    def _lista_identificadores(self, token):
        #debug('_list ids', token)

        if token.token == ',':
            token = self.next_token()
            if token.what == 'Identifier':
                self.aux_type_stack.append(token.token)
                self.var_stack.push(token.token)
                token = self.next_token()
                token = self._lista_identificadores(token)
                return token

        return token

    def tipo(self, token):
        #debug('tipo', token)

        if token.token in ['integer', 'real', 'boolean']:
            for var in self.aux_type_stack:
                self.type_stack.push(Type(var, token.token))
            self.aux_type_stack.clear()
            return self.next_token()

        raise SyntaxError('Missing type')

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
                self.proc_stack.push(token.token)
                self.proc_stack.open_scope()
                self.var_stack.open_scope()
                self.type_stack.open_scope()
                token = self.next_token()
                token = self.argumentos(token)
                token = self.declaracoes_variaveis(token)
                token = self.comando_composto(token)
                self.debug_scope_stack()
                self.type_stack.close_scope()
                self.var_stack.close_scope()
                self.proc_stack.close_scope()
                return token
            else:
                raise SyntaxError('Invalid identifier')
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
                    raise SyntaxError('Missing ;')

        else:
            #raise SyntaxError('Missing (')
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
            raise SyntaxError('Missing end', token)
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
                self.check_scope(token.token)
                self.working_type = self.type_stack.search_scope(token.token).type_
                self.working_var = token.token
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
                #token = self.next_token()
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
                    print(token, 'oi')
                    raise SyntaxError("Missing 'then' after if")
                
            elif token.token == 'case':
                token = self.next_token()
                if token.what == 'Identifier':
                    self.check_scope(token.token)
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
                            raise SyntaxError('Missing end')
                    else:
                        raise SyntaxError('Missing of')
                else:
                    raise SyntaxError('Expecting identifier')

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
                    raise SyntaxError('Missing do after while')

            elif token.token == 'begin':
                token = self.comando_composto(token)
                ret = token
                raise ValueError()

            elif token.token == ';':
                return token

        except ValueError:
            if ret.token == ';':
                return ret
            print(ret)
            #exit(0)
            raise SyntaxError('Missing ;')

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
                raise SyntaxError('Missing :')
        else:
            raise SyntaxError('Expecting integer')
            

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
                raise SyntaxError('Missing :')
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
            self.working_or = token
            token = self.termo(token)
            if token.what == 'Aditive':
                op = token.token
                if op == 'or':
                    if self.working_or:
                        if self.working_exp:
                            op1 = lx.Token('true', 'Boolean', 0)
                        else:
                            op1 = self.working_or

                        op2 = self.next_token()
                        
                        if op1.what == 'Boolean' and op2.what == 'Boolean':
                            return self.next_token()
                        else:
                            raise TypeError(f'Incompatible types between {op1.what} and {op2.what}')

                else: 
                    token = self.next_token()
                    token = self.expressao_simples(token)

            return token

    def sinal(self, token):
        if DEBUG:
            print('sinal')

        if token.token in ['+', '-']:
            return self.next_token()

        return None

    def termo(self, token):
        if DEBUG:
            print('termo')

        self.working_and = token
        
        aux = self.fator(token)
        if aux:
            token = self._termo(aux)

        return token

    def _termo(self, token):
        if token.what == 'Multiplicative':
            op = token.token
            if op == 'and':
                if self.working_and:
                    if self.working_exp:
                        op1 = lx.Token('true', 'Boolean', 0)
                    else:
                        op1 = self.working_and
                    op2 = self.next_token()

                    if op1.what == 'Boolean' and op2.what == 'Boolean':
                        return self.next_token()
                    else:
                        raise TypeError(f'Incompatible types between {op1.what} and {op2.what}')
                        
            else:
                token = self.next_token()
           
                token = self.fator(token)
                token = self._termo(token)

        return token

    def fator(self, token):
        if DEBUG:
            print('fator')

        if token.what == 'Identifier':
            self.working_type = self.type_stack.search_scope(token.token).type_
            this_type = self.type_stack.search_scope(token.token)
            if this_type:
                this_type = this_type.type_
            else:
                raise ScopeError(f'Variable {token.token} does not exist in this scope')
            token = self.next_token()
            print(token)
            token = self._fator(token)
            return token

        elif token.token in ['true', 'false']:
            if self.working_type:
                if self.working_type != 'boolean':
                    raise TypeError(f'Type boolean is incompatible with type {self.working_type} of {self.working_var}')
            return self.next_token()

        elif token.what == 'Real':
            type_ = token.what.lower()
            if self.working_type != 'real' and self.working_type != 'boolean':
                raise TypeError(f'Type {type_} of {token.token} is incompatible with type {self.working_type} of {self.working_var}')
            return self.next_token()
        
        elif token.what in 'Integer':
            if self.working_type != 'real':
                if self.working_type != 'integer' and self.working_type != 'boolean':
                    raise TypeError(f'Token {token.token} is incompatible with type {self.working_type} of {self.working_var}')
            return self.next_token()


        elif token.token == '(':
            token = self.next_token()
            self.working_exp = True
            token = self.expressao(token)
            if token.token == ')':
                ret = self.next_token()
                return ret
            raise SyntaxError('Missing )')

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
            raise SyntaxError('Missing )')
        return token#self.next_token()

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
    #except SyntaxError as ex:
    #    print(ex)
    except TypeError as ex:
        print(ex)
