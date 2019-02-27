// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(MAIN)
    @SCREEN
    D  = A
    @address
    M = D
    @i
    M = 0
    @KBD
    D = M
    @NOKEYPRESS
    D; JEQ
    @key
    M = -1
    @LOOP
    0;JMP
(NOKEYPRESS)
    @key
    M = 0
(LOOP)
    @key
    D = M
    @address
    A = M
    M = D 
    @i
    M = M +1
    D = M
    @8192
    D = D - A
    @MAIN
    D; JGE
    @address
    M = M+1
    @LOOP
    0;JMP