; semicolons are used for comments

.org 1000       ; .org command is used to set address of a block of code/data

label:          ; word followed by a colon is a label
    NOP         ; instruction
    LDR #10     ; hash-symbol is used for immediate addressing
    STR @2000   ; at-symbol is used for absolute addressing
    MOV PCL R    ; example of register or special operands
    JMP @loop


.org 1050
text:
ds  "hello there!"

single_byte:
db  01

byte_array:
dba 00, 11, 22, 33, 44, 55, 66, 77

.org 2000
loop:
    NOP
    LDR @single_byte
    INC
    MOV AC R

    LDR R $byte_array

    STR @single_byte
    JMP @loop


; lines can be concatenated using backslash \
this line is concatenated to the previous one, \
so semicolon is not needed. \
but it is preferred for style-purposes)


; file must terminate in a blank line
