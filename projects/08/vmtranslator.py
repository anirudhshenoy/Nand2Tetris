import sys


class Translator:
    def __init__(self, parser, codewriter):
        self.parser = parser
        self.codewriter = codewriter

    def translate(self):
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
        self.codewriter.write_to_file()


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
            'if': 'C_IF',
            'return': 'C_RETURN'
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
    def __init__(self, filename):
        self.assembly_code = []
        self.conditional_index = 0  # Used to create Labels for conditional jumps
        self.filename = filename[:-3]

    def set_file_name(self, filename):
        self.filename = filename

    def writeLabel(self, label):
        self.assembly_code.append('(' +label + ')')

    def writeGoTo(self, label):
        self.assembly_code.append('@' + label)
        self.assembly_code.append('0; JMP')
    
    def writeIf(self, label):
        self._dec_SP()
        self.assembly_code.append('@SP')
        #TODO complete implmentation
        pass
    
    def writeInfiniteLoop(self):
        self.assembly_code.append('(INFINITE_LOOP)')
        self.assembly_code.append('@INFINITE_LOOP')
        self.assembly_code.append('0;JMP')

    def add_comment(self, comment):
        self.assembly_code.append('//' + comment)

    def writeArithmetic(self, command):
        # Move the first operand to the D register
        self._dec_SP()
        self.assembly_code.append('A=M')
        self.assembly_code.append('D=M')  # Value at SP
        if(command == 'not'):
            self.assembly_code.append('M=!D')
            self._inc_SP()
            return
        if(command == 'neg'):
            self.assembly_code.append('M=-D')
            self._inc_SP()
            return
        # Following commands require 2 operands, so we extract the previous element
        self._dec_SP()
        # Get the address of the 2nd operand
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
        self.assembly_code.append('@0')  # Set False Flag
        self.assembly_code.append('D=A')
        self._push_to_stack()
        self.assembly_code.append('@CONTINUE_' + str(self.conditional_index))
        self.assembly_code.append('0;JMP')
        self.assembly_code.append('(IF_' + str(self.conditional_index) + ')')
        self.assembly_code.append('@1')  # Set True Flag,
        self.assembly_code.append('D=-A')  # true flag is -1
        self._push_to_stack()
        self.assembly_code.append(      # Resume execution from here
            '(CONTINUE_' + str(self.conditional_index) + ')')
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
            self.assembly_code.append('D=A')
        elif(segment == 'static' or segment == 'temp' or segment == 'pointer'):
            self.assembly_code.append('D=M')
        else:
            self.assembly_code.append('D=M')
            self.assembly_code.append('@' + index)
            self.assembly_code.append('D=D+A')
            self.assembly_code.append('A=D')
            self.assembly_code.append('D=M')

    def _write_pop_commands(self, segment, index):
        if(segment == 'static' or segment == 'temp' or segment == 'pointer'):
            self.assembly_code.append('D=A')
        else:
            self.assembly_code.append('D=M')
            self.assembly_code.append('@' + index)
            self.assembly_code.append('D=D+A')

    def writePushPop(self, command, segment, index):
        self.assembly_code.append('@' + self._get_address(segment, index))
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

    def write_to_file(self):
        with open(self.filename + '.asm', 'w') as f:
            for line in self.assembly_code:
                f.write("%s\n" % line)


if __name__ == "__main__":
    t = Translator(Parser(sys.argv[1]), CodeWriter(sys.argv[1]))
    t.translate()
