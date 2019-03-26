import json

STATIC_CONSTANT = 'static'
FIELD_CONSTANT = 'field'
ARG_CONSTANT = 'arg'
VAR_CONSTANT = 'var'


class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.inSubroutine = False
        self.class_index = {
            STATIC_CONSTANT: 0,
            FIELD_CONSTANT: 0
        }

    def startSubroutine(self):
        self.inSubroutine = True
        self.subroutine_table = {}
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
        if(kind == VAR_CONSTANT or kind == ARG_CONSTANT):
            return self.subroutine_index.get(kind)
        else:
            return self.class_index.get(kind)

    def kindOf(self, name):
        kind = None
        try:
            kind = self.subroutine_table[name].get('kind')
        except:
            kind = self.class_table[name].get('kind')
        finally:
            return kind

    def typeOf(self, name):
        obj_type = None
        try:
            obj_type = self.subroutine_table[name].get('type')
        except:
            obj_type = self.class_table[name].get('type')
        finally:
            return obj_type

    def indexOf(self, name):
        index = None
        try:
            index = self.subroutine_table[name].get('index')
        except:
            index = self.class_table[name].get('index')
        finally:
            return index

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
