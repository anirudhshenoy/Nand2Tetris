//push constant 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
//pop static 8
@StaticTest8
D=A
@SP
M=M-1
@SP
A=M
D=D+M
M=D-M
D=D-M
A=M
M=D
//pop static 3
@StaticTest3
D=A
@SP
M=M-1
@SP
A=M
D=D+M
M=D-M
D=D-M
A=M
M=D
//pop static 1
@StaticTest1
D=A
@SP
M=M-1
@SP
A=M
D=D+M
M=D-M
D=D-M
A=M
M=D
//push static 3
@StaticTest3
D=M
@SP
A=M
M=D
@SP
M=M+1
//push static 1
@StaticTest1
D=M
@SP
A=M
M=D
@SP
M=M+1
//sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
//push static 8
@StaticTest8
D=M
@SP
A=M
M=D
@SP
M=M+1
//add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
(INFINITE_LOOP)
@INFINITE_LOOP
0;JMP