import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom
from SymbolTable import *
from VMWriter import *

SYMBOL_CONST = 'SYMBOL'
KEYWORD_CONST = 'KEYWORD'
INTEGER_CONST = 'INT_CONST'
STRING_CONST = 'STR_CONST'
IDENTIFIER_CONST = 'IDENTIFIER'
IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
SYMBOL = 'symbol'
STRING = 'stringConstant'
INTEGER = 'integerConstant'


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
            elif(token_type == INTEGER_CONST):
                ET.SubElement(
                    root, "integerConstant").text = self.tokenize.intVal()
            elif(token_type == STRING_CONST):
                ET.SubElement(
                    root, "stringConstant").text = self.tokenize.stringVal()
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
        xml_files = [file[:-5] + 'T.xml' for file in self.files]
        self.compiler = CompilationEngine(xml_files)
        for file in xml_files:
            print('Compiling File: ' + file)
            self.compiler.openXMLFile(file)
            self.compiler.advance()
            self.compiler.compileClass()
            self.compiler.closeFile(file[:-5] + '.xml')


class CompilationEngine:

    def __init__(self, files):
        self.classes = [file[:-5] for file in files]
        self.variables = []

    def closeFile(self, file):
        print(self.st)
        self.vm.close()
        tree = ET.ElementTree(self.root)
        tree.write(file)
        dom = xml.dom.minidom.parse(file)
        pretty_xml_as_string = dom.toprettyxml()
        f_xml = open(file, 'w')
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
        self.st = SymbolTable()
        self.vm = VMWriter(xml_file[:-5] + '.vm')

    def compileClass(self):
        self.root = ET.Element('class')
        self.add_sub_element(self.root, KEYWORD)
        if self.advance().tag == IDENTIFIER:
            self.add_sub_element(self.root, IDENTIFIER)
        if self.advance().text == '{':
            self.add_sub_element(self.root, SYMBOL)
            while True:
                self.advance()
                if self.current_token.text == 'static' or self.current_token.text == 'field':
                    class_var = ET.SubElement(self.root, 'classVarDec')
                    self.compileClassVarDec(class_var)
                else:
                    break
            while True:
                if self.current_token.text == '}':
                    self.add_sub_element(self.root, SYMBOL)
                    break
                else:
                    self.compileSubroutine()
                    self.advance()

    def compileClassVarDec(self, root):
        self.add_sub_element(root, KEYWORD)
        kind = self.current_token.text
        self.advance()
        self.add_sub_element(root, KEYWORD)
        type = self.current_token.text
        while True:
            self.advance()
            if self.current_token.tag == IDENTIFIER:
                self.add_sub_element(root, IDENTIFIER)
                name = self.current_token.text
                self.st.define(name, type, kind)
            elif self.current_token.text == ';':
                self.add_sub_element(root, SYMBOL)
                break
            # Check if there are more declarations
            elif(self.current_token.text == ','):
                self.add_sub_element(root, SYMBOL)

    def compileSubroutine(self):
        self.st.startSubroutine()
        if (self.current_token.text == 'constructor' or
            self.current_token.text == 'function' or
                self.current_token.text == 'method'):
            sub_routine = ET.SubElement(self.root, 'subroutineDec')
            self.add_sub_element(sub_routine, KEYWORD)
            self.advance()
            if self.compileType(sub_routine):
                if self.advance().tag == IDENTIFIER:
                    self.add_sub_element(sub_routine, IDENTIFIER)
                    function_name = self.current_token.text
                    if self.advance().text == '(':
                        self.add_sub_element(sub_routine, SYMBOL)
                        self.compileParameterList(sub_routine)
                        # Add Closing parenthesis
                        self.add_sub_element(sub_routine, SYMBOL)
                        if self.advance().text == '{':
                            self.compileSubroutineBody(
                                sub_routine, function_name)

    def compileSubroutineBody(self, root, function_name):
        subroutine_body = ET.SubElement(root, 'subroutineBody')
        self.add_sub_element(subroutine_body, SYMBOL)
        while True:
            self.advance()
            if self.current_token.text == 'var':
                self.compileVarDec(subroutine_body)
            else:
                break
        self.vm.writeFunction(function_name, self.st.varCount(VAR_CONSTANT))
        self.compileStatements(subroutine_body)
        self.add_sub_element(subroutine_body, SYMBOL)  # Add closing }

    def compileType(self, root):
        if self.current_token.text == 'int' or self.current_token.text == 'char' or self.current_token.text == 'boolean':
            self.add_sub_element(root, KEYWORD)
            return True
        elif self.compileClassName(root):
            return True
        elif self.current_token.text == 'void':
            self.add_sub_element(root, KEYWORD)
            return True
        return False

    def compileParameterList(self, root):
        parameter_list = ET.SubElement(root, 'parameterList')
        count_parameters = 0
        while True:
            self.advance()
            if self.current_token.tag == KEYWORD:
                self.add_sub_element(parameter_list, KEYWORD)
                type = self.current_token.text
                self.advance()
                self.add_sub_element(parameter_list, IDENTIFIER)
                name = self.current_token.text
                self.st.define(name, type, ARG_CONSTANT)
                count_parameters += 1
            elif self.current_token.text == ')':
                if not count_parameters:
                    parameter_list.text = '\n'
                return count_parameters
            elif self.current_token.text == ',':
                self.add_sub_element(parameter_list, SYMBOL)

    def compileVarName(self, root):
        if self.current_token.tag == IDENTIFIER:
            self.add_sub_element(root, IDENTIFIER)
            if self.tokens[-1].text == '[':
                self.advance()
                self.add_sub_element(root, SYMBOL)
                self.advance()
                if self.compileExpression(root):
                    if self.current_token.text == ']':
                        self.add_sub_element(root, SYMBOL)
                        return True
            return True
        return False

    def compileVarDec(self, root):
        var_dec = ET.SubElement(root, 'varDec')
        self.add_sub_element(var_dec, KEYWORD)
        self.advance()
        self.add_sub_element(var_dec, KEYWORD)  # Add type
        type = self.current_token.text
        while True:
            self.advance()
            if self.current_token.tag == IDENTIFIER:
                self.add_sub_element(var_dec, IDENTIFIER)
                name = self.current_token.text
                self.st.define(name, type, VAR_CONSTANT)

            elif self.current_token.text == ',':
                self.add_sub_element(var_dec, SYMBOL)
            elif self.current_token.text == ';':
                self.add_sub_element(var_dec, SYMBOL)
                break

    def compileStatements(self, root):
        # TODO - Run while loop here to compile statements till }
        statements = ET.SubElement(root, 'statements')
        while True:
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
            elif self.current_token.text == '}':
                break
            self.advance()

    def compileDo(self, root):
        do_statement = ET.SubElement(root, 'doStatement')
        self.add_sub_element(do_statement, KEYWORD)     # Add 'do' Keyword
        self.advance()
        self.add_sub_element(do_statement, IDENTIFIER) # Add SubroutineName or class/Var Name 
        call_function = self.current_token.text
        self.advance()
        if (self.current_token.text == '('):
            self.add_sub_element(do_statement, SYMBOL)      # Add opening (
            self.advance()
            nArgs = self.compileExpressionList(do_statement)

        else:           # .subroutineName
            self.add_sub_element(do_statement, SYMBOL)      # Add .
            self.advance()
            self.add_sub_element(do_statement, IDENTIFIER)
            call_function += ('.' + self.current_token.text)
            nArgs = self.compileExpressionList(do_statement)
        self.vm.writeCall(call_function, nArgs)

        # self.compileSubroutineCall(do_statement)
        # self.advance()
        if self.current_token.text == ';':
            self.add_sub_element(do_statement, SYMBOL)

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
                self.advance()
            if self.current_token.text == '=':
                self.add_sub_element(let_statement, SYMBOL)
                self.advance()
                self.compileExpression(let_statement)
            if self.current_token.text == ';':
                self.add_sub_element(let_statement, SYMBOL)

    def compileWhile(self, root):
        while_statement = ET.SubElement(root, 'whileStatement')
        self.add_sub_element(while_statement, KEYWORD)  # Add while keyword
        if self.advance().text == '(':
            self.add_sub_element(while_statement, SYMBOL)
            self.advance()
            if self.compileExpression(while_statement):
                # Add closing )
                self.add_sub_element(while_statement, SYMBOL)
                if self.advance().text == '{':
                    self.add_sub_element(while_statement, SYMBOL)
                    self.compileStatements(while_statement)
                    # Add closing }
                    self.add_sub_element(while_statement, SYMBOL)

    def compileReturn(self, root):
        return_statement = ET.SubElement(root, 'returnStatement')
        self.add_sub_element(return_statement, KEYWORD)  # Add do keyword
        self.advance()
        if self.current_token.text != ';':
            self.compileExpression(return_statement)
        if self.current_token.text == ';':
            self.add_sub_element(return_statement, SYMBOL)
            self.vm.writeReturn()

    def compileIf(self, root):
        if_statement = ET.SubElement(root, 'ifStatement')
        self.add_sub_element(if_statement, KEYWORD)     # Add if keyword
        if self.advance().text == '(':
            self.add_sub_element(if_statement, SYMBOL)
            self.advance()
            if self.compileExpression(if_statement):
                self.add_sub_element(if_statement, SYMBOL)      # Add closing )
                if self.advance().text == '{':
                    self.add_sub_element(if_statement, SYMBOL)
                    self.compileStatements(if_statement)
                    self.add_sub_element(if_statement, SYMBOL)  # Add closing }
                    if self.tokens[-1].text == 'else':
                        self.advance()
                        self.add_sub_element(if_statement, KEYWORD)
                        if self.advance().text == '{':
                            self.add_sub_element(if_statement, SYMBOL)
                            self.compileStatements(if_statement)
                            # Add closing }
                            self.add_sub_element(if_statement, SYMBOL)

    def compileExpression(self, root):
        expression_tag = ET.SubElement(root, 'expression')
        self.compileTerm(expression_tag)
        self.advance()
        while self.current_token.text in '+-*/&|<>=':
            operator = self.current_token
            self.advance()
            self.compileTerm(expression_tag)
            self.tokens.append(operator)
            self.advance()
            self.compileOp(expression_tag)
            self.advance()

    def compileOp(self, root):
        if (self.current_token.text == '+'):
            self.vm.writeArithmetic('add')
        elif (self.current_token.text == '-'):
            self.vm.writeArithmetic('sub')
        elif (self.current_token.text == '*'):
            self.vm.writeCall('Math.multiply', 2)
        elif (self.current_token.text == '/'):
            self.vm.writeCall('Math.divide', 2)
        elif (self.current_token.text == '|'):
            self.vm.writeArithmetic('or')
        elif (self.current_token.text == '<'):
            self.vm.writeArithmetic('lt')
        elif (self.current_token.text == '>'):
            self.vm.writeArithmetic('gt')
        elif (self.current_token.text == '='):
            self.vm.writeArithmetic('eq')

    def compileClassName(self, root):
        if self.current_token.text in self.classes:
            self.add_sub_element(root, IDENTIFIER)
            return True
        return False

    def compileStringConstant(self, root):
        if self.current_token.tag == STRING:
            self.add_sub_element(root, STRING)
            return True
        return False

    def compileTerm(self, root):
        term_statement = ET.SubElement(root, 'term')
        if self.current_token.tag == INTEGER:           # Integer Constant
            self.vm.writePush(SEGMENT_CONSTANT, self.current_token.text)
            return True
        elif self.current_token.tag == STRING:          # String Constant
            pass
            return True
        elif self.current_token.text == 'true':         # Keyword Constant
            self.vm.writePush(SEGMENT_CONSTANT, 1)
            self.vm.writeArithmetic('neg')
            return True
        elif self.current_token.text == 'false':
            self.vm.writePush(SEGMENT_CONSTANT, 0)
            return True
        elif self.current_token.text == 'null':
            self.vm.writePush(SEGMENT_CONSTANT, 0)
            return True
        elif self.current_token.text == 'this':
            self.vm.writePush(SEGMENT_POINTER, 0)
            return True
        elif self.current_token.tag == IDENTIFIER:      # var Name
            if self.tokens[-1].text == '[':
                self.advance()
                self.advance()
                self.compileExpression(term_statement)
            elif self.tokens[-1].text == '.':
                self.advance()
                self.advance()
                self.compileTerm(term_statement)
            elif self.tokens[-1].text == '(':
                self.advance()
                self.advance()
                self.compileExpressionList(term_statement)
        elif self.current_token.text == '-':            # unaryOp
            self.vm.writeArithmetic('neg')
            self.compileTerm()
        elif self.current_token.text == '~':
            self.vm.writeArithmetic('not')
            self.compileTerm()

        elif self.current_token.text == '(':            # Recurse call expression
            self.advance()
            self.compileExpression(term_statement)
        return False

    def compileExpressionList(self, root):
        expression_list = ET.SubElement(root, 'expressionList')
        count_expressions = 1
        while True:
            if self.compileExpression(expression_list):
                if self.current_token.text == ',':
                    self.add_sub_element(expression_list, SYMBOL)
                    self.advance()
                    count_expressions += 1
            else:
                if count_expressions == 0:
                    expression_list.text = '\n'
                expression_list.remove(expression_list.getchildren()[len(
                    expression_list.getchildren())-1])
                return count_expressions

    def compileSubroutineCall(self, root):
        if self.current_token.tag == IDENTIFIER:
            self.add_sub_element(root, IDENTIFIER)  # Add subroutineName
            self.advance()
            if self.current_token.text == '(':
                self.add_sub_element(root, SYMBOL)
                self.advance()
                self.compileExpressionList(root)
                self.add_sub_element(root, SYMBOL)  # Add closing )
            elif self.compileVarName(root) or self.compileClassName(root):
                self.advance()
            if self.current_token.text == '.':
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
            elif(file_line[:2] == '*/'):
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
        jack_file_data = [j for j in jack_file_data if j[:2] != '* ']
        for i in range(len(jack_file_data)):           # Remove inline comments
            if(jack_file_data[i].find('//') != -1):
                str_split = jack_file_data[i][:jack_file_data[i].find(
                    '//')].split('  ')
                # Assuming lines have atleast 2 whitespaces before comment
                jack_file_data[i] = str_split[0]
                if len(str_split) > 1 and str_split[1][:2] != '//':
                    jack_file_data[i] += str_split[1]
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
        symbol = '{}()[].,;+-*/&|<>=~'
        if(first_word in symbol):
            return SYMBOL_CONST
        elif(first_word in keyword):
            return KEYWORD_CONST
        elif(first_word[0] == '"'):
            return STRING_CONST
        elif(first_word[0] == '_' or first_word[0].isalpha()):
            return IDENTIFIER_CONST
        elif(first_word.isdigit()):
            return INTEGER_CONST

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
        if(self.tokenType() == INTEGER_CONST):
            return self.current_token

    def stringVal(self):
        if(self.tokenType() == STRING_CONST):
            temp_string = ''
            while (self.advance() != '"'):
                temp_string = ''.join([temp_string, self.current_token])
            return temp_string


if __name__ == '__main__':
    # analyzr = JackAnalyzer(sys.argv[1])
    analyzr = JackAnalyzer('Seven')
    analyzr.analyze()
    # compile = CompilationEngine()
    # compile.openXMLFile('Main.xml')
    # compile.advance()
    # compile.compileClass()
    # compile.closeFile()
