//push constant 5
@5
D=A
@SP
A=M
M=D
@SP
M=M+1
//pop local 2 
@LCL
D=M
@2
D=D+A
A=D
D=M
@SP
M=M-1
@SP
A=M
D=D+M
M=D-M
D=D-M
A=M
M=D
(INFINITE_LOOP)
@INFINITE_LOOP
0;JMP
