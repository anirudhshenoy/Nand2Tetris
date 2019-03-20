import os
import sys


class JackAnalyzer:
    def __init__(self, projectname):
        self.retrieve_filenames(projectname)

    def retrieve_filenames(self, projectname):
        if(os.path.isdir(projectname)):
            os.chdir(projectname)
            self.files = [file for file in os.listdir()
                          if file.endswith('.jack')]
        elif(os.path.isfile(projectname + '.jack')):
            self.files = [projectname + '.jack']
        else:
            raise Exception('Invalid Directory or Filename')

    def analyze_file(self):
        pass

    def analyze(self):
        self.tokenize = JackTokenizer()
        for file in self.files:
            self.tokenize.openFile(file)
            self.f_xml = open(file.split('.')[0]+'.xml', 'w')
            self.tokenize.set_xml_file(self.f_xml)
            self.analyze_file()


class JackTokenizer:

    SYMBOL_CONST = 'SYMBOL'
    KEYWORD_CONST = 'KEYWORD'
    INTERGER_CONST = 'INT_CONST'
    STRING_CONST = 'STR_CONST'
    IDENTIFIER_CONST = 'IDENTIFIER'

    def set_xml_file(self, xml_filename):
        self.f_xml = xml_filename

    @staticmethod
    def remove_multiline_comments(file_line):
        if(len(file_line)):
            if(file_line[0] == '/'):
                return False
            else:
                return True
        else:
            return False

    def openFile(self, filename):
        # TODO - Does regex make this easier?
        with open(filename, 'r') as f:
            self.jack_file_data = f.readlines()
        self.jack_file_data = [j.strip() for j in self.jack_file_data]
        for i in range(len(self.jack_file_data)):           # Remove inline comments
            if(self.jack_file_data[i].find('//') != -1):
                self.jack_file_data[i] = self.jack_file_data[i][:self.jack_file_data[i].find(
                    '//')].split('  ')[0]           # Assuming lines have atleast 2 whitespaces before comment
        self.jack_file_data = list(filter(
            self.remove_multiline_comments, self.jack_file_data))
        print(self.jack_file_data)
        self.jack_file_data.reverse()

    def hasMoreTokens(self):
        return len(self.jack_file_data) > 0

    def advance(self):
        if(self.hasMoreTokens()):
            self.current_token = self.jack_file_data.pop()
            return self.current_token

    def tokenType(self):
        # List for keyword
        keyword = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 
                    'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
        symbol = '{}()[].,;+-*/&|,.=~'
        if(self.current_token in symbol):
            return 'SYMBOL'
        token_lookup = {}
        pass

    def keyWord(self):
        if(self.tokenType() == KEYWORD_CONST):
            pass

    def symbol(self):
        if(self.tokenType() == SYMBOL_CONST):
            pass

    def identifier(self):
        if(self.tokenType() == IDENTIFIER_CONST):
            pass

    def intVal(self):
        if(self.tokenType() == INTERGER_CONST):
            pass

    def stringVal(self):
        if(self.tokenType() == STRING_CONST):
            pass


if __name__ == '__main__':
    analyzr = JackAnalyzer(sys.argv[1])
    analyzr.analyze()
