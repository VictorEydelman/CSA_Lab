import logging
import sys

from isa import read_code, Opcode


class DataPath:
    alu = None
    memory = None
    input_token = None
    input_address = None
    ir = None
    memory_size = None
    stack_data = []
    Z = None
    N = None
    output_buffer = []
    tick = None
    interruption = None

    def __init__(self, memory_size, input_token, input_address):
        self.alu = 0
        self.memory = [{"opcode": Opcode.NOP.value, "arg": 0}] * memory_size
        self.input_token = input_token
        self.input_address = input_address
        self.ir = {"opcode": Opcode.NOP.value}
        self.memory_size = memory_size
        self.stack_data.append(0)
        self.Z = 0
        self.N = 0
        self.tick = 0
        self.interruption=True

    def signal_tick(self):
        self.tick += 1
        while self.tick in self.input_address and self.interruption:
            #print(self.input_token[self.input_address.index(self.tick)])
            self.input_address[self.input_address.index(self.tick)] = 0

    def s(self, code: list):
        for mem in code:
            self.memory[mem["index"]] = {"opcode": mem["opcode"],"arg": mem["arg"]}

    def flag(self):
        try:
            if self.alu == 0:
                self.Z = 1
            else:
                self.Z = 0
            if self.alu < 0:
                self.N = 1
            else:
                self.N = 0
        except:
            ""

    def in_alu(self, operation, left_sel=None, right_sel=None):
        left = None
        right = None
        if left_sel is not None:
            if left_sel == "stack":
                left = self.stack_data.pop()
        if right_sel is not None:
            if right_sel == "stack":
                right = self.stack_data.pop()
        if operation == "inc_a":
            self.alu = int(left) + 1
        elif operation == "dec_a":
            self.alu = int(left) - 1
        elif operation == "dec_b":
            self.alu = int(right) - 1
        elif operation == "skip_b":
            self.alu = right
        elif operation == "skip_a":
            self.alu = left
        elif operation == "inc_b":
            self.alu = right + 1
        elif operation == "from_memory":
            self.alu = int(self.memory[int(left)]["arg"])
        elif operation == "to_memory":
            self.memory[int(left)] = {"opcode": self.memory[int(left)]["opcode"], "arg": right}
        elif operation == "add":
            self.alu = int(left) + int(right)
        elif operation == "sub":
            self.alu = int(right) - int(left)
        elif operation == "mul":
            self.alu = int(left) * int(right)
        elif operation == "out":
            i=2
            symbol = int(self.memory[left + i]["arg"])
            while right+1>=i and symbol!=0:
                self.output_buffer.append(chr(symbol))
                symbol = int(self.memory[left+i]["arg"])
                i+=1
        self.flag()

    def signal_stack(self):
        self.stack_data.append(self.alu)

    def to_stack(self, arg):
        self.stack_data.append(arg)

    def signal_output(self):
        symbol = self.stack_data[-1]
        logging.debug("output: %s << %s", repr("".join(self.output_buffer)), repr(symbol))
        self.output_buffer.append(str(symbol))


class ControlUnit:
    data_path = None
    pc = None
    code = None
    stack_return = []

    def __init__(self, code, data_path):
        self.data_path = data_path
        self.pc = int(code[0]["_start"])
        del code[0]
        data_path.s(code)
        self.code = code

    def d(self):
        self.pc += 1
        ir = self.data_path.memory[self.pc]
        opcode, arg = ir["opcode"], ir["arg"]
        if opcode == Opcode.INC:
            self.data_path.signal_tick()
            self.data_path.in_alu("inc_a", left_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.DEC:
            self.data_path.signal_tick()
            self.data_path.in_alu("inc_a", left_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.JMP:
            self.data_path.signal_tick()
            self.pc = arg - 1
        elif opcode == Opcode.JZ:
            self.data_path.signal_tick()
            if self.data_path.Z == 1:
                self.pc = arg - 1
        elif opcode == Opcode.JNZ:
            self.data_path.signal_tick()
            if self.data_path.Z == 0:
                self.pc = arg - 1
        elif opcode == Opcode.JN:
            self.data_path.signal_tick()
            if self.data_path.N == 1:
                self.pc = arg - 1
        elif opcode == Opcode.JNS:
            self.data_path.signal_tick()
            if self.data_path.N == 0:
                self.pc = arg - 1
        elif opcode == Opcode.HALT:
            self.data_path.signal_tick()
            return "halt"
        elif opcode == Opcode.PUSH_ADDR:
            self.data_path.signal_tick()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.PUSH:
            self.data_path.signal_tick()
            self.data_path.to_stack(arg)
        elif opcode == Opcode.POP:
            self.data_path.signal_tick()
            self.data_path.stack_data.pop()
        elif opcode == Opcode.POP_ADDR:
            self.data_path.signal_tick()
            self.data_path.to_stack(arg)
            self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
            self.data_path.stack_data.pop()
            self.data_path.stack_data.pop()
        elif opcode == Opcode.ADD:
            self.data_path.signal_tick()
            self.data_path.in_alu("add", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.SUB:
            self.data_path.signal_tick()
            self.data_path.in_alu("sub", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.MUL:
            self.data_path.signal_tick()
            self.data_path.in_alu("mul", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
        elif opcode == Opcode.CALL:
            self.data_path.signal_tick()
            self.stack_return.append(self.pc)
            self.pc = arg - 1
        elif opcode == Opcode.RET:
            self.data_path.signal_tick()
            self.pc = self.stack_return.pop()
        elif opcode == Opcode.PRINT:
            self.data_path.signal_tick()
            print("".join(self.data_path.output_buffer))
        elif opcode == Opcode.EI:
            self.data_path.interruption = True
        elif opcode == Opcode.DI:
            self.data_path.interruption = False
        elif opcode == Opcode.RESW:
            self.data_path.to_stack(arg)
            self.data_path.to_stack(self.pc)
            self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
            self.data_path.stack_data.pop()
        elif opcode == Opcode.WORD:
            self.data_path.signal_tick()
        elif opcode == Opcode.OUT:
            self.data_path.to_stack(arg+1)
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.to_stack(arg+1)
            self.data_path.in_alu("out", left_sel="stack",right_sel="stack")
        return ""

    def __repr__(self):
        state_repr = "PC: {:3} MEM_OUT: {}".format(
            self.pc,
            self.data_path.memory[self.pc]
        )
        instr = self.data_path.memory[self.pc]
        opcode = instr["opcode"]
        instr_repr = str(opcode)
        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])
        if "term" in instr:
            term = instr["term"]
            instr_repr += " ('{}'@{}:{})".format(term[0], term[1], term[2])
        return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, input_token, input_address, memory, limit):
    data_path = DataPath(memory, input_token, input_address)
    control_unit = ControlUnit(code, data_path)
    i = 0
    logging.debug("%s", control_unit)

    for i in range(limit):
        rez = control_unit.d()
        if rez == "halt":
            break
        logging.debug("%s", control_unit)

    # print(data_path.output_buffer)
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), i


def main(sourse, target):
    code = read_code(sourse)
    with open(target, encoding="utf-8") as file:
        target = file.read()
        input_token = []
        input_address = []
        num = 0
        for char in target:
            if num % 8 == 2:
                input_address.append(int(char))
            if num % 8 == 5:
                input_token.append(char)
            num += 1

    output, instr = simulation(code, input_token, input_address, 200, 200)
    print("".join(output))
    print(instr)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: translator_asm.py <input_file> <target_file>"
    _, sourse, target = sys.argv
    main(sourse, target)
