SEGMENT_CONSTANT = 'constant'
SEGMENT_TEMP = 'temp'
SEGMENT_POINTER = 'pointer'
SEGMENT_LOCAL = 'local'
SEGMENT_ARGUMENT = 'argument'
SEGMENT_STATIC = 'static'
SEGMENT_THAT = 'that'

LOOP_LABEL = 'LOOP_'
EXIT_LABEL = 'EXIT_'
IF_LABEL = 'IF_'
ELSE_LABEL = 'ELSE_'


class VMWriter:
    def __init__(self, filename):
        self.current_class = filename[:-3]
        self.f_vm = open(filename, 'w')

    def writePush(self, segment, index):
        self.f_vm.write('push ' + segment + ' ' + str(index) + '\n')

    def writePop(self, segment, index):
        self.f_vm.write('pop ' + segment + ' ' + str(index) + '\n')

    def writeArithmetic(self, command):
        self.f_vm.write(command + '\n')

    def writeLabel(self, label):
        self.f_vm.write('label ' + label + '\n')

    def writeGoto(self, label):
        self.f_vm.write('goto ' + label + '\n')

    def writeIf(self, label):
        self.f_vm.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self.f_vm.write('call ' + name + ' ' + str(nArgs) + '\n')
        #self.writePop(SEGMENT_TEMP, 0)

    def writeFunction(self, name, nLocals):
        self.f_vm.write('function ' + self.current_class +
                        '.' + name + ' ' + str(nLocals) + '\n')

    def writeReturn(self):
        self.f_vm.write('return' + '\n')
        pass

    def close(self):
        self.f_vm.close()
