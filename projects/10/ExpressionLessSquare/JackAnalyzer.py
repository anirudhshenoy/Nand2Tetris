import os
import sys
import re


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

    # Split string into symbols and alphanumeric word
    @staticmethod
    def decompose_string(str):
        decomposed_str = []
        word = ''
        for s in str:
            if(s.isalnum()):
                word = ''.join([word, s])
            else:
                if(len(word)):
                    decomposed_str.append(word)
                decomposed_str.append(s)
                word = ''
        return decomposed_str

    @staticmethod
    def remove_multiline_comments(file_line):
        if(len(file_line)):
            if(file_line[0] == '/'):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def tokenize(lines):
        tokens = []
        for line in lines:
            for l in line.split():
                if(not l.isalnum()):
                    for s in JackTokenizer.decompose_string(l):
                        tokens.append(s)
                else:
                    tokens.append(l)
        print(tokens)

    def openFile(self, filename):
        # TODO - Does regex make this easier?
        with open(filename, 'r') as f:
            jack_file_data = f.readlines()
        jack_file_data = [j.strip() for j in jack_file_data]
        for i in range(len(jack_file_data)):           # Remove inline comments
            if(jack_file_data[i].find('//') != -1):
                jack_file_data[i] = jack_file_data[i][:jack_file_data[i].find(
                    '//')].split('  ')[0]           # Assuming lines have atleast 2 whitespaces before comment
        jack_file_data = list(filter(
            self.remove_multiline_comments, jack_file_data))
        print(jack_file_data)
        self.tokenize(jack_file_data)
        # self.jack_file_data.reverse()

    def hasMoreTokens(self):
        return len(self.jack_file_data) > 0

    def advance(self):
        if(self.hasMoreTokens()):
            self.current_token = self.jack_file_data.pop()
            return self.current_token

    def tokenType(self):
        first_word = self.current_token.split()[0]
        keyword = ['class', 'constructor', 'function', 'method', 'field',
                   'static', 'var', 'int', 'char', 'boolean',
                   'void', 'true', 'false', 'null', 'this', 'let', 'do',
                   'if', 'else', 'while', 'return']
        symbol = '{}()[].,;+-*/&|,.=~'
        if(first_word in symbol):
            return SYMBOL_CONST
        elif(first_word in keyword):
            return KEYWORD_CONST
        elif(first_word[0] == '"'):
            return STR_CONST
        elif(first_word[0] == '_' or first_word[0].isalpha()):
            return IDENTIFIER_CONST
        elif(first_word.isdigit()):
            return INT_CONST

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
