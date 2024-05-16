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
Поддерживаются однострочные комментарии, начинающиеся с ```;```.

## Операции:
* ```inc``` - инкремент верхнего элемент стека
* ```dec``` - декримент верхнего элемент стека
* ```add``` - произвести сложение двух верхних элементов стека, и записать результат в стек вместо них
* ```sub``` - произвести вычитание верхнего элемента стека из второго сверху элемента стека, и записать результат в стек вместо них
* ```mul``` - произвести произведение двух верхних элементов стека, и записать результат в стек вместо них
* ```swap``` - произвести обмен местами двух верхних элементов стека
* ```ei``` - разрешение прерывания
* ```di``` - запрет прерывания
* ```push``` - записать в стек указанное число
* ```push_addr``` - записать в стек число из памяти с указанным адресом
* ```pop``` - удалить верхний элемент из стека
* ```pop_addr``` - удалить верхний элемент из стека и записать его значение по указаному адресу.
* ```jmp``` - безусловный переход на указанную метку
* ```jz``` - переход на указанную метку, если флаг 'Z' равен 1
* ```jnz``` - переход на указанную метку, если флаг 'Z' равен 0
* ```jn``` - переход на указанную метку, если флаг 'N' равен 1
* ```jns``` - переход на указанную метку, если флаг 'N' равен 0
* ```call``` - переход на подпрограмму по указанной метке, PC записывается в стек возврата
* ```ret``` - возврат из подпрограммы, восстановление PC из стека
* ```word``` - определить указаное число в память.
* ```halt``` - остановить процессор
  ## Метки
  Метки для переходов определяются на отдельных строчках.
  
