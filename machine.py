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
    tos = None
    input_buffer = None
    output_buffer_str = None
    output_buffer_int = None

    def __init__(self, memory_size, input_token, input_address):
        self.alu = 0
        self.memory = [{"opcode": Opcode.NOP.value, "arg": 0}] * memory_size
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
        self.tos = 0
        self.input_buffer = []
        self.output_buffer_str = []
        self.output_buffer_int = []

    def signal_tick(self):
        self.tick += 1

    def signal_tos_pop(self):
        if self.stack_data:
            a = self.stack_data.pop()
            if self.stack_data:
                self.tos = self.stack_data[-1]
        return a

    def signal_tos_push(self, arg):
        self.stack_data.append(arg)
        self.tos = arg

    def signal_interruption_controller(self):
        if self.input_address:
            if self.tick in self.input_address and self.interruption and self.tick <= max(self.input_address):
                a = self.input_token[self.input_address.index(self.tick)]
                self.input_address[self.input_address.index(self.tick)] = 0
                self.signal_tick()
                logging.info("Interruption")
                self.input_buffer.append(a)
                self.signal_tick()
                self.signal_interruption_controller()
            elif self.tick > max(self.input_address) > 0:
                self.input_address = [0]
                self.input_buffer.append("\n")
                self.signal_tick()

    def instructions_in_memory(self, code: list):
        for mem in code:
            self.memory[mem["index"]] = {"opcode": mem["opcode"], "arg": int(mem["arg"])}

    def flag(self):
        if self.tos == 0:
            self.Z = 1
        else:
            self.Z = 0
        if self.tos < 0:
            self.N = 1
        else:
            self.N = 0

    def checking_the_number(self):
        if self.alu <= -(2**31):
            self.alu = self.alu + 2**32
            self.signal_tick()
            self.signal_interruption_controller()
        if self.alu >= 2**31:
            self.alu = self.alu - 2**32
            self.signal_tick()
            self.signal_interruption_controller()

    def operation_in_alu(self, operation, left, right):
        if operation == "inc":
            self.alu = left + 1
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "dec":
            self.alu = left - 1
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "add":
            self.alu = left + right
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "sub":
            self.alu = right - left
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "mul":
            self.alu = left * right
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "div":
            self.alu = right // left
            self.signal_tick()
            self.signal_interruption_controller()
        self.checking_the_number()

    def in_alu_with_memory(self, operation, left, right):
        if operation == "from_memory":
            if left == 0:
                if self.input_buffer:
                    self.alu = ord(self.input_buffer[right])
                else:
                    self.alu = 0
            else:
                self.alu = self.memory[left]["arg"]
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "to_memory":
            self.checking_the_number()
            if left == 2:
                self.output_buffer_str.append(chr(right))
            elif left == 1:
                self.output_buffer_int.append(str(right))
            else:
                self.alu = right
                self.memory[left] = {"opcode": self.memory[left]["opcode"], "arg": self.alu % (2**32)}
            self.signal_tick()
            self.signal_interruption_controller()

    def in_alu(self, operation, left_sel=None, right_sel=None):
        left = None
        right = None
        if left_sel is not None:
            left = self.signal_tos_pop()
        if right_sel is not None:
            self.signal_tick()
            self.signal_interruption_controller()
            right = self.signal_tos_pop()
        if operation in {"inc", "dec", "mul", "div", "add", "sub"}:
            self.operation_in_alu(operation, left, right)
        elif operation == "swap":
            self.signal_tos_push(right)
            self.signal_tick()
            self.signal_interruption_controller()
            self.signal_tos_push(left)
            self.alu = right
            self.signal_tick()
            self.signal_interruption_controller()
        elif operation == "dup":
            self.signal_tos_push(left)
            self.signal_tick()
            self.signal_interruption_controller()
            self.signal_tos_push(left)
        else:
            self.in_alu_with_memory(operation, left, right)
        self.flag()

    def signal_stack(self):
        self.checking_the_number()
        self.signal_tos_push(self.alu)

    def to_stack(self, arg):
        if arg <= -(2**31):
            arg = arg + 2**32
        if arg >= 2**31:
            arg = arg - 2**32
        self.signal_tos_push(arg)

    def signal_pop(self):
        self.signal_tos_pop()

    def signal_interruption_ei(self):
        self.interruption = True
        self.signal_tick()
        self.signal_interruption_controller()

    def signal_interruption_di(self):
        self.interruption = False


class ControlUnit:
    data_path = None
    pc = None
    code = None
    stack_return = None
    tos = None

    def __init__(self, code, data_path):
        self.data_path = data_path
        self.pc = int(code[0]["_start"])
        del code[0]
        self.stack_return = []
        data_path.instructions_in_memory(code)
        self.code = code
        self.tos = 0

    def tos_pop(self):
        if self.stack_return:
            a = self.stack_return.pop()
            if self.stack_return:
                self.tos = self.stack_return[-1]
        return a

    def tos_push(self, arg):
        self.stack_return.append(arg)
        self.tos = arg

    def operation(self, opcode):
        if opcode == Opcode.INC:
            self.data_path.in_alu("inc", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.DEC:
            self.data_path.in_alu("dec", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.ADD:
            self.data_path.in_alu("add", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.SUB:
            self.data_path.in_alu("sub", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.MUL:
            self.data_path.in_alu("mul", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.DIV:
            self.data_path.in_alu("div", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        else:
            self.data_path.in_alu("swap", left_sel="stack", right_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()

    def without_arg(self, opcode):
        if opcode == Opcode.RET:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = self.tos_pop()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.EI:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_interruption_ei()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.DI:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_interruption_di()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.LOAD:
            self.data_path.to_stack(0)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("from_memory", left_sel="stack", right_sel="stack")
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.DUP:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("dup", left_sel="stack")
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        else:
            self.operation(opcode)

    def branching(self, opcode, arg):
        self.data_path.flag()
        if opcode == Opcode.JMP:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.JZ and self.data_path.Z == 1:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.JNZ and self.data_path.Z == 0:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.JN and self.data_path.N == 1:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.JNS and self.data_path.N == 0:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()

    def push_pop_stack(self, opcode, arg):
        if opcode == Opcode.PUSH_ADDR:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.PUSH:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.PUSH_BY:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("from_memory", left_sel="stack")
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.POP_ADDR:
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.POP:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_pop()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()

    def instruction_decoder(self):
        ir = self.data_path.memory[self.pc]
        opcode = ir["opcode"]
        if opcode in {Opcode.JMP, Opcode.JZ, Opcode.JNS, Opcode.JN, Opcode.JNZ}:
            self.branching(opcode, ir["arg"])
        elif opcode == Opcode.HALT:
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            raise StopIteration
        elif opcode in {Opcode.PUSH, Opcode.PUSH_BY, Opcode.PUSH_ADDR, Opcode.POP, Opcode.POP_ADDR}:
            self.push_pop_stack(opcode, ir["arg"])
        elif opcode == Opcode.CALL:
            arg = ir["arg"]
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.tos_push(self.pc)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.pc = arg - 1
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode == Opcode.STORE:
            arg = ir["arg"]
            self.data_path.to_stack(arg)
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.in_alu("to_memory", left_sel="stack", right_sel="stack")
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
            self.data_path.signal_stack()
            self.data_path.signal_tick()
            self.data_path.signal_interruption_controller()
        elif opcode in {
            Opcode.RET,
            Opcode.EI,
            Opcode.DI,
            Opcode.LOAD,
            Opcode.DUP,
            Opcode.INC,
            Opcode.DEC,
            Opcode.ADD,
            Opcode.SUB,
            Opcode.MUL,
            Opcode.DIV,
            Opcode.SWAP,
        }:
            self.without_arg(opcode)
        self.pc += 1
        return ""

    def __repr__(self):
        state_repr = "PC: {} ticks: {} interruption: {} in MEM_OUT: {}".format(
            self.pc, self.data_path.tick, self.data_path.interruption, self.data_path.memory[self.pc]
        )
        instr = self.data_path.memory[self.pc]
        opcode = instr["opcode"]
        instr_repr = str(opcode)
        instr_repr += " {}".format(instr["arg"])
        return "{} {}".format(state_repr, instr_repr).strip()


def simulation(code, input_token, input_address, memory, limit):
    data_path = DataPath(memory, input_token, input_address)
    control_unit = ControlUnit(code, data_path)
    i = 0
    logging.debug("%s", control_unit)
    try:
        for i in range(limit):
            control_unit.instruction_decoder()
            logging.debug("%s", control_unit)
    except StopIteration:
        pass
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer_str + data_path.output_buffer_int)))
    return "".join(data_path.output_buffer_str + data_path.output_buffer_int), i + 1, data_path.tick


def main(program_file, input_file):
    code = read_code(program_file)
    with open(input_file, encoding="utf-8") as file:
        tar = file.read()
        input_token = []
        input_address = []
        if tar != "":
            t = eval(tar)
            for num, char in t:
                input_address.append(num)
                input_token.append(char)

    output, instr, tick = simulation(code, input_token, input_address, 256, 1000)
    print("".join(output))
    print("instr_counter:", instr)
    print("ticks:", tick)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(format="%(levelname)-7s %(module)s:%(funcName)-13s %(message)s")
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
