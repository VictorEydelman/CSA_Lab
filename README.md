# Лабораторная работа №3 по Архитектуре Компьютера
* Эйдельман Виктор Аркадьевич. P3214
* asm | stack | neum | hw | instr | struct | trap -> stream | mem | cstr | prob2 | cache
* Базовый вариант: asm | stack | neum | hw | instr | struct | trap -> stream | mem | cstr | prob2 | -

Язык программирования - Assembly
```
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"

label ::= label_name ":"

instr ::= op0
        | op1 integer
        | op2 arg
        | op3 label_name
        | op4 address

op0 ::= "inc"
      | "dec"
      | "halt"
      | "ei"
      | "di"
      | "pop"
      | "ret"
      | "add"
      | "sub"
      | "mul"
      | "swap"
      | "print"

op1 ::= "push"

op2 ::= "word"
        | "resw"

op3 ::= "jmp"
      | "jz"
      | "jnz"
      | "jn"
      | "jns"
      | "call"
      | "out"

op4 ::= "push_addr"
        | "pop_addr"

integer ::= [ "-" ] { <any of "0-9"> }

address ::= <any of *> { <any of "0-9"> }

arg ::= <any of "0-9">

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```
