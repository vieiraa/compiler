import sys
from automaton import Automaton

if __name__ == '__main__':
    tokens = []
    if len(sys.argv) != 2:
        print(f'Usage: python lexico.py filename')
        sys.exit(0)

    with open(sys.argv[1], 'r') as infile:
        auto = Automaton()
        tokens = auto.tokenize(infile.read())

    with open('table.txt', 'w') as outfile:
        for token in tokens:
            outfile.write(str(token))
