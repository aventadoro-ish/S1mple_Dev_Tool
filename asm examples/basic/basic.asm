; semicolons are used for comments

.org 1000       ; .org command is used to set address of a block of code/data

label:          ; word followed by a colon is a label
    NOP         ; instruction
    LDR #10     ; hash-symbol is used for immediate addressing
    STR @2000   ; at-symbol is used for absolute addressing
    MOV R PC

; lines can be concatenated using backslash \
this line is concatenated to the previous one, \
so semicolon is not needed. \
but it is preferred for style-purposes)


; file must terminate in a blank line
