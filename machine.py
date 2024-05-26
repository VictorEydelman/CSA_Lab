import logging
import sys

from isa import Opcode, read_code


class DataPath:
    alu = None
    memory = None
    input_token = None
    input_address = None
    memory_size = None
    stack_data = None
    Z = None
    N = None
    tick = None
    interruption = None
    tick_now = None

    def __init__(self, memory_size, input_token, input_address):
        self.alu = 0
        self.memory = [{"opcode": Opcode.NOP.value, "arg": 0}] * memory_size
        self.memory[0], self.memory[2] = (
            {"opcode": Opcode.NOP.value, "arg": ""},
            {"opcode": Opcode.NOP.value, "arg": ""},
        )
        self.input_token = input_token
        self.input_address = input_address
        self.ir = {"opcode": Opcode.NOP.value}
        self.memory_size = memory_size
        self.stack_data = []
        self.Z = 0
        self.N = 0
        self.tick = 0
        self.interruption = True
        self.tick_now = 0

    def signal_tick(self):
        self.tick += 1

    def a_interruption(self):
        num = self.tick
        while num <= self.tick:
            while num in self.input_address and self.interruption:
                a = self.input_token[self.input_address.index(num)]
                self.memory[0] = {"opcode": self.memory[0]["opcode"], "arg": self.memory[0]["arg"] + a}
                self.signal_tick()
                self.memory[1] = {"opcode": self.memory[0]["opcode"], "arg": ord(a)}
                self.input_address[self.input_address.index(num)] = 0
                self.signal_tick()
            num += 1

    def s(self, code: list):
        for mem in code:
            self.memory[mem["index"]] = {"opcode": mem["opcode"], "arg": mem["arg"]}

    def flag(self):
        if not isinstance(self.alu, str):
            if self.alu == 0:
                self.Z = 1
            else:
                self.Z = 0
            if self.alu < 0:
                self.N = 1
            else:
                self.N = 0

    def inc_dec(self,operation,left):
        if operation == "inc":
            self.alu = int(left) + 1
        elif operation == "dec":
            self.alu = int(left) - 1
    def operation_in_alu(self, operation, left, right):
        if operation==("inc" or "dec"):
            self.inc_dec(operation,left)
        elif operation == "add":
            self.alu = int(left) + int(right)
        elif operation == "sub":
            self.alu = int(right) - int(left)
        elif operation == "mul":
            self.alu = int(left) * int(right)
        elif operation == "div":
            self.alu = int(right) // int(left)
        elif operation == "swap":
            self.stack_data.append(left)
            self.signal_tick()
            self.a_interruption()
            self.stack_data.append(right)
            self.alu = right

    def in_alu_with_memory(self, operation, left, right):
        if operation == "from_memory":
            self.alu = self.memory[int(left)]["arg"]
        elif operation == "to_memory":
            if int(left) != 2:
                self.alu = int(right)
                self.memory[int(left)] = {"opcode": self.memory[int(left)]["opcode"], "arg": right}
            else:
                self.alu = str(right)
                self.memory[int(left)] = {
                    "opcode": self.memory[int(left)]["opcode"],
                    "arg": str(self.memory[int(left)]["arg"]) + str(right),
                }

    def in_alu(self, operation, left_sel=None, right_sel=None):
        left = None
        right = None
        if left_sel is not None:
            left = self.stack_data.pop()
        if right_sel is not None:
            right = self.stack_data.pop()
        if operation == ("inc" or "dec" or "mul" or "div" or "swap" or "add" or "sub"):
            self.operation_in_alu(operation, left, right)
        elif operation == "out":
            i = 0
            symbol = 1
            while int(right) > i and symbol != 0 and self.memory[left + i]["opcode"] == Opcode.WORD:
                symbol = int(self.memory[left + i]["arg"])
                self.signal_tick()
                self.a_interruption()
                self.alu = symbol
                self.memory[2]["arg"] += chr(symbol)
                self.signal_tick()
                self.a_interruption()
                i += 1
        else:
            self.in_alu_with_memory(operation,left,right)
        self.flag()

    def signal_stack(self):
        self.stack_data.append(self.alu)

    def to_stack(self, arg):
        self.stack_data.append(arg)


class ControlUnit:
    data_path = None
    pc = None
    code = None
    stack_return = None

    def __init__(self, code, data_path):
        self.data_path = data_path
        self.pc = int(code[0]["_start"]) + 1
        del code[0]
        self.stack_return = []
        data_path.s(code)
        self.code = code

    def operation(self,opcode):
        if opcode == Opcode.INC:
            self.data_path.in_alu("inc", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.DEC:
            self.data_path.in_alu("inc", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.ADD:
            self.data_path.in_alu("add", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.SUB:
            self.data_path.in_alu("sub", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.MUL:
            self.data_path.in_alu("mul", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.DIV:
            self.data_path.in_alu("div", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()

    def without_arg(self,opcode):
        if opcode == Opcode.RET:
            self.pc = self.stack_return.pop()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.EI:
            self.data_path.interruption = True
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.DI:
            self.data_path.interruption = False
            self.data_path.signal_tick()
        elif opcode == Opcode.LOAD:
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.to_stack(0)
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.LOAD_SYMBOL:
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.to_stack(1)
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        else:
            self.operation(opcode)

    def branching(self,opcode,arg):
        if opcode == Opcode.JMP:
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.JZ and self.data_path.Z == 1:
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.JNZ and self.data_path.Z == 0:
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.JN and self.data_path.N == 1:
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.JNS and self.data_path.N == 0:
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
    def push_pop_stack(self,opcode,arg):
        if opcode == Opcode.PUSH_ADDR:
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.PUSH:
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.POP_ADDR:
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.POP:
            self.data_path.stack_data.pop()
            self.data_path.signal_tick()
            self.data_path.a_interruption()
    def d(self):
        self.pc += 1
        ir = self.data_path.memory[self.pc]
        opcode = ir["opcode"]
        if opcode == (Opcode.JMP or Opcode.JZ or Opcode.JNZ or Opcode.JN or Opcode.JNS):
            self.branching(opcode,ir["arg"])
        elif opcode == Opcode.HALT:
            return "halt"
        elif opcode == (Opcode.PUSH or Opcode.PUSH_ADDR or Opcode.POP or Opcode.POP_ADDR):
            self.push_pop_stack(opcode, ir["arg"])
        elif opcode == Opcode.CALL:
            arg = ir["arg"]
            self.data_path.signal_tick()
            self.data_path.a_interruption()
            self.stack_return.append(self.pc)
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.a_interruption()
        elif opcode == Opcode.STORE:
            arg = ir["arg"]
            if arg != "":
                self.data_path.signal_tick()
                self.data_path.a_interruption()
                self.data_path.to_stack(arg)
                self.data_path.in_alu("from_memory", left_sel="stack")
                self.data_path.signal_tick()
                self.data_path.a_interruption()
                self.data_path.signal_stack()
                self.data_path.to_stack(arg + 1)
                self.data_path.signal_tick()
                self.data_path.a_interruption()
                self.data_path.in_alu("out", left_sel="stack", right_sel="stack")
                self.data_path.signal_tick()
                self.data_path.a_interruption()
            else:
                self.data_path.to_stack(2)
                self.data_path.signal_tick()
                self.data_path.a_interruption()
                self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
                self.data_path.signal_stack()
                self.data_path.signal_tick()
                self.data_path.a_interruption()
        else:
            self.without_arg(opcode)
        return ""

    def __repr__(self):
        state_repr = "PC: {} MEM_OUT: {}".format(self.pc, self.data_path.memory[self.pc])
        instr = self.data_path.memory[self.pc]
        opcode = instr["opcode"]
        instr_repr = str(opcode)
        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])
        return "{} {}".format(state_repr, instr_repr)


def simulation(code, input_token, input_address, memory, limit):
    data_path = DataPath(memory, input_token, input_address)
    control_unit = ControlUnit(code, data_path)

    for i in range(limit):
        rez = control_unit.d()
        if rez == "halt":
            break
        logging.debug("%s", control_unit)

    logging.info("output_buffer: %s", repr("".join(str(data_path.memory[2]["arg"]))))
    return "".join(str(data_path.memory[2]["arg"])), i + 1, data_path.tick


def main(sourse, target):
    code = read_code(sourse)
    with open(target, encoding="utf-8") as file:
        target = file.read()
        input_token = []
        input_address = []
        if target != "":
            t = eval(target)
            for num, char in t:
                input_address.append(num)
                input_token.append(char)

    output, instr, tick = simulation(code, input_token, input_address, 200, 1000)
    print("".join(output))
    print(instr)
    print(tick)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(format="%(levelname)-7s %(module)s:%(funcName)-13s %(message)s")
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <input_file> <target_file>"
    _, sourse, target = sys.argv
    main(sourse, target)
