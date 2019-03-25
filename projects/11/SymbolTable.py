import json

STATIC_CONSTANT = 'static'
FIELD_CONSTANT = 'field'
ARG_CONSTANT = 'arg'
VAR_CONSTANT = 'var'


class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.inSubroutine = False
        self.class_index = {
            STATIC_CONSTANT: 0,
            FIELD_CONSTANT: 0
        }

    def startSubroutine(self):
        self.inSubroutine = True
        self.subroutine_index = {
            ARG_CONSTANT: 0,
            VAR_CONSTANT: 0
        }

    def define(self, name, type, kind):
        variable = {'type': type, 'kind': kind}
        if(self.inSubroutine):
            variable.update({'index': self.subroutine_index[kind]})
            self.subroutine_table[name] = variable
            self.subroutine_index[kind] += 1
        else:
            variable.update({'index': self.class_index[kind]})
            self.class_table[name] = variable
            self.class_index[kind] += 1

    def varCount(self, kind):
        if(self.inSubroutine):
            return self.subroutine_index.get(kind)
        else:
            return self.class_index.get(kind)

    def kindOf(self, name):
        if(self.inSubroutine):
            return self.subroutine_table[name].get('kind')
        else:
            return self.class_table[name].get('kind')

    def typeOf(self, name):
        if(self.inSubroutine):
            return self.subroutine_table[name].get('type')
        else:
            return self.class_table[name].get('type')

    def indexOf(self, name):
        if(self.inSubroutine):
            return self.subroutine_table[name].get('index')
        else:
            return self.class_table[name].get('index')

    def __repr__(self):
        string = 'Class Table: \n'
        string += json.dumps(self.class_table)
        string += '\n'
        string += 'Subroutine Table: \n'
        string += json.dumps(self.subroutine_table)
        return string


if __name__ == '__main__':
    st = SymbolTable()
    st.define('x', 'int', FIELD_CONSTANT)
    st.define('y', 'boolean', STATIC_CONSTANT)

    print(st)
