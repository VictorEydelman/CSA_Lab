
# Лабораторная работа №3 по Архитектуре Компьютера

* Эйдельман Виктор Аркадьевич. P3214
* asm | stack | neum | hw | instr | struct | trap -> stream | mem | cstr | prob2 | cache
* Базовый вариант: asm | stack | neum | hw | instr | struct | trap | mem | cstr | prob2 | -

## Язык программирования - Assembly

```text
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
      | "load"
      | "dup"

op1 ::= "push"

op2 ::= "word"

op3 ::= "jmp"
      | "jz"
      | "jnz"
      | "jn"
      | "jns"
      | "call"

op4 ::= "push_addr"
        | "pop_addr"
        | "store"

integer ::= [ "-" ] { <any of "0-9"> }

address ::= <any of *> { <any of "0-9"> }

arg ::= <any of "0-9">

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```

Поддерживаются однострочные комментарии, начинающиеся с ```;```.

### Операции

* ```inc``` - инкремент верхнего элемент стека
* ```dec``` - декримент верхнего элемент стека
* ```add``` - произвести сложение двух верхних элементов стека,
   и записать результат в стек вместо них
* ```sub``` - произвести вычитание верхнего элемента стека из
  второго сверху элемента стека, и записать результат в стек вместо них
* ```mul``` - произвести произведение двух верхних элементов стека,
  и записать результат в стек вместо них
* ```div``` - произвести целочисленное деление второго сверхну элемента
  стека на первый сверху элемент стека, и записать результат в стек вместо них
* ```swap``` - произвести обмен местами двух верхних элементов стека
* ```dup``` - добавить в стек такой же, как тот, который в TOS.
* ```ei``` - разрешение прерывания
* ```di``` - запрет прерывания
* ```push``` - записать в стек указанное число
* ```push_addr``` - записать в стек число из памяти с указанным адресом
* ```pop``` - удалить верхний элемент из стека
* ```pop_addr``` - удалить верхний элемент из стека и записать его
  значение по указаному адресу.
* ```jmp``` - безусловный переход на указанную метку
* ```jz``` - переход на указанную метку, если флаг 'Z' равен 1
* ```jnz``` - переход на указанную метку, если флаг 'Z' равен 0
* ```jn``` - переход на указанную метку, если флаг 'N' равен 1
* ```jns``` - переход на указанную метку, если флаг 'N' равен 0
* ```call``` - переход на подпрограмму по указанной метке, PC
  записывается в стек возврата
* ```ret``` - возврат из подпрограммы, восстановление PC из стека
* ```load``` - выгрузка в стек элемента из input_buffer с индексом из TOS.
* ```store``` - загрузка в конец output_buffer_str или output_buffer_int данных находящихся в стеке, выбор между буфферами посуществляется по аргументу, если 1, output_buffer_int, если 2, то output_buffer_int
* ```word``` - определить указаное число в память
* ```halt``` - остановить процессор

### Метки

Метки для переходов определяются на отдельных строчках.
  
## Организация памяти

### Модель памяти процессора

1. Память команд и данных совместная (архитектура фон Неймана)
2. Адресация - прямая абсолютная, поддерживается прямая загрузка на стек
3. Первые три ячейки памяти выделены под input_buffer, где хранятся
   полученные с внешнего источника данные, под output_buffer_int,
   где хранится данные которые мы будем выводить в формате числа, и ouput_buffer,
   где хранится  данные которые мы будем выводить в формате строки, то есть числа преобразованные с помощью ASCII кода в строки.
   Остальные ячейки хранятся в формате инструкция, аргумент.
4. Аргумент ячеек памяти имеет размер 32 бита.
5. Количество ячеек в памяти 256.
6. Ячейки стеков состоят только из аргументов.
7. Ячейки стека имеет размер 32 бита.
8. Работа со стеком происходит только через верний элемент стека, через TOS.

```text
            Memory                      Stack_data              Return_stack
+----------------------------+     +------------------+     +----------------+  
| 00 : input_buffer          |     | 00 : argument    |     | 00 : argument  |
| 01 : output_buffer_int     |     | 01 : argument    |     | 01 : argument  |
| 02 : output_buffer_str     |     | 02 : argument    |     | 02 : argument  |
| 03 : instruction, argument |     |        ...       |     |        ...     |
| 04 : instruction, argument |     | n : argument     |     | n : argument   |
|            ...             |     |        ...       |     |        ...     |
| n  : program start         |     | i : argument     |     | i : argument   |
|            ...             |     | i+1 : argument   |     | i+1 : argument |
| i  : instruction, argument |     |        ...       |     |        ...     |
| i+1: instruction, argument |     +------------------+     +----------------+
|            ...             |
+----------------------------+
```

## Система команд

### Особенности процессора

1. Длина машинного слова не определена.
2. В качестве аргументов команды принимают число, аргумент, метка, адрес или аргументы из вершины стека.
3. Поток управления:
   * Инкремент PC после каждой команды
   * Поддерживается условный и безусловный переход

### Набор инструкций

Язык | Количество тактов | Описание
:-------|:-----------:|--------|
inc| 2 |  инкремент верхнего элемент стека
dec| 2 | декримент верхнего элемент стека
add | 3 | произвести сложение двух верхних элементов стека, и записать результат в стек вместо них
sub | 3 | произвести вычитание верхнего элемента стека из второго сверху элемента стека, и записать результат в стек вместо них
mul | 3 | произвести произведение двух верхних элементов стека, и записать результат в стек вместо них
div | 3 | произвести целочисленное деление второго сверхну элемента стека на первый сверху элемент стека, и записать результат в стек вместо них
swap | 4 | произвести обмен местами двух верхних элементов стека
dup | 3 | добавить в стек такой же, как тот, который в TOS
ei | 2 | разрешение прерывания
di | 2 | запрет прерывания
push | 2 | записать в стек указанное число
push_addr | 4 | записать в стек число из памяти с указанным адресом
pop | 2 |удалить верхний элемент из стека
pop_addr| 4 | удалить верхний элемент из стека и записать его значение по указаному адресу.
jmp | 2 | безусловный переход на указанную метку
jz | 2 | переход на указанную метку, если флаг 'Z' равен 1
jnz | 2 | переход на указанную метку, если флаг 'Z' равен 0
jn | 2 | переход на указанную метку, если флаг 'N' равен 1
jns | 2 | переход на указанную метку, если флаг 'N' равен 0
call | 3 | переход на подпрограмму по указанной метке, PC записывается в стек возврата
ret | 2 | возврат из подпрограммы, восстановление PC из стека
load | 4 | выгрузка из input_buffer в стек
store | 4 | загрузка в конец output_buffer_str или output_buffer_int данных находящихся в стеке, выбор между буфферами посуществляется по аргументу, если 1, output_buffer_int, если 2, то output_buffer_int
word | 0 | определить указаное число в память.
halt | 1 | остановить процессор

### Кодирование инструкций

* Машиный код сериализуется в список JSON.
* Один элемент списка -- одна инструкция.
* Индекс списка -- адрес инструкции. Используется для команд
  перехода и перехода на подпрограмму.
* Первый элеменнт списка хранит индекс старта программы с ключом _start.
Пример:

```text
[
       {
              "_start": 1
       },
       {
              "index": 2,
              "opcode": "ei",
              "arg": "",
       }
]
```

* index -- адрес инструкции
* opcode -- строка с кодом операции
* arg -- аргумент

Типы данных хранятся в модуле isa, где:

* Opcode -- перечисление кодов операций

## Транслятор

Интерфейс командной строки: translator.py <input_file> <target_file>
Реализовано в модуле: [translator](.\translator.py)
Трансляция реализуется в два прохода:

1. Первый:
   При нём у нас есть 4 типа строки:
   * Если строка пустая или содержит просто комментарии, то переход к следующей строке.
   * Если в строке есть символ ":", то эта строка является меткой и
   метка записывается как ключ в список меток, со значением текущего индекса,
   если метка равна "_start",то адрес метки сохраняется.
   * Если строка - это инструкция без аргумента, то добавляем в список инструкций
   элемент состоящий из index, opcode, ""
   * Если строка - это инструкция с аргументом, то добавляем в список инструкций
   элемент состоящий из index, opcode, arg term.
2. Второй:
   * Заменяем все метки в аргументах на их значения этих меток в списке меток.
   * Адрес метки "_start" записывается в начало списка инструкций.

## Модель процессора

Интерфейс командной строки: ```machine.py <machine_code_file> <input_file>
Реализовано в модуле: [machine](.\machine.py).

# DataPath

![image](https://github.com/VictorEydelman/CSA_Lab/assets/113546427/dc81ffac-22d6-4066-b687-0c46a8a16aea)

Реализован в классе ```DataPath```.

Описание:

1. ```memory``` - однопортовая память, поэтому либо читаем, либо пишем.
2. ```ALU``` - ALU, которое принимает значения из TOS сначала на левый, а потом на
   правый вход, оба элемента из стека удаляются, и взаимодейстует с ними с помощью сигналов:
   * ```inc``` - инкрементирует значение полученное на левый вход,
     записывая результат в результат алу.
   * ```dec``` - декрементирует значение полученное на левый вход,
     записывая результат в результат алу.
   * ```add``` - сложение значений полученных на левый и правый вход,
     записывая результат в результат алу.
   * ```sub``` - вычитание значения полученного на левый вход из полученного
     на правый, записывая результат в результат алу.
   * ```mul``` - умножение значений полученных на левый и правый вход,
     записывая результат в результат алу.
   * ```div``` - целочисленное деление значения полученного на левый вход
     на полученное на правый, записывая результат в результат алу.
   * ```swap``` - запись в стек сначала значение полученное на правый вход,
     затем на левый.
   * ```to_memory``` - добавляет в память значение полученное на правый вход,
     по адресу полученному на левый.
   * ```from_memory``` - по адресу полученному на левый вход получает значение
     этой ячейки памяти, и записывает в результат алу.
   * ```dup``` - полученные на левый вход данные мы дважды записываем с стек.
3. ```ControlUnit``` -  ControlUnit
4. ```Stack data``` - стек данных, достать или записать в него можно
   только через TOS, то есть верхний элемент стека. Имеет несколько сигналов:
   * ```signal_stack``` - записывает результат alu в TOS.
   * ```signal_pop``` - удаляет верхний элемент стека.
5. ```tick``` - количество тактов в программе на данный момент. Имеет сигнал:
   * ```signal_tick``` - он инкрементирует значение tick.
6. ```interruption``` - разрешение прерывания. Содержит два сигнала:
   * ```signal_interruption_EI``` - разрешить прерывания.
   * ```signal_interruption_DI``` - запретить прерывания.
7. ```interruption controller``` - позволяет принимать данные при прерывания.
    Передаёт принятые данные в конец значения ячейки памяти 0, где хранится input_buffer,
    и в ячейку 1, где находится input_last_symbol. Имеет сигнал:
   * ```signal_interruption_controller`` - вызывает проверку есть ли прерывание.

# ControlUnit

![image](https://github.com/VictorEydelman/CSA-Lab3/assets/113546427/71cabec9-032c-4549-a8e0-800150d03e52)

Реализован в классе ```Contorl unit```.

1. ```DataPath``` -  DataPath
2. ```instruction decoder``` - Дешефратор инструкций
3. ```PC``` - счётчик команд, регистр, в котором хранится адрес очередной
   инструкции для исполнения.
4. ```Stack return``` - стек данных, достать или записать в него можно
   только через TOS, то есть верхний элемент стека.

Особенности работы модели:

1. Цикл симуляции осуществляется в файле ```simulation```.
2. Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
3. Для журнала состояний процессора используется стандартный модуль logging.
4. Количество инструкций для моделирования лимитировано.
5. Остановка моделирования осуществляется при:
    * превышении лимита количества выполняемых инструкций
    * исключении StopIteration -- если выполнена инструкция halt.

## Тестирование

Тестирование выполняется при помощи golden test-ов.
Тесты реализованы в: golden_test.py.

### Тесты

* hello_world_asm.asm - [hello_world_asm.yml](./golden/hello_world_asm.yml)
* hello_username_asm.asm - [hello_username_asm.yml](./golden/hello_username_asm.yml)
* cat_asm.asm - [cat_asm.yml](./golden/cat_asm.yml)
* prob2_asm.asm - [prob2_asm.yml](./golden/prob2_asm.yml)

Запустить тесты: ```poetry run pytest . -v```
Обновить конфигурацию golden tests: ```poetry run pytest . -v --update-goldens```

### CI при помощи Github Action

```text
name: Python CI

on:
  push:
    branches:
      - master

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: poetry run ruff format --check .

      - name: Run Ruff linters
        run: poetry run ruff check .
```

### Пример использования и журнала работы процессора на примере ```cat```

<details>
<summary>Spoiler</summary>

```shell
> cat .\target.json
  {"_start": 22},
  {"index": 4, "opcode": "word", "arg": "0"},
  {"index": 5, "opcode": "pop", "arg": 0},
  {"index": 6, "opcode": "push_addr", "arg": 4},
  {"index": 7, "opcode": "load", "arg": 0},
  {"index": 8, "opcode": "store", "arg": "2"},
  {"index": 9, "opcode": "push_addr", "arg": 4},
  {"index": 10, "opcode": "load", "arg": 0},
  {"index": 11, "opcode": "push", "arg": "10"},
  {"index": 12, "opcode": "sub", "arg": 0},
  {"index": 13, "opcode": "jz", "arg": 18},
  {"index": 14, "opcode": "push_addr", "arg": 4},
  {"index": 15, "opcode": "inc", "arg": 0},
  {"index": 16, "opcode": "pop_addr", "arg": 4},
  {"index": 17, "opcode": "jmp", "arg": 5},
  {"index": 18, "opcode": "push", "arg": "1"},
  {"index": 19, "opcode": "pop_addr", "arg": 4},
  {"index": 20, "opcode": "ret", "arg": 0},
  {"index": 21, "opcode": "word", "arg": "0"},
  {"index": 22, "opcode": "ei", "arg": 0},
  {"index": 23, "opcode": "push_addr", "arg": 21},
  {"index": 24, "opcode": "load", "arg": 0},
  {"index": 25, "opcode": "push", "arg": "10"},
  {"index": 26, "opcode": "sub", "arg": 0},
  {"index": 27, "opcode": "di", "arg": 0},
  {"index": 28, "opcode": "jz", "arg": 34},
  {"index": 29, "opcode": "pop", "arg": 0},
  {"index": 30, "opcode": "push_addr", "arg": 21},
  {"index": 31, "opcode": "inc", "arg": 0},
  {"index": 32, "opcode": "pop_addr", "arg": 21},
  {"index": 33, "opcode": "jmp", "arg": 22},
  {"index": 34, "opcode": "call", "arg": 5},
  {"index": 35, "opcode": "halt", "arg": 0}]
> python .\machine.py .\target.json .\example\input.txt     
  DEBUG   machine:simulation    PC: 22 ticks: 0 interruption: True in MEM_OUT: {'opcode': 'ei', 'arg': 0} ei 0
  INFO    machine:signal_interruption_controller Interruption                                                                 
  DEBUG   machine:simulation    PC: 23 ticks: 3 interruption: True in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  INFO    machine:signal_interruption_controller Interruption                                                                 
  INFO    machine:signal_interruption_controller Interruption                                                                 
  DEBUG   machine:simulation    PC: 24 ticks: 10 interruption: True in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0           
  DEBUG   machine:simulation    PC: 25 ticks: 13 interruption: True in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10         
  INFO    machine:signal_interruption_controller Interruption
  DEBUG   machine:simulation    PC: 26 ticks: 18 interruption: True in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 27 ticks: 20 interruption: True in MEM_OUT: {'opcode': 'di', 'arg': 0} di 0
  DEBUG   machine:simulation    PC: 28 ticks: 21 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 34} jz 34
  DEBUG   machine:simulation    PC: 29 ticks: 21 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 30 ticks: 22 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 31 ticks: 25 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 32 ticks: 26 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 21} pop_addr 21
  DEBUG   machine:simulation    PC: 33 ticks: 30 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 22} jmp 22
  DEBUG   machine:simulation    PC: 22 ticks: 31 interruption: False in MEM_OUT: {'opcode': 'ei', 'arg': 0} ei 0
  DEBUG   machine:simulation    PC: 23 ticks: 32 interruption: True in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 24 ticks: 35 interruption: True in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 25 ticks: 38 interruption: True in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 26 ticks: 40 interruption: True in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 27 ticks: 42 interruption: True in MEM_OUT: {'opcode': 'di', 'arg': 0} di 0
  DEBUG   machine:simulation    PC: 28 ticks: 43 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 34} jz 34
  DEBUG   machine:simulation    PC: 29 ticks: 43 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 30 ticks: 44 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 31 ticks: 47 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 32 ticks: 48 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 21} pop_addr 21
  DEBUG   machine:simulation    PC: 33 ticks: 52 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 22} jmp 22
  DEBUG   machine:simulation    PC: 22 ticks: 53 interruption: False in MEM_OUT: {'opcode': 'ei', 'arg': 0} ei 0
  DEBUG   machine:simulation    PC: 23 ticks: 54 interruption: True in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 24 ticks: 57 interruption: True in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 25 ticks: 60 interruption: True in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 26 ticks: 62 interruption: True in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 27 ticks: 64 interruption: True in MEM_OUT: {'opcode': 'di', 'arg': 0} di 0
  DEBUG   machine:simulation    PC: 28 ticks: 65 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 34} jz 34
  DEBUG   machine:simulation    PC: 29 ticks: 65 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 30 ticks: 66 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 31 ticks: 69 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 32 ticks: 70 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 21} pop_addr 21
  DEBUG   machine:simulation    PC: 33 ticks: 74 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 22} jmp 22
  DEBUG   machine:simulation    PC: 22 ticks: 75 interruption: False in MEM_OUT: {'opcode': 'ei', 'arg': 0} ei 0
  DEBUG   machine:simulation    PC: 23 ticks: 76 interruption: True in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 24 ticks: 79 interruption: True in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 25 ticks: 82 interruption: True in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 26 ticks: 84 interruption: True in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 27 ticks: 86 interruption: True in MEM_OUT: {'opcode': 'di', 'arg': 0} di 0
  DEBUG   machine:simulation    PC: 28 ticks: 87 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 34} jz 34
  DEBUG   machine:simulation    PC: 29 ticks: 87 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 30 ticks: 88 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 31 ticks: 91 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 32 ticks: 92 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 21} pop_addr 21
  DEBUG   machine:simulation    PC: 33 ticks: 96 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 22} jmp 22
  DEBUG   machine:simulation    PC: 22 ticks: 97 interruption: False in MEM_OUT: {'opcode': 'ei', 'arg': 0} ei 0
  DEBUG   machine:simulation    PC: 23 ticks: 98 interruption: True in MEM_OUT: {'opcode': 'push_addr', 'arg': 21} push_addr 21
  DEBUG   machine:simulation    PC: 24 ticks: 101 interruption: True in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 25 ticks: 104 interruption: True in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 26 ticks: 106 interruption: True in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 27 ticks: 108 interruption: True in MEM_OUT: {'opcode': 'di', 'arg': 0} di 0
  DEBUG   machine:simulation    PC: 28 ticks: 109 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 34} jz 34
  DEBUG   machine:simulation    PC: 34 ticks: 110 interruption: False in MEM_OUT: {'opcode': 'call', 'arg': 5} call 5
  DEBUG   machine:simulation    PC: 5 ticks: 112 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 6 ticks: 113 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 7 ticks: 116 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 8 ticks: 119 interruption: False in MEM_OUT: {'opcode': 'store', 'arg': 2} store 2
  DEBUG   machine:simulation    PC: 9 ticks: 122 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 10 ticks: 125 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 11 ticks: 128 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 12 ticks: 130 interruption: False in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 13 ticks: 132 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 18} jz 18
  DEBUG   machine:simulation    PC: 14 ticks: 132 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 15 ticks: 135 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 16 ticks: 136 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 4} pop_addr 4
  DEBUG   machine:simulation    PC: 17 ticks: 140 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 5} jmp 5
  DEBUG   machine:simulation    PC: 5 ticks: 141 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 6 ticks: 142 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 7 ticks: 145 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 8 ticks: 148 interruption: False in MEM_OUT: {'opcode': 'store', 'arg': 2} store 2
  DEBUG   machine:simulation    PC: 9 ticks: 151 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 10 ticks: 154 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 11 ticks: 157 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 12 ticks: 159 interruption: False in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 13 ticks: 161 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 18} jz 18
  DEBUG   machine:simulation    PC: 14 ticks: 161 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 15 ticks: 164 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 16 ticks: 165 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 4} pop_addr 4
  DEBUG   machine:simulation    PC: 17 ticks: 169 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 5} jmp 5
  DEBUG   machine:simulation    PC: 5 ticks: 170 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 6 ticks: 171 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 7 ticks: 174 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 8 ticks: 177 interruption: False in MEM_OUT: {'opcode': 'store', 'arg': 2} store 2
  DEBUG   machine:simulation    PC: 9 ticks: 180 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 10 ticks: 183 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 11 ticks: 186 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 12 ticks: 188 interruption: False in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 13 ticks: 190 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 18} jz 18
  DEBUG   machine:simulation    PC: 14 ticks: 190 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 15 ticks: 193 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 16 ticks: 194 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 4} pop_addr 4
  DEBUG   machine:simulation    PC: 17 ticks: 198 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 5} jmp 5
  DEBUG   machine:simulation    PC: 5 ticks: 199 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 6 ticks: 200 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 7 ticks: 203 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 8 ticks: 206 interruption: False in MEM_OUT: {'opcode': 'store', 'arg': 2} store 2
  DEBUG   machine:simulation    PC: 9 ticks: 209 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 10 ticks: 212 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 11 ticks: 215 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 12 ticks: 217 interruption: False in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 13 ticks: 219 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 18} jz 18
  DEBUG   machine:simulation    PC: 14 ticks: 219 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 15 ticks: 222 interruption: False in MEM_OUT: {'opcode': 'inc', 'arg': 0} inc 0
  DEBUG   machine:simulation    PC: 16 ticks: 223 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 4} pop_addr 4
  DEBUG   machine:simulation    PC: 17 ticks: 227 interruption: False in MEM_OUT: {'opcode': 'jmp', 'arg': 5} jmp 5
  DEBUG   machine:simulation    PC: 5 ticks: 228 interruption: False in MEM_OUT: {'opcode': 'pop', 'arg': 0} pop 0
  DEBUG   machine:simulation    PC: 6 ticks: 229 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 7 ticks: 232 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 8 ticks: 235 interruption: False in MEM_OUT: {'opcode': 'store', 'arg': 2} store 2
  DEBUG   machine:simulation    PC: 9 ticks: 238 interruption: False in MEM_OUT: {'opcode': 'push_addr', 'arg': 4} push_addr 4
  DEBUG   machine:simulation    PC: 10 ticks: 241 interruption: False in MEM_OUT: {'opcode': 'load', 'arg': 0} load 0
  DEBUG   machine:simulation    PC: 11 ticks: 244 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 10} push 10
  DEBUG   machine:simulation    PC: 12 ticks: 246 interruption: False in MEM_OUT: {'opcode': 'sub', 'arg': 0} sub 0
  DEBUG   machine:simulation    PC: 13 ticks: 248 interruption: False in MEM_OUT: {'opcode': 'jz', 'arg': 18} jz 18
  DEBUG   machine:simulation    PC: 18 ticks: 249 interruption: False in MEM_OUT: {'opcode': 'push', 'arg': 1} push 1
  DEBUG   machine:simulation    PC: 19 ticks: 251 interruption: False in MEM_OUT: {'opcode': 'pop_addr', 'arg': 4} pop_addr 4
  DEBUG   machine:simulation    PC: 20 ticks: 255 interruption: False in MEM_OUT: {'opcode': 'ret', 'arg': 0} ret 0
  DEBUG   machine:simulation    PC: 35 ticks: 256 interruption: False in MEM_OUT: {'opcode': 'halt', 'arg': 0} halt 0
  INFO    machine:simulation    output_buffer: 'Viko\n'
Viko

instr_counter: 121
ticks: 256
```

</details>

### Пример проверки исходного кода

```shell
Run poetry run coverage run -m pytest . -v
============================= test session starts ========================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.5.0 -- /home/runner/.cache/pypoetry/virtualenvs/csa-lab3-ZpubCx5H-py3.12/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/CSA-Lab3/CSA-Lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collecting ... collected 4 items

golden_test.py::test_translator_asm_and_machine[golden/prob2_asm.yml] PASSED [ 25%]
golden_test.py::test_translator_asm_and_machine[golden/hello_world_asm.yml] PASSED [ 50%]
golden_test.py::test_translator_asm_and_machine[golden/hello_username_asm.yml] PASSED [ 75%]
golden_test.py::test_translator_asm_and_machine[golden/cat_asm.yml] PASSED [100%]

============================== 4 passed in 0.73s ===========================
```

```text
| ФИО                         |алг           |LoC|code инстр|инстр|такт|                                   вариант                                  |
| Эйдельман Виктор Аркадьевич |cat           |38 |    33    | 121 |256 | (asm | stack | neum | hw | instr | struct | trap | mem | cstr | prob2 | -) |
| Эйдельман Виктор Аркадьевич |hello_world   |26 |    21    | 92  |181 | (asm | stack | neum | hw | instr | struct | trap | mem | cstr | prob2 | -) |
| Эйдельман Виктор Аркадьевич |hello_username|105|    93    | 477 |987 | (asm | stack | neum | hw | instr | struct | trap | mem | cstr | prob2 | -) |
```
