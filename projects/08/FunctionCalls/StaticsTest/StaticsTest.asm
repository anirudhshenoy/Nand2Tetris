@256
D=A
@SP
M=D
@RET_ADDR_Sys.init0
M=A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@Sys.init
0; JMP
(RET_ADDR_Sys.init0)
//function Sys.init 0
(Sys.init)
//push constant 6
@6
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 8
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
//call Class1.set 2
@RET_ADDR_Class1.set1
M=A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@7
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Class1.set
0; JMP
(RET_ADDR_Class1.set1)
//pop temp 0 
@5
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
//push constant 23
@23
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 15
@15
D=A
@SP
A=M
M=D
@SP
M=M+1
//call Class2.set 2
@RET_ADDR_Class2.set2
M=A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@7
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Class2.set
0; JMP
(RET_ADDR_Class2.set2)
//pop temp 0 
@5
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
//call Class1.get 0
@RET_ADDR_Class1.get3
M=A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Class1.get
0; JMP
(RET_ADDR_Class1.get3)
//call Class2.get 0
@RET_ADDR_Class2.get4
M=A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Class2.get
0; JMP
(RET_ADDR_Class2.get4)
//label WHILE
(WHILE)
//goto WHILE
@WHILE
0; JMP
//function Class2.set 0
(Class2.set)
//push argument 0
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
//pop static 0
@Class2.vm0
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
//push argument 1
@ARG
D=M
@1
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
//pop static 1
@Class2.vm1
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
//push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
//return
@LCL
D=M
@5
D=D-A
A=D
D=M
@R13
M=D
@LCL
D=M
@R14
M=D
@ARG
A=M
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
@ARG
D=M+1
@SP
M=D
@R14
M=M-1
A=M
D=M
@THAT
M=D
@R14
M=M-1
A=M
D=M
@THIS
M=D
@R14
M=M-1
A=M
D=M
@ARG
M=D
@R14
M=M-1
A=M
D=M
@LCL
M=D
@R13
A=M
0;JMP
//function Class2.get 0
(Class2.get)
//push static 0
@Class2.vm0
D=M
@SP
A=M
M=D
@SP
M=M+1
//push static 1
@Class2.vm1
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
//return
@LCL
D=M
@5
D=D-A
A=D
D=M
@R13
M=D
@LCL
D=M
@R14
M=D
@ARG
A=M
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
@ARG
D=M+1
@SP
M=D
@R14
M=M-1
A=M
D=M
@THAT
M=D
@R14
M=M-1
A=M
D=M
@THIS
M=D
@R14
M=M-1
A=M
D=M
@ARG
M=D
@R14
M=M-1
A=M
D=M
@LCL
M=D
@R13
A=M
0;JMP
//function Class1.set 0
(Class1.set)
//push argument 0
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
//pop static 0
@Class1.vm0
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
//push argument 1
@ARG
D=M
@1
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
//pop static 1
@Class1.vm1
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
//push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
//return
@LCL
D=M
@5
D=D-A
A=D
D=M
@R13
M=D
@LCL
D=M
@R14
M=D
@ARG
A=M
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
@ARG
D=M+1
@SP
M=D
@R14
M=M-1
A=M
D=M
@THAT
M=D
@R14
M=M-1
A=M
D=M
@THIS
M=D
@R14
M=M-1
A=M
D=M
@ARG
M=D
@R14
M=M-1
A=M
D=M
@LCL
M=D
@R13
A=M
0;JMP
//function Class1.get 0
(Class1.get)
//push static 0
@Class1.vm0
D=M
@SP
A=M
M=D
@SP
M=M+1
//push static 1
@Class1.vm1
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
//return
@LCL
D=M
@5
D=D-A
A=D
D=M
@R13
M=D
@LCL
D=M
@R14
M=D
@ARG
A=M
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
@ARG
D=M+1
@SP
M=D
@R14
M=M-1
A=M
D=M
@THAT
M=D
@R14
M=M-1
A=M
D=M
@THIS
M=D
@R14
M=M-1
A=M
D=M
@ARG
M=D
@R14
M=M-1
A=M
D=M
@LCL
M=D
@R13
A=M
0;JMP
