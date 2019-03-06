import sys


class Assembler:
    def __init__(self, parser, code):
        self.parser = parser
        self.code = code
        self.byte_code = []

    def assemble(self, filename):
        self.parser.load_file(filename)
        while(self.parser.hasMoreCommands()):
            command = self.parser.advance()
            print(command)
            command_type = self.parser.commandType()
            if(command_type == 'A_COMMAND'):
                self.byte_code.append(self.code.a_code(self.parser.symbol()))
            elif(command_type == 'L_COMMAND'):
                pass
            else:
                dest = self.parser.dest()
                comp = self.parser.comp()
                jump = self.parser.jump()
                print(dest)
                print(comp)
                print(jump)
                c_command = ''.join(['111', self.code.comp(
                    comp), self.code.dest(dest), self.code.jump(jump)])
                self.byte_code.append(c_command)
        print(self.byte_code)
        with open(filename[:-3] + 'hack', 'w') as f:
            for line in self.byte_code:
                f.write("%s\n" % line)

class Parser:
    def load_file(self, filename):
        with open(filename, 'r') as f:
            self.read_data = f.readlines()
        self.read_data = [
            command[:-1] for command in self.read_data if command[:2] != '//' and command[:2] != '\n']
        self.read_data.reverse()
        self.current_command = None

    def advance(self):
        if(self.hasMoreCommands()):
            self.current_command = self.read_data.pop()
            return self.current_command

    def hasMoreCommands(self):
        return True if len(self.read_data) else False

    def commandType(self):
        first_character = self.current_command[0]
        if(first_character == '@'):
            return 'A_COMMAND'
        elif(first_character == '('):
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def symbol(self):
        if(self.commandType() == 'A_COMMAND' or self.commandType() == 'L_COMMAND'):
            if(self.current_command[-1] == ')'):
                return self.current_command[1:-1]
            else:
                return self.current_command[1:]

    def dest(self):
        if(self.commandType() == 'C_COMMAND'):
            if(self.current_command.find('=') == -1):
                return 'null'
            return self.current_command[:self.current_command.find('=')]

    def comp(self):
        if(self.commandType() == 'C_COMMAND'):
            if(self.current_command.find(';') == -1):
                return self.current_command[self.current_command.find('=')+1:]
            elif(self.current_command.find('=') == -1):
                return self.current_command[:self.current_command.find(';')]
            return self.current_command[self.current_command.find('='):self.current_command.find(';')+1]

    def jump(self):
        if(self.commandType() == 'C_COMMAND'):
            if(self.current_command.find(';') == -1):
                return 'null'
            return self.current_command[self.current_command.find(';')+1:]


class Code:
    def a_code(self, decimal):
        a = bin(int(decimal))[2:]
        return ''.join(['0'*(16-len(a)), a])

    def dest(self, mnemonic):
        bits = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        return bits.get(mnemonic)

    def comp(self, mnemonic):
        bits = {
            '0': '101010',
            '1': '111111',
            '-1': '111010',
            'D': '001100',
            'A': '110000',
            '!D': '001101',
            '!A': '110001',
            '-D': '001111',
            '-A': '110011',
            'D+1': '011111',
            'A+1': '110111',
            'D-1': '001110',
            'A-1': '110010',
            'D+A': '000010',
            'D-A': '010011',
            'A-D': '000111',
            'D&A': '000000',
            'D|A': '010101',
        }
        a = '1' if(mnemonic.find('M')) != -1 else '0'
        if(a):
            mnemonic = mnemonic.replace('M', 'A')
        return ''.join([a, bits.get(mnemonic)])

    def jump(self, mnemonic):
        bits = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
        return bits.get(mnemonic)


if __name__ == '__main__':
    assembler = Assembler(Parser(), Code())
    assembler.assemble(sys.argv[1])
