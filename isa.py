import json
from enum import Enum


class Opcode(str, Enum):
    INC = "inc"  # 0
    DEC = "dec"  # 0
    NOP = "nop"  # 0
    HALT = "halt"  # 0
    EI = "ei"  # 0
    DI = "di"  # 0
    PUSH = "push"  # 1
    PUSH_ADDR = "push_addr"
    PUSH_BY = "push_by"
    POP = "pop"  # 0
    POP_ADDR = "pop_addr"
    JZ = "jz"  # 2
    JNZ = "jnz"  # 2
    JN = "jn"  # 2
    JNS = "jns"  # 2
    JMP = "jmp"  # 2
    ADD = "add"  # 0
    SUB = "sub"  # 0
    MUL = "mul"  # 0
    DIV = "div"  # 0
    CALL = "call"  # 2
    RET = "ret"  # 0
    WORD = "word"  # 1
    RESW = "resw"  # 1
    LOAD = "load"  # 2
    SWAP = "swap"  # 0
    STORE = "store"
    LOAD_SYMBOL = "load_symbol"

    def __str__(self):
        return self.value


def write_code(filename, code):
    with open(filename, "w", encoding="utf-8") as file:
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n".join(buf) + "]")


def read_code(filename):
    with open(filename, encoding="utf-8") as file:
        return json.loads(file.read())
