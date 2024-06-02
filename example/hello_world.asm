sym_in:
    word 60
    word 32
    word 0
sym_out:
    word 62
    word 32
    word 0
what:
    word 87
    word 104
    word 97
    word 116
    word 32
    word 105
    word 115
    word 32
    word 121
    word 111
    word 117
    word 114
    word 32
    word 110
    word 97
    word 109
    word 101
    word 63
    word 10
    word 0
hello:
    word 72
    word 101
    word 108
    word 108
    word 111
    word 44
    word 32
    word 0
symbol:
    word sym_out
print_words:
    push_addr symbol
    push_by
    jz back
    store 2
    push_addr symbol
    inc
    pop_addr symbol
    jmp print_words
back:
    ret
print_name:
    pop
    push_addr number
    load
    store 2
    push_addr number
    load
    push 10
    sub
    jz end
    push_addr number
    inc
    pop_addr number
    jmp print_name
end:
    push 1
    pop_addr number
    ret
num:
    word 0
_start:
    ei
    push_addr num
    load
    push 10
    sub
    di
    jz print
    pop
    push_addr num
    inc
    pop_addr num
    jmp _start
number:
    word 0
print:
    call print_words
    push what
    pop_addr symbol
    call print_words
    push sym_in
    pop_addr symbol
    call print_words
    call print_name
    push sym_out
    pop_addr symbol
    call print_words
    push hello
    pop_addr symbol
    call print_words
    push 0
    pop_addr number
    call print_name
    halt
