hello_world:
    word 72
    word 101
    word 108
    word 108
    word 111
    word 32
    word 87
    word 111
    word 114
    word 108
    word 100
    word 0
symbol:
    word hello_world
_start:
    push_addr symbol
    push_by
    jz end
    store 2
    push_addr symbol
    inc
    pop_addr symbol
    jmp _start
end:
    halt
