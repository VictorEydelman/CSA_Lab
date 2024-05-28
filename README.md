
# Лабораторная работа №3 по Архитектуре Компьютера

* Эйдельман Виктор Аркадьевич. P3214
* asm|stack|neum|hw|instr|struct|trap->stream|mem|cstr|prob2|cache
* Базовый вариант:asm|stack|neum|hw|instr|struct|trap|mem|cstr|prob2|-

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
      | "store"
      | "load"
      | "load_symbol"

op1 ::= "push"

op2 ::= "word"

op3 ::= "jmp"
      | "jz"
      | "jnz"
      | "jn"
      | "jns"
      | "call"
      | "store"

op4 ::= "push_addr"
        | "pop_addr"

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
* ```load``` - выгрузка из input_buffer в стек
* ```load_symbol``` - выгрузка из input_buffer_symbol в стек
* ```store``` - загрузка в output_buffer данных из TOS, если
  команда без аргумента и если с указание на константу, то загружается
  значение этой константы.
* ```word``` - определить указаное число в память
* ```halt``` - остановить процессор

### Метки

Метки для переходов определяются на отдельных строчках.
  
## Организация памяти

### Модель памяти процессора

1. Память команд и данных совместная (архитектура фон Неймана)
3. Адресация - прямая абсолютная, поддерживается прямая загрузка на стек
4. Первые три ячейки памяти выделены под input_buffer, где хранятся
   полученные с внешнего источника данные, под input_buffer_symbol,
   где хранится последний полученный символ в виде числа, и ouput_buffer,
   где хранится сообщение которое мы будем выводить. Остальные ячейки
   хранятся в формате инструкция, аргумент.
6. Аргумент ячеек памяти имеет размер 32 бита.
7. Количество ячеек в памяти 256.
8. Ячейки стеков состоят только из аргументов.
9. Работа со стеком происходит только через верний элемент стека, через TOS.

```text
            Memory                      Stack_data              Return_stack
+----------------------------+     +------------------+     +----------------+  
| 00 : input_buffer          |     | 00 : argument    |     | 00 : argument  |
| 01 : input_buffer_symbol   |     | 01 : argument    |     | 01 : argument  |
| 02 : output_buffer         |     | 02 : argument    |     | 02 : argument  |
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

- Длина машинного слова не определена.
- В качестве аргументов команды принимают число, аргумент, метка,
  адрес или аргументы из вершины стека.
- Поток управления:
  - инкремент PC после каждой команды
  - Поддерживается условный и безусловный переход

### Набор инструкций

Язык | Количество тактов | Описание
:-------|:-----------:|--------|
inc| 1 |  инкремент верхнего элемент стека
dec| 1 | декримент верхнего элемент стека
add | 2| произвести сложение двух верхних элементов стека,
и записать результат в стек вместо них
sub | 2| произвести вычитание верхнего элемента стека из
второго сверху элемента стека, и записать результат в стек вместо них
mul | 2 | произвести произведение двух верхних элементов стека,
и записать результат в стек вместо них
div | 2 | произвести целочисленное деление второго сверхну элемента
стека на первый сверху элемент стека, и записать результат в стек вместо них
swap |3 | произвести обмен местами двух верхних элементов стека
ei | 1 | разрешение прерывания
di | 1 | запрет прерывания
push | 2 | записать в стек указанное число
push_addr | 3 | записать в стек число из памяти с указанным адресом
pop | 1 |удалить верхний элемент из стека
pop_addr| 3 |удалить верхний элемент из стека и записать его значение
по указаному адресу.
jmp | 1 | безусловный переход на указанную метку
jz | 1 | переход на указанную метку, если флаг 'Z' равен 1
jnz | 1 | переход на указанную метку, если флаг 'Z' равен 0
jn | 1 | переход на указанную метку, если флаг 'N' равен 1
jns | 1 | переход на указанную метку, если флаг 'N' равен 0
call | 2 | переход на подпрограмму по указанной метке, PC записывается
в стек возврата
ret | 1 | возврат из подпрограммы, восстановление PC из стека
load | 3 | выгрузка из input_buffer в стек
load_symbol | 3 | выгрузка из input_buffer_symbol в стек
store | 3 | загрузка в output_buffer данных из TOS, если команда без аргумента
store | 2*n+1 | загрузка в output_buffer данных константы из памяти,
если аргумент - метка на неё указывающая.(n - количество букв)
word | 0| определить указаное число в память.
halt | 0 | остановить процессор

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
   - Если строка пустая или содержит просто комментарии, то переход к следующей строке.
   - Если в строке есть символ ":", то эта строка является меткой и
   метка записывается как ключ в список меток, со значением текущего индекса,
   если метка равна "_start",то индекс сохраняется отдельно в список инструкций.
   - Если строка - это инструкция без аргумента, то добавляем в список инструкций
   элемент состоящий из index, opcode, term
   - Если строка - это инструкция с аргументом, то добавляем в список инструкций
   элемент состоящий из index, opcode, arg term.
2. Второй:
   - Заменяем все метки в аргументах на их значения этих меток в списке меток.

## Модель процессора

Интерфейс командной строки: ```machine.py <machine_code_file> <input_file>
Реализовано в модуле: [machine](.\machine.py).

# DataPath

![image](https://github.com/VictorEydelman/CSA-Lab3/assets/113546427/eaf3e2f0-0307-4186-a985-f1474202f093)

Реализован в классе ```DataPath```.

Описание:

1. ```memory``` - однопортовая память, поэтому либо читаем, либо пишем.
2. ```ALU``` - ALU, которое принимает значения из TOS сначала на левый, а потом на
   правый вход, и взаимодейстует с ними с помощью сигналов:
   -  ```inc``` - инкрементирует значение полученное на левый вход,
     записывая результат в результат алу.
   -  ```dec``` - декрементирует значение полученное на левый вход,
     записывая результат в результат алу.
   -  ```add``` - сложение значений полученных на левый и правый вход,
     записывая результат в результат алу.
   -  ```sub``` - вычитание значения полученного на левый вход из полученного
     на правый, записывая результат в результат алу.
   -  ```mul``` - умножение значений полученных на левый и правый вход,
     записывая результат в результат алу.
   -  ```div``` - целочисленное деление значения полученного на левый вход
     на полученное на правый, записывая результат в результат алу.
   -  ```swap``` - запись в стек сначала значение полученное на правый вход,
     затем на левый.
   -  ```to_memory``` - добавляет в память значение полученное на правый вход,
     по адресу полученному на левый.
   -  ```from_memory``` - по адресу полученному на левый вход получает значение
     этой ячейки памяти, и записывает в результат алу.
   -  ```store``` - позволяет загрузить в буффер вывода данные из константы,
     для этого в левый вход приходит адрес метки в памяти, затем пока пришедший
     из памяти не равен ```\0```, мы записываем полученные значения подряд в буффер вывода.
4. ```ControlUnit``` -  ControlUnit
5. ```Stack data``` - стек данных, достать или записать в него можно только через TOS,
   то есть верхний элемент стека. Имеет несколько сигналов:
   - ```signal_stack``` - записывает результат alu в TOS.
   - ```signal_pop``` - удаляет верхний элемент стека.
7. ```tick``` - количество тактов в программе на данный момент. Имеет сигнал:
   - ```signal_tick``` - он инкрементирует значение tick.
8. ```interruption``` - разрешение прерывания. Содержит два сигнала:
   - ```signal_interruption_EI``` - разрешить прерывания.
   - ```signal_interruption_DI``` - запретить прерывания.
9. ```interruption controller``` - позволяет принимать данные при прерывания.
    Передаёт принятые данные в конец значения ячейки памяти 0, где хранится input_buffer,
    и в ячейку 1, где находится input_last_symbol.


# ControlUnit

![image](https://github.com/VictorEydelman/CSA-Lab3/assets/113546427/71cabec9-032c-4549-a8e0-800150d03e52)

Реализован в классе ```Contorl unit```.
1. ```DataPath``` -  DataPath
2. ```instruction decoder``` - Дешефратор инструкций
3. ```PC``` - счётчик команд, регистр, в котором хранится адрес очередной
   инструкции для исполнения.
5. ``` Stack return``` - стек данных, достать или записать в него можно
   только через TOS, то есть верхний элемент стека.

Особенности работы модели:
- Цикл симуляции осуществляется в файле ```simulation```.
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования лимитировано.
- Остановка моделирования осуществляется при:
  - превышении лимита количества выполняемых инструкций
  - исключении StopIteration -- если выполнена инструкция halt.

## Тестирование

Тестирование выполняется при помощи golden test-ов.
Тесты реализованы в: golden_test.py.

Запустить тесты: ```poetry run pytest . -v```
Обновить конфигурацию golden tests: ```poetry run pytest . -v --update-goldens```

CI при помощи Github Action:

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

Пример использования и журнала работы процессора на примере ```cat```:

```shell
(Lab) PS C:\Users\veyde\OneDrive\Документы\Работы ИТМО\АК\Лаба3> cat .\target.json
[{"_start": 3},
{"index": 5, "opcode": "ei", "arg": ""},
{"index": 6, "opcode": "load_symbol", "arg": ""},
{"index": 7, "opcode": "push", "arg": "10"},
{"index": 8, "opcode": "sub", "arg": ""},
{"index": 9, "opcode": "jz", "arg": 11},
{"index": 10, "opcode": "jmp", "arg": 4},
{"index": 11, "opcode": "load", "arg": ""},
{"index": 12, "opcode": "store", "arg": ""},
{"index": 13, "opcode": "halt", "arg": ""}]
(Lab) PS C:\Users\veyde\OneDrive\Документы\Работы ИТМО\АК\Лаба3> python .\machine.py .\target.json .\example\input.txt     
DEBUG   machine:simulation    PC: 5 ticks: 0 MEM_OUT: {'opcode': 'ei', 'arg': ''} ei 
DEBUG   machine:simulation    PC: 6 ticks: 3 MEM_OUT: {'opcode': 'load_symbol', 'arg': ''} load_symbol 
DEBUG   machine:simulation    PC: 7 ticks: 10 MEM_OUT: {'opcode': 'push', 'arg': '10'} push 10
DEBUG   machine:simulation    PC: 8 ticks: 12 MEM_OUT: {'opcode': 'sub', 'arg': ''} sub
DEBUG   machine:simulation    PC: 9 ticks: 20 MEM_OUT: {'opcode': 'jz', 'arg': 11} jz 11
DEBUG   machine:simulation    PC: 10 ticks: 20 MEM_OUT: {'opcode': 'jmp', 'arg': 4} jmp 4
DEBUG   machine:simulation    PC: 4 ticks: 21 MEM_OUT: {'opcode': 'nop', 'arg': 0} nop 0
DEBUG   machine:simulation    PC: 5 ticks: 21 MEM_OUT: {'opcode': 'ei', 'arg': ''} ei
DEBUG   machine:simulation    PC: 6 ticks: 22 MEM_OUT: {'opcode': 'load_symbol', 'arg': ''} load_symbol
DEBUG   machine:simulation    PC: 7 ticks: 25 MEM_OUT: {'opcode': 'push', 'arg': '10'} push 10
DEBUG   machine:simulation    PC: 8 ticks: 27 MEM_OUT: {'opcode': 'sub', 'arg': ''} sub
DEBUG   machine:simulation    PC: 9 ticks: 29 MEM_OUT: {'opcode': 'jz', 'arg': 11} jz 11
DEBUG   machine:simulation    PC: 11 ticks: 30 MEM_OUT: {'opcode': 'load', 'arg': ''} load
DEBUG   machine:simulation    PC: 12 ticks: 33 MEM_OUT: {'opcode': 'store', 'arg': ''} store
DEBUG   machine:simulation    PC: 13 ticks: 36 MEM_OUT: {'opcode': 'halt', 'arg': ''} halt
INFO    machine:simulation    output_buffer: 'Vikor\n'
Vikor

instr_counter: 16
ticks: 36
```

Пример проверки исходного кода:

```shell
Run poetry run coverage run -m pytest . -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.5.0 -- /home/runner/.cache/pypoetry/virtualenvs/csa-lab3-ZpubCx5H-py3.12/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/CSA-Lab3/CSA-Lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collecting ... collected 4 items

golden_test.py::test_translator_asm_and_machine[golden/prob2_asm.yml] PASSED [ 25%]
golden_test.py::test_translator_asm_and_machine[golden/hello_world_asm.yml]PASSED[50%]
golden_test.py::test_translator_asm_and_machine[golden/hello_username_asm.yml]PASSED[75%]
golden_test.py::test_translator_asm_and_machine[golden/cat_asm.yml] PASSED [100%]

============================== 4 passed in 0.73s ===============================
```

```text
| ФИО                         |алг           |LoC|code инстр|инстр|такт|
| Эйдельман Виктор Аркадьевич |cat           |11 |    10    | 16  |351 |
| Эйдельман Виктор Аркадьевич |hello_world   |16 |    15    | 3   |24  |
| Эйдельман Виктор Аркадьевич |hello_username|56 |    51    |23   |116 |
```
