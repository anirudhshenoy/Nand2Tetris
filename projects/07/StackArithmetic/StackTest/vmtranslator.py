import sys


class Translator:
    def __init__(self, parser, codewriter):
        self.parser = parser
        self.codewriter = codewriter

    def translate(self, filename):
        while(self.parser.hasMoreCommands()):
            command = self.parser.advance()
            self.codewriter.add_comment(command)
            command_type = self.parser.commandType()
            if (command_type == 'C_PUSH' or command_type == 'C_POP'):
                self.codewriter.writePushPop(
                    command.split()[0], self.parser.arg1(), self.parser.arg2())
            else:
                self.codewriter.writeArithmetic(command)
        self.codewriter.writeInfiniteLoop()
        self.codewriter.write_to_file(filename)


class Parser:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.read_data = f.readlines()
        self.read_data = [
            command[:-1] for command in self.read_data if command[:2] != '//' and command != '\n']
        self.read_data.reverse()
        self.current_command = None

    def hasMoreCommands(self):
        return True if len(self.read_data) else False

    def advance(self):
        if(self.hasMoreCommands()):
            self.current_command = self.read_data.pop()
            return self.current_command

    def commandType(self):
        first_word = self.current_command.split()[0]
        if(first_word == 'push'):
            return 'C_PUSH'
        elif(first_word == 'pop'):
            return 'C_POP'
        else:
            return 'C_ARITHMETIC'

    def arg1(self):
        if(self.commandType() == 'C_RETURN'):
            return
        try:
            arg1 = self.current_command.split()[1]
        except IndexError:
            arg1 = self.current_command
        finally:
            return arg1

    def arg2(self):
        if(self.commandType() == 'C_POP' or
           self.commandType() == 'C_PUSH' or
           self.commandType() == 'C_FUNCTION' or
           self.commandType() == 'C_CALL'):
            try:
                arg2 = self.current_command.split()[2]
            except IndexError:
                arg2 = self.current_command
            finally:
                return arg2


class CodeWriter:
    def __init__(self):
        self.assembly_code = []
        self.conditional_index = 0

    def writeInfiniteLoop(self):
        self.assembly_code.append('(INFINITE_LOOP)')
        self.assembly_code.append('@INFINITE_LOOP')
        self.assembly_code.append('0;JMP')
    
    def add_comment(self, comment):
        self.assembly_code.append('//' + comment)

    def writeArithmetic(self, command):
        self.assembly_code.append('@SP')    #Decrement SP
        self.assembly_code.append('M=M-1')
        self.assembly_code.append('A=M')    
        self.assembly_code.append('D=M')    #Value at SP
        if(command == 'not'):
            self.assembly_code.append('M=!D')
            self._inc_SP()
            return
        if(command == 'neg'):
            self.assembly_code.append('M=-D')
            self._inc_SP()
            return
        self.assembly_code.append('@SP')    #Decrement SP
        self.assembly_code.append('M=M-1')
        self.assembly_code.append('A=M')
        if(command == 'add'):
            self.assembly_code.append('M=M+D')
            self._inc_SP()
            return
        elif(command == 'sub'):
            self.assembly_code.append('M=M-D')
            self._inc_SP()
            return
        elif(command == 'and'):
            self.assembly_code.append('M=M&D')
            self._inc_SP()
            return
        elif(command == 'or'):
            self.assembly_code.append('M=M|D')
            self._inc_SP()
            return
        else:
            self.writeConditional(command)

    def writeConditional(self, command):
        command = command.upper()
        self.assembly_code.append('D=M-D')
        self.assembly_code.append('@IF_' + str(self.conditional_index))
        self.assembly_code.append('D;J'+command)
        self.assembly_code.append('@0')
        self.assembly_code.append('D=A')
        self._push_to_stack()
        self.assembly_code.append('@CONTINUE_' + str(self.conditional_index))
        self.assembly_code.append('0;JMP')
        self.assembly_code.append('(IF_' + str(self.conditional_index) + ')')
        self.assembly_code.append('@1')
        self.assembly_code.append('D=-A')
        self._push_to_stack()
        self.assembly_code.append('(CONTINUE_' + str(self.conditional_index) + ')')
        self._inc_SP()
        self.conditional_index += 1
        return

    def _pop_from_stack(self):
        self.assembly_code.append('@SP')
        self.assembly_code.append('A=M')
        self.assembly_code.append('D=D+M')
        self.assembly_code.append('M=D-M')
        self.assembly_code.append('D=D-M')
        self.assembly_code.append('A=M')
        self.assembly_code.append('M=D')

    def _dec_SP(self):
        self.assembly_code.append('@SP')
        self.assembly_code.append('M=M-1')

    def _push_to_stack(self):
        self.assembly_code.append('@SP')
        self.assembly_code.append('A=M')
        self.assembly_code.append('M=D')

    def _inc_SP(self):
        self.assembly_code.append('@SP')
        self.assembly_code.append('M=M+1')

    def writePushPop(self, command, segment, index):
        if(segment == 'constant'):
            self.assembly_code.append('@' + index)
            self.assembly_code.append('D=A')
        else:
            self.assembly_code.append('@' + segment)
            self.assembly_code.append('D=A')
            self.assembly_code.append('@' + index)
            self.assembly_code.append('D=D+A')
        if(command == 'push'):
            self._push_to_stack()
            self._inc_SP()
        else:
            self._pop_from_stack()
            self._dec_SP()

    def write_to_file(self, filename):
        with open(filename + '.asm', 'w') as f:
            for line in self.assembly_code:
                f.write("%s\n" % line)


if __name__ == "__main__":
    t = Translator(Parser(sys.argv[1]), CodeWriter())
    t.translate(sys.argv[2])
