@7
D=A
@SP
A=M
M=D
@SP
M=M+1
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@IF_0
D;JEQ
@0
D=A
@SP
A=M
M=D
@CONTINUE_0
0;JMP
(IF_0)
@32767
D=A
@SP
A=M
M=D
(CONTINUE_0)
@SP
M=M+1
