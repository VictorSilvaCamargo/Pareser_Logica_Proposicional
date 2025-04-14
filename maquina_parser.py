# Discentes: Renan Antonio Hammerschmidt Krefta, Victor Silva Camargo, Vinícius Silva Camargo

## Conjunto de Regras
"""

import sys

# Conjunto de Regras
regras = {
    "FORMULA": "CONSTANTE | PROPOSICAO | FORMULAUNARIA | FORMULABINARIA",
    "CONSTANTE": "true | false",
    "PROPOSICAO": "[0-9][0-9a-z]*",
    "FORMULAUNARIA": "( OPERATORUNARIO FORMULA )",
    "FORMULABINARIA": "( OPERATORBINARIO FORMULA FORMULA )",
    "OPERATORUNARIO": "\\neg",
    "OPERATORBINARIO": "\\wedge | \\vee | \\rightarrow | \\leftrightarrow",
    "ABREPAREN": "(",
    "FECHAPAREN": ")"
}

operadores_binarios = [op.strip() for op in regras["OPERATORBINARIO"].split("|")]
operadores_unarios = [regras["OPERATORUNARIO"]]
constantes = [c.strip() for c in regras["CONSTANTE"].split("|")]

def eh_proposicao(token):
    return token and token[0].isdigit() and all(c.isdigit() or 'a' <= c <= 'z' for c in token[1:])

def eh_constante(token):
    return token in constantes

class StateMachine:
    def __init__(self):
        self.state = 'start'
        self.transitions = {
            'start': {'CONSTANTE': 'formula_simples_correta',
                      'PROPOSICAO': 'formula_simples_correta',
                      'ABREPAREN': 'abre_parenteses'},
            'formula_simples_correta': {' ': 'formula_simples_correta'},
            'abre_parenteses': {' ': 'abre_parenteses',
                                'ABREPAREN': 'abre_parenteses',
                                'OPERADORUNARIO': 'operador_unario',
                                'OPERADORBINARIO': 'operador_binario'},
            'operador_unario': {' ': 'operador_unario',
                                'CONSTANTE': 'termo_unario',
                                'PROPOSICAO': 'termo_unario',
                                'ABREPAREN': 'abre_parenteses'},
            'termo_unario': {' ': 'termo_unario',
                             'FECHAPAREN': 'fecha_parenteses'},
            'operador_binario': {' ': 'operador_binario',
                                 'ABREPAREN': 'abre_parenteses',
                                 'CONSTANTE': 'termo_binario_nao_final',
                                 'PROPOSICAO': 'termo_binario_nao_final'},
            'termo_binario_nao_final': {' ': 'termo_binario_nao_final',
                                        'CONSTANTE': 'termo_binario_final',
                                        'PROPOSICAO': 'termo_binario_final',
                                        'ABREPAREN': 'abre_parenteses'},
            'termo_binario_final': {' ': 'termo_binario_final',
                                    'FECHAPAREN': 'fecha_parenteses'},
            'fecha_parenteses': {' ': 'fecha_parenteses',
                                 'ABREPAREN': 'abre_parenteses',
                                 'FECHAPAREN': 'fecha_parenteses',
                                 'CONSTANTE': 'termo_binario_final',
                                 'PROPOSICAO': 'termo_binario_final'}
        }
        self.final_states = {'formula_simples_correta', 'fecha_parenteses'}

    def trigger(self, event):
        if event in self.transitions[self.state]:
            self.state = self.transitions[self.state][event]

    def process(self, tokens):
        self.state = 'start'
        tokens_converted = []
        for token in tokens:
            if eh_constante(token):
                tokens_converted.append('CONSTANTE')
            elif token == '(':
                tokens_converted.append('ABREPAREN')
            elif token == ')':
                tokens_converted.append('FECHAPAREN')
            elif token == '\\neg':
                tokens_converted.append('OPERADORUNARIO')
            elif token in operadores_binarios:
                tokens_converted.append('OPERADORBINARIO')
            elif eh_proposicao(token):
                tokens_converted.append('PROPOSICAO')
            else:
                tokens_converted.append(token)

        for token in tokens_converted:
            if token not in self.transitions.get(self.state, {}):
                return False
            self.trigger(token)

        if self.state in self.final_states:
            return tokens
        return False

class LL1_Parser:
    def __init__(self, tokens):
        self.tokens = tokens + ['$']
        self.pos = 0

    def atual(self):
        return self.tokens[self.pos]

    def proximo(self):
        self.pos += 1

    def match(self, esperado):
        if self.atual() == esperado:
            self.proximo()

    def parse(self):
        self.F()
        return self.atual() == '$'

    def F(self):
        token = self.atual()
        if eh_constante(token):
            self.C()
        elif eh_proposicao(token):
            self.P()
        elif token == '(':
            lookahead = self.tokens[self.pos + 1]
            if lookahead == '\\neg':
                self.FU()
            elif lookahead in operadores_binarios:
                self.FB()

    def C(self):
        self.match(self.atual())

    def P(self):
        self.match(self.atual())

    def FU(self):
        self.match('(')
        self.match('\\neg')
        self.F()
        self.match(')')

    def FB(self):
        self.match('(')
        op = self.atual()
        if op in operadores_binarios:
            self.match(op)
        self.F()
        self.F()
        self.match(')')

# --- Ponto de entrada do script ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parser.py <arquivo.txt>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)

    qtd = int(linhas[0].strip())
    expressoes = [linha.strip() for linha in linhas[1:]]

    for expr in expressoes:
        tokens = expr.replace("(", " ( ").replace(")", " ) ").split()

        fsm = StateMachine()
        result = fsm.process(tokens)

        if result == False:
            print("invalida")
        else:
            parser = LL1_Parser(result)
            if parser.parse():
                print("valida")
            else:
                print("invalida")
