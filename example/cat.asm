number:
    word 1
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
print:
    call print_name
    halt
