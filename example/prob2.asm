    num:
        push_addr 101
        push 2
        div
        push 2
        mul
        push_addr 101
        sub
        jz ch
        ret
    ch:
        pop
        push_addr 101
        push_addr 102
        add
        pop_addr 102
        push 0
        ret
    _start:
        push 2
        pop_addr 102
        push 4000000
        pop_addr 103
        push 2
        push 2
        push 1
    loop:
        add
        pop_addr 101
        push_addr 101
        swap
        push_addr 101
        call num
        pop
        push_addr 103
        push_addr 101
        sub
        jn end
        pop
        jmp loop
    end:
        push_addr 102
        store
        halt