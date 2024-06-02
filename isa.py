import json
from enum import Enum


class Opcode(str, Enum):
    INC = "inc"
    DEC = "dec"
    NOP = "nop"
    HALT = "halt"
    EI = "ei"
    DI = "di"
    PUSH = "push"
    PUSH_ADDR = "push_addr"
    PUSH_BY = "push_by"
    POP = "pop"
    POP_ADDR = "pop_addr"
    JZ = "jz"
    JNZ = "jnz"
    JN = "jn"
    JNS = "jns"
    JMP = "jmp"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    CALL = "call"
    RET = "ret"
    WORD = "word"
    RESW = "resw"
    LOAD = "load"
    SWAP = "swap"
    STORE = "store"
    DUP = "dup"

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
