import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom

SYMBOL_CONST = 'SYMBOL'
KEYWORD_CONST = 'KEYWORD'
INTERGER_CONST = 'INT_CONST'
STRING_CONST = 'STR_CONST'
IDENTIFIER_CONST = 'IDENTIFIER'
IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
SYMBOL = 'symbol'
STRING = 'string'
INTEGER = 'integer'


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

    def analyze_file(self, file):
        root = ET.Element("tokens")
        while(self.tokenize.hasMoreTokens()):
            token = self.tokenize.advance()
            token_type = self.tokenize.tokenType()
            if(token_type == SYMBOL_CONST):
                ET.SubElement(root, "symbol").text = self.tokenize.symbol()
            elif(token_type == KEYWORD_CONST):
                ET.SubElement(root, "keyword").text = self.tokenize.keyWord()
            elif(token_type == INTERGER_CONST):
                ET.SubElement(root, "integer").text = self.tokenize.intVal()
            elif(token_type == STRING_CONST):
                ET.SubElement(root, "string").text = self.tokenize.stringVal()
            elif(token_type == IDENTIFIER_CONST):
                ET.SubElement(
                    root, "identifier").text = self.tokenize.identifier()
        tree = ET.ElementTree(root)
        filename = file.split('.')[0] + 'T.xml'
        tree.write(filename)
        dom = xml.dom.minidom.parse(filename)
        pretty_xml_as_string = dom.toprettyxml()
        f_xml = open(filename, 'w')
        f_xml.write(pretty_xml_as_string[pretty_xml_as_string.find('\n')+1:])
        f_xml.close()

    def analyze(self):
        self.tokenize = JackTokenizer()
        for file in self.files:
            print('Tokenizing file: ' + file)
            self.tokenize.openFile(file)
            self.analyze_file(file)
        print('Done!')


class CompilationEngine:

    def __init__(self):
        pass

    def closeFile(self):
        tree = ET.ElementTree(self.root)
        tree.write('test.xml')
        dom = xml.dom.minidom.parse('test.xml')
        pretty_xml_as_string = dom.toprettyxml()
        f_xml = open('test.xml', 'w')
        f_xml.write(pretty_xml_as_string[pretty_xml_as_string.find('\n')+1:])
        f_xml.close()

    def add_sub_element(self, root, tag):
        ET.SubElement(root, tag).text = self.current_token.text

    def hasMoreTokens(self):
        return len(self.tokens) > 0

    def advance(self):
        if(self.hasMoreTokens()):
            self.current_token = self.tokens.pop()
            return self.current_token

    def openXMLFile(self, xml_file):
        self.xml_tree = ET.parse(xml_file)
        self.tokens = list(self.xml_tree.getroot())
        self.tokens.reverse()

    def compileClass(self):
        self.root = ET.Element('class')
        self.add_sub_element(self.root, KEYWORD)
        if self.advance().tag == IDENTIFIER:
            self.add_sub_element(self.root, IDENTIFIER)
        if self.advance().text == '{':
            self.add_sub_element(self.root, SYMBOL)
            self.advance()
            if self.current_token.text == 'static' or self.current_token.text == 'field':
                self.compileClassVarDec()
            # TODO while True:
            for i in range(3):
                self.advance()
                if self.current_token.text == '}':
                    self.add_sub_element(self.root, SYMBOL)
                else:
                    self.compileSubroutine()

    def compileClassVarDec(self):
        class_var = ET.SubElement(self.root, 'classVarDec')
        self.add_sub_element(class_var, KEYWORD)
        self.advance()
        if self.compileType(class_var):
            if self.advance().tag == IDENTIFIER:
                self.add_sub_element(class_var, IDENTIFIER)
                while True:
                    if self.advance().text == ';':
                        self.add_sub_element(class_var, SYMBOL)
                        break
                    elif(self.current_token.text == ','):
                        self.add_sub_element(class_var, SYMBOL)
                        if self.advance().tag == IDENTIFIER:
                            self.add_sub_element(class_var, IDENTIFIER)

    def compileSubroutine(self):
        if (self.current_token.text == 'constructor' or
            self.current_token.text == 'function' or
                self.current_token.text == 'method'):
            sub_routine = ET.SubElement(self.root, 'subroutineDec')
            self.add_sub_element(sub_routine, KEYWORD)
            if self.advance().text == 'void' or self.compileType(sub_routine):
                self.add_sub_element(sub_routine, KEYWORD)
                if self.advance().tag == IDENTIFIER:
                    self.add_sub_element(sub_routine, IDENTIFIER)
                    if self.advance().text == '(':
                        self.add_sub_element(sub_routine, SYMBOL)
                        self.compileParameterList(sub_routine)
                        # Add Closing parenthesis
                        self.add_sub_element(sub_routine, SYMBOL)
                        if self.advance().text == '{':
                            self.compileSubroutineBody(sub_routine)
                            # ADd closing parenthesis
                            self.add_sub_element(sub_routine, SYMBOL)

    def compileSubroutineBody(self, root):
        subroutine_body = ET.SubElement(root, 'subroutineBody')
        self.add_sub_element(subroutine_body, SYMBOL)
        while True:
            self.advance()
            if self.current_token.text == 'var':
                self.compileVarDec(subroutine_body)
            elif self.compileStatements(subroutine_body):
                continue
            elif self.current_token.text == '}':
                break

    def compileType(self, root):
        # TODO Make array of filenames and compare className
        if self.current_token.text == 'int' or self.current_token.text == 'char' or self.current_token.text == 'boolean' or self.current_token.text == 'SquareGame':
            self.add_sub_element(root, KEYWORD)
            return True
        return False

    def compileParameterList(self, root):
        parameter_list = ET.SubElement(root, 'parameterList')
        count_parameters = 0
        while True:
            self.advance()
            if self.compileType(parameter_list):
                self.advance()
                if self.compileVarName(parameter_list):
                    count_parameters += 1
            elif self.current_token.text == ')':
                if not count_parameters:
                    parameter_list.text = ' '
                    break
            elif self.current_token.text == ',':
                self.add_sub_element(parameter_list, SYMBOL)

    def compileVarName(self, root):
        if self.current_token.tag == IDENTIFIER:
            self.add_sub_element(root, IDENTIFIER)
            return True
        return False

    def compileVarDec(self, root):
        var_dec = ET.SubElement(root, 'varDec')
        if self.current_token.text == 'var':
            self.add_sub_element(var_dec, KEYWORD)
            while True:
                self.advance()
                if self.compileType(var_dec):
                    self.advance()
                    if self.compileVarName(var_dec):
                        continue
                elif self.current_token.text == ',':
                    self.add_sub_element(var_dec, SYMBOL)
                elif self.current_token.text == ';':
                    self.add_sub_element(var_dec, SYMBOL)
                    break

    def compileStatements(self, root):
        # TODO - Run while loop here to compile statements till }
        statements = ET.SubElement(root, 'statements')
        if self.current_token.text == 'let':
            self.compileLet(statements)
        elif self.current_token.text == 'if':
            self.compileIf(statements)
        elif self.current_token.text == 'while':
            self.compileWhile(statements)
        elif self.current_token.text == 'do':
            self.compileDo(statements)
        elif self.current_token.text == 'return':
            self.compileReturn(statements)

    def compileDo(self, root):
        do_statement = ET.SubElement(root, 'doStatements')
        self.add_sub_element(do_statement, KEYWORD)     # Add 'do' Keyword
        self.advance()
        self.compileSubroutineCall(do_statement)
        self.advance()

    def compileLet(self, root):
        let_statement = ET.SubElement(root, 'letStatement')
        self.add_sub_element(let_statement, KEYWORD)    # Add 'let' Keyword
        self.advance()
        if self.compileVarName(let_statement):
            self.advance()
            if self.current_token.text == '[':
                self.add_sub_element(let_statement, SYMBOL)
                self.advance()
                self.compileExpression(let_statement)
                self.add_sub_element(let_statement, SYMBOL)     # Add Closing ]
            elif self.current_token.text == '=':
                self.add_sub_element(let_statement, SYMBOL)
                self.advance()
                self.compileExpression(let_statement)
            if self.advance().text == ';':
                self.add_sub_element(let_statement, SYMBOL)

    def compileWhile(self, root):
        while_statement = ET.SubElement(root, 'whileStatement')
        self.add_sub_element(while_statement, KEYWORD)  # Add while keyword
        if self.advance().text == '(':
            self.add_sub_element(while_statement, SYMBOL)
            self.advance()
            if self.compileExpression():
                self.add_sub_element(if_statement, SYMBOL)      # Add closing )
                if self.advance().text == '{':
                    self.add_sub_element(if_statement, SYMBOL)
                    self.compileStatements(if_statement)
                    self.add_sub_element(if_statement, SYMBOL)  # Add closing }

    def compileReturn(self, root):
        do_statement = ET.SubElement(root, 'doStatements)
        self.add_sub_element(do_statement, KEYWORD)  # Add do keyword
        self.advance()
        self.compileSubroutineCall(do_statement)
        if self.advance().text == ';':
            self.add_sub_element(do_statement, SYMBOL)

    def compileIf(self, root):
        if_statement = ET.SubElement(root, 'ifStatement')
        self.add_sub_element(if_statement, KEYWORD)     # Add if keyword
        if self.advance().text == '(':
            self.add_sub_element(if_statement, SYMBOL)
            self.advance()
            if self.compileExpression(root):
                self.add_sub_element(if_statement, SYMBOL)      # Add closing )
                if self.advance().text == '{':
                    self.add_sub_element(if_statement, SYMBOL)
                    self.compileStatements(if_statement)
                    self.add_sub_element(if_statement, SYMBOL)  # Add closing }
                    if self.advance().text == 'else':
                        self.add_sub_element(if_statement, KEYWORD)
                        if self.advance().text == '{':
                            self.add_sub_element(if_statement, SYMBOL)
                            self.compileStatements(if_statement)
                            # Add closing }
                            self.add_sub_element(if_statement, SYMBOL)

    def compileExpression(self, root):
        expression_tag = ET.SubElement(root, 'expression')
        self.compileTerm(expression_tag)

    def compileClassName(self, root):
        pass

    def compileUnaryOp(self, root):
        pass

    def compileIntegerConstant(self, root):
        if self.current_token.tag == INTEGER:
            self.add_sub_element(root, INTEGER)
            return True
        return False

    def compileStringConstant(self, root):
        if self.current_token.tag == STRING:
            self.add_sub_element(root, STRING)
            return True
        return False

    def compileKeywordConstant(self, root):
        if (self.current_token.text == 'true' or
            self.current_token.text == 'false' or
            self.current_token.text == 'null' or
                self.current_token.text == 'this'):
            self.add_sub_element(root, KEYWORD)
            return True
        return False

    def compileTerm(self, root):
        # TODO Add expressions
        term_statement = ET.SubElement(root, 'term')
        if (self.compileIntegerConstant(term_statement) or
            self.compileStringConstant(term_statement) or
            self.compileKeywordConstant(term_statement) or
            self.compileVarName(term_statement) or
            self.compileSubroutineCall(term_statement) or
                self.compileUnaryOp(term_statement)):

    def compileExpressionList(self):
        pass

    def compileSubroutineCall(self, root):
        if self.current_token.tag == IDENTIFIER:
            self.add_sub_element(root, IDENTIFIER)  # Add subroutineName
            self.advance()
            if self.current_token.text == '(':
                self.add_sub_element(root, SYMBOL)
                self.compileExpressionList(root)
                self.add_sub_element(root, SYMBOL)  # Add closing )
            elif self.compileVarName(root) or self.compileClassName(root):
                pass
            if self.advance().text == '.':
                self.add_sub_element(root, SYMBOL)
                if self.advance().tag == IDENTIFIER:
                    self.add_sub_element(root, IDENTIFIER)
                    if self.advance().text == '(':
                        self.add_sub_element(root, SYMBOL)
                        self.advance()
                        self.compileExpressionList(root)
                        self.add_sub_element(root, SYMBOL)  # Add closing )
                        return True
        return False



class JackTokenizer:

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
        if(len(word)):
            decomposed_str.append(word)
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
        return tokens

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
        self.tokens = self.tokenize(jack_file_data)
        self.tokens.reverse()

    def hasMoreTokens(self):
        return len(self.tokens) > 0

    def advance(self):
        if(self.hasMoreTokens()):
            self.current_token = self.tokens.pop()
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
            return self.current_token

    def symbol(self):
        if(self.tokenType() == SYMBOL_CONST):
            return self.current_token

    def identifier(self):
        if(self.tokenType() == IDENTIFIER_CONST):
            return self.current_token

    def intVal(self):
        if(self.tokenType() == INTERGER_CONST):
            return self.current_token

    def stringVal(self):
        if(self.tokenType() == STRING_CONST):
            return self.current_token


if __name__ == '__main__':
    # analyzr = JackAnalyzer(sys.argv[1])
    # analyzr.analyze()
    compile = CompilationEngine()
    compile.openXMLFile('Main.xml')
    compile.advance()
    compile.compileClass()
    compile.closeFile()
