    max:
        word 4000000
    now:
        word 0
    sum:
        word 2
    prov:
        push_addr now
        push 2
        div
        push 2
        mul
        push_addr now
        sub
        jz ch
        ret
    ch:
        pop
        push_addr now
        push_addr sum
        add
        pop_addr sum
        push 0
        ret
    _start:
        push 2
        dup
        push 1
    loop:
        add
        pop_addr now
        push_addr now
        swap
        push_addr now
        call prov
        pop
        push_addr max
        push_addr now
        sub
        jn end
        pop
        jmp loop
    end:
        push_addr sum
        store 1
        halt
