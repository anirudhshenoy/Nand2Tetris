import sys


class Translator:
    def __init__(self, filename):
        self.filename = filename
        self.parser = Parser(filename)
        self.f_asm = open(filename[:-3] + '.asm', 'w')
        self.codewriter = CodeWriter(filename, self.f_asm)

    def translate(self):
        while(self.parser.hasMoreCommands()):
            command = self.parser.advance()
            self.codewriter.add_comment(command)
            command_type = self.parser.commandType()
            if (command_type == 'C_PUSH' or command_type == 'C_POP'):
                self.codewriter.writePushPop(
                    command.split()[0], self.parser.arg1(), self.parser.arg2())
            elif (command_type == 'C_GOTO'):
                self.codewriter.writeGoTo(self.parser.arg1())
            elif (command_type == 'C_LABEL'):
                self.codewriter.writeLabel(self.parser.arg1())
            elif (command_type == 'C_FUNCTION'):
                self.codewriter.writeFunction(
                    self.parser.arg1(), self.parser.arg2())
            elif (command_type == 'C_IF'):
                self.codewriter.writeIf(self.parser.arg1())
            elif (command_type == 'C_RETURN'):
                self.codewriter.writeReturn()
            else:
                self.codewriter.writeArithmetic(command)
        self.codewriter.writeInfiniteLoop()
        self.codewriter.closeFile()


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
        commandtype_lookup = {
            'push': 'C_PUSH',
            'pop': 'C_POP',
            'function': 'C_FUNCTION',
            'goto': 'C_GOTO',
            'label': 'C_LABEL',
            'if-goto': 'C_IF',
            'return': 'C_RETURN',
            'call': 'C_CALL'
        }
        return commandtype_lookup.get(first_word, 'C_ARITHMETIC')

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
    def __init__(self, filename, f_asm):
        self.conditional_index = 0  # Used to create Labels for conditional jumps
        self.filename = filename[:-3]
        self.f_asm = f_asm

    def set_file_name(self, filename):
        self.filename = filename

    def writeFunction(self, label, nargs):
        self.writeLabel(label)
        self.write_command_to_file('@' + nargs)
        self.write_command_to_file('D=A')
        self.write_command_to_file('@SP')
        self.write_command_to_file('D=M+D')
        self.write_command_to_file('M=D')

    def writeReturn(self):
        # TODO : *ARG = pop() done  
        self.write_command_to_file('@LCL')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@R14')
        self.write_command_to_file('M=D')
        self.write_command_to_file('@ARG')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=A')
        self._dec_SP()
        self._pop_from_stack()
        self.write_command_to_file('@ARG')
        self.write_command_to_file('D=M+1')
        self.write_command_to_file('@SP')
        self.write_command_to_file('M=D')
        self.write_command_to_file('@R14')
        self.write_command_to_file('M=M-1')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@THAT')
        self.write_command_to_file('M=D')
        self.write_command_to_file('@R14')
        self.write_command_to_file('M=M-1')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@THIS')
        self.write_command_to_file('M=D')
        self.write_command_to_file('@R14')
        self.write_command_to_file('M=M-1')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@ARG')
        self.write_command_to_file('M=D')
        self.write_command_to_file('@R14')
        self.write_command_to_file('M=M-1')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@LCL')
        self.write_command_to_file('M=D')

    def writeLabel(self, label):
        self.write_command_to_file('(' + label + ')')

    def writeGoTo(self, label):
        self.write_command_to_file('@' + label)
        self.write_command_to_file('0; JMP')

    def writeIf(self, label):
        self._dec_SP()
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')
        self.write_command_to_file('@' + label)
        self.write_command_to_file('D; JGT')

    def writeInfiniteLoop(self):
        self.write_command_to_file('(INFINITE_LOOP)')
        self.write_command_to_file('@INFINITE_LOOP')
        self.write_command_to_file('0;JMP')

    def add_comment(self, comment):
        self.write_command_to_file('//' + comment)

    def writeArithmetic(self, command):
        # Move the first operand to the D register
        self._dec_SP()
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=M')  # Value at SP
        if(command == 'not'):
            self.write_command_to_file('M=!D')
            self._inc_SP()
            return
        if(command == 'neg'):
            self.write_command_to_file('M=-D')
            self._inc_SP()
            return
        # Following commands require 2 operands, so we extract the previous element
        self._dec_SP()
        # Get the address of the 2nd operand
        self.write_command_to_file('A=M')
        if(command == 'add'):
            self.write_command_to_file('M=M+D')
            self._inc_SP()
            return
        elif(command == 'sub'):
            self.write_command_to_file('M=M-D')
            self._inc_SP()
            return
        elif(command == 'and'):
            self.write_command_to_file('M=M&D')
            self._inc_SP()
            return
        elif(command == 'or'):
            self.write_command_to_file('M=M|D')
            self._inc_SP()
            return
        else:
            self.writeConditional(command)

    def writeConditional(self, command):
        command = command.upper()
        self.write_command_to_file('D=M-D')
        self.write_command_to_file('@IF_' + str(self.conditional_index))
        self.write_command_to_file('D;J'+command)
        self.write_command_to_file('@0')  # Set False Flag
        self.write_command_to_file('D=A')
        self._push_to_stack()
        self.write_command_to_file('@CONTINUE_' + str(self.conditional_index))
        self.write_command_to_file('0;JMP')
        self.write_command_to_file('(IF_' + str(self.conditional_index) + ')')
        self.write_command_to_file('@1')  # Set True Flag,
        self.write_command_to_file('D=-A')  # true flag is -1
        self._push_to_stack()
        self.write_command_to_file(      # Resume execution from here
            '(CONTINUE_' + str(self.conditional_index) + ')')
        self._inc_SP()
        self.conditional_index += 1
        return

    def _pop_from_stack(self):
        # Ensure Address to pop to is set in D Register
        self.write_command_to_file('@SP')
        self.write_command_to_file('A=M')
        self.write_command_to_file('D=D+M')
        self.write_command_to_file('M=D-M')
        self.write_command_to_file('D=D-M')
        self.write_command_to_file('A=M')
        self.write_command_to_file('M=D')

    def _dec_SP(self):
        self.write_command_to_file('@SP')
        self.write_command_to_file('M=M-1')

    def _push_to_stack(self):
        self.write_command_to_file('@SP')
        self.write_command_to_file('A=M')
        self.write_command_to_file('M=D')

    def _inc_SP(self):
        self.write_command_to_file('@SP')
        self.write_command_to_file('M=M+1')

    def _get_address(self, segment, index):
        if(segment == 'constant'):
            return index
        elif(segment == 'static'):
            # TODO static variable should be filename.Index
            return self.filename + str(index)
        elif(segment == 'temp'):
            return str(int(index)+5)
        elif(segment == 'pointer'):
            if(index == '1'):
                return 'THAT'
            else:
                return 'THIS'
        else:
            return self._get_segment_shorthand(segment)

    def _write_push_commands(self, segment, index):
        if(segment == 'constant'):
            self.write_command_to_file('D=A')
        elif(segment == 'static' or segment == 'temp' or segment == 'pointer'):
            self.write_command_to_file('D=M')
        else:
            self.write_command_to_file('D=M')
            self.write_command_to_file('@' + index)
            self.write_command_to_file('D=D+A')
            self.write_command_to_file('A=D')
            self.write_command_to_file('D=M')

    def _write_pop_commands(self, segment, index):
        if(segment == 'static' or segment == 'temp' or segment == 'pointer'):
            self.write_command_to_file('D=A')
        else:
            self.write_command_to_file('D=M')
            self.write_command_to_file('@' + index)
            self.write_command_to_file('D=D+A')

    def writePushPop(self, command, segment, index):
        self.write_command_to_file('@' + self._get_address(segment, index))
        if(command == 'push'):
            self._write_push_commands(segment, index)
            self._push_to_stack()
            self._inc_SP()
        elif(command == 'pop'):
            self._write_pop_commands(segment, index)
            self._dec_SP()
            self._pop_from_stack()

    def _get_segment_shorthand(self, segment):
        segment_shorthand = {
            'this': 'THIS',
            'that': 'THAT',
            'local': 'LCL',
            'argument': 'ARG',
        }
        return segment_shorthand.get(segment)

    def write_command_to_file(self, command):
        self.f_asm.write(command + '\n')

    def closeFile(self):
        self.f_asm.close()


if __name__ == "__main__":
    t = Translator(sys.argv[1])
    t.translate()
