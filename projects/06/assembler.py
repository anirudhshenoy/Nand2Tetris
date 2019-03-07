import sys


class Assembler:
    def __init__(self, parser, code, symboltable):
        self.parser = parser
        self.code = code
        self.symboltable = symboltable
        self.byte_code = []

    def first_pass(self, filename):
        self.parser.load_file(filename)
        address = 0
        while(self.parser.hasMoreCommands()):
            command = self.parser.advance()
            command_type = self.parser.commandType()
            if(command_type == 'L_COMMAND'):
                self.symboltable.add_entry(
                    self.parser.symbol(), pad_to_n_bit(address, 15))
            else:
                address += 1
        # print(self.symboltable.table)

    def get_a_command_int(self, symbol):
        a_command_symbol = self.parser.symbol()
        try:
            a_command_int = int(a_command_symbol)
        except ValueError:
            if(self.symboltable.contains(symbol)):
                return self.symboltable.get_address(symbol)
            self.symboltable.add_new_variable(symbol)
            return self.symboltable.get_address(symbol)
        return pad_to_n_bit(a_command_int, 15)

    def assemble(self, filename):
        self.first_pass(filename)
        self.parser.load_file(filename)
        while(self.parser.hasMoreCommands()):
            command = self.parser.advance()
            command_type = self.parser.commandType()
            if(command_type == 'A_COMMAND'):
                self.byte_code.append('0' +
                                      self.get_a_command_int(self.parser.symbol()))
            elif(command_type == 'L_COMMAND'):
                pass
            else:
                dest = self.parser.dest()
                comp = self.parser.comp()
                jump = self.parser.jump()
                c_command = ''.join(['111', self.code.comp(
                    comp), self.code.dest(dest), self.code.jump(jump)])
                self.byte_code.append(c_command)
        # print(self.byte_code)
        with open(filename[:-3] + 'hack', 'w') as f:
            for line in self.byte_code:
                f.write("%s\n" % line)


class Parser:
    def load_file(self, filename):
        with open(filename, 'r') as f:
            self.read_data = f.readlines()
        self.read_data = [
            command[:-1].split()[0] for command in self.read_data if command[:2] != '//' and
            command[:2] != '\n']
        self.read_data.reverse()
        self.current_command = None

    def get_code_list(self):
        return self.read_data

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
            return self.current_command[
                self.current_command.find('='):self.current_command.find(';')+1]

    def jump(self):
        if(self.commandType() == 'C_COMMAND'):
            if(self.current_command.find(';') == -1):
                return 'null'
            return self.current_command[self.current_command.find(';')+1:]


class SymbolTable:
    def __init__(self):
        self.table = {
            'SP': '000000000000000',
            'LCL': '000000000000001',
            'ARG': '000000000000010',
            'THIS': '000000000000011',
            'THAT': '000000000000100',
            'R0': '000000000000000',
            'R1': '000000000000001',
            'R2': '000000000000010',
            'R3': '000000000000011',
            'R4': '000000000000100',
            'R5': '000000000000101',
            'R6': '000000000000110',
            'R7': '000000000000111',
            'R8': '000000000001000',
            'R9': '000000000001001',
            'R10': '000000000001010',
            'R11': '000000000001011',
            'R12': '000000000001100',
            'R13': '000000000001101',
            'R14': '000000000001110',
            'R15': '000000000001111',
            'SCREEN': '100000000000000',
            'KBD': '110000000000000',
        }
        self.next_available_address = 16

    def add_new_variable(self, symbol):
        address = pad_to_n_bit(self.next_available_address, 15)
        self.add_entry(symbol, address)
        self.next_available_address += 1

    def add_entry(self, symbol, address):
        self.table.update({
            symbol: address
        })

    def contains(self, symbol):
        try:
            address = self.table[symbol]
        except:
            address = 0
        finally:
            return True if address else False

    def get_address(self, symbol):
        if(self.contains(symbol)):
            return self.table[symbol]


class Code:

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


def pad_to_n_bit(integer, n):
    address = bin(integer)[2:]
    return ''.join(['0'*(n - len(address)), address])


if __name__ == '__main__':
    assembler = Assembler(Parser(), Code(), SymbolTable())
    assembler.assemble(sys.argv[1])
