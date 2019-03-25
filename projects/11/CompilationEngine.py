class CompilationEngine:

    def __init__(self, files):
        self.classes = [file[:-5] for file in files]
        self.variables = []

    def closeFile(self, file):
        print(self.st)
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
        self.vm = VMWriter(xml_file[-3] + '.vm')

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
                            self.compileSubroutineBody(sub_routine, function_name)

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
            name = self.current_token.text
            self.add_sub_element(root, 'USED' + self.st.kindOf(name) + str(self.st.indexOf(name))) 
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
        self.add_sub_element(do_statement, IDENTIFIER)  # Add SubroutineName
        self.advance()
        self.add_sub_element(do_statement, SYMBOL)      # Add opening (
        self.advance()
        self.compileExpression(do_statement)
        
        #self.compileSubroutineCall(do_statement)
        #self.advance()
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
        if self.compileTerm(expression_tag):
            while True:
                self.advance()
                if self.compileOp(expression_tag):
                    self.advance()
                    self.compileTerm(expression_tag)
                else:
                    break
            return True
        return False

    def compileOp(self, root):
        if (self.current_token.text == '+' or
            self.current_token.text == '-' or
            self.current_token.text == '*' or
            self.current_token.text == '/' or
            self.current_token.text == '&' or
            self.current_token.text == '|' or
            self.current_token.text == '<' or
            self.current_token.text == '>' or
                self.current_token.text == '='):
            self.add_sub_element(root, SYMBOL)
            return True
        return False

    def compileClassName(self, root):
        if self.current_token.text in self.classes:
            self.add_sub_element(root, IDENTIFIER)
            return True
        return False

    def compileUnaryOp(self, root):
        if (self.current_token.text == '-' or
                self.current_token.text == '~'):
            self.add_sub_element(root, SYMBOL)
            self.advance()
            if self.compileTerm(root):
                return True
        return False

    def compileIntegerConstant(self, root):
        if self.current_token.tag == INTEGER:
            self.vm.writePush(SEGMENT_CONSTANT, self.current_token.text)
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
        if self.tokens[-1].text != '.':
            if (self.compileIntegerConstant(term_statement) or
                self.compileStringConstant(term_statement) or
                self.compileKeywordConstant(term_statement) or
                self.compileVarName(term_statement) or
                self.compileSubroutineCall(term_statement) or
                    self.compileUnaryOp(term_statement)):
                return True
            elif self.current_token.text == '(':
                self.add_sub_element(term_statement, SYMBOL)
                self.advance()
                if self.compileExpression(term_statement):
                    self.add_sub_element(term_statement, SYMBOL)
                    return True
        else:
            self.compileSubroutineCall(term_statement)
            return True
        return False

    def compileExpressionList(self, root):
        expression_list = ET.SubElement(root, 'expressionList')
        count_expressions = 0
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

class CompilationEngine:

    def __init__(self, files):
        self.classes = [file[:-5] for file in files]
        self.variables = []

    def closeFile(self, file):
        print(self.st)
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
        self.vm = VMWriter(xml_file[-3] + '.vm')

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
                            self.compileSubroutineBody(sub_routine, function_name)

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
            name = self.current_token.text
            self.add_sub_element(root, 'USED' + self.st.kindOf(name) + str(self.st.indexOf(name))) 
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
        self.add_sub_element(do_statement, IDENTIFIER)  # Add SubroutineName
        self.advance()
        self.add_sub_element(do_statement, SYMBOL)      # Add opening (
        self.advance()
        self.compileExpression(do_statement)
        
        #self.compileSubroutineCall(do_statement)
        #self.advance()
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
        if self.compileTerm(expression_tag):
            while True:
                self.advance()
                if self.compileOp(expression_tag):
                    self.advance()
                    self.compileTerm(expression_tag)
                else:
                    break
            return True
        return False

    def compileOp(self, root):
        if (self.current_token.text == '+' or
            self.current_token.text == '-' or
            self.current_token.text == '*' or
            self.current_token.text == '/' or
            self.current_token.text == '&' or
            self.current_token.text == '|' or
            self.current_token.text == '<' or
            self.current_token.text == '>' or
                self.current_token.text == '='):
            self.add_sub_element(root, SYMBOL)
            return True
        return False

    def compileClassName(self, root):
        if self.current_token.text in self.classes:
            self.add_sub_element(root, IDENTIFIER)
            return True
        return False

    def compileUnaryOp(self, root):
        if (self.current_token.text == '-' or
                self.current_token.text == '~'):
            self.add_sub_element(root, SYMBOL)
            self.advance()
            if self.compileTerm(root):
                return True
        return False

    def compileIntegerConstant(self, root):
        if self.current_token.tag == INTEGER:
            self.vm.writePush(SEGMENT_CONSTANT, self.current_token.text)
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
        if self.tokens[-1].text != '.':
            if (self.compileIntegerConstant(term_statement) or
                self.compileStringConstant(term_statement) or
                self.compileKeywordConstant(term_statement) or
                self.compileVarName(term_statement) or
                self.compileSubroutineCall(term_statement) or
                    self.compileUnaryOp(term_statement)):
                return True
            elif self.current_token.text == '(':
                self.add_sub_element(term_statement, SYMBOL)
                self.advance()
                if self.compileExpression(term_statement):
                    self.add_sub_element(term_statement, SYMBOL)
                    return True
        else:
            self.compileSubroutineCall(term_statement)
            return True
        return False

    def compileExpressionList(self, root):
        expression_list = ET.SubElement(root, 'expressionList')
        count_expressions = 0
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

