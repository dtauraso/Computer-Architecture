"""CPU functionality."""

import sys

# for branch table in ALU
multiply_opcode = 0b10100010

stack_pointer = 7
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # special registers
        # general purpose registers(reg)
        # program (ram)
        # self.ram

        self.ram = {
            # base of stack
            0xf3: 0xff
            }

        # make 8 empty registers
        self.reg = [0b00000000] * 8
    
        # stack pointer is the last general register
        self.reg[stack_pointer] = 0xf3

        # special instruction
        self.hlt =0b00000001

        # so we know when a stack overflow occurrs
        self.last_line_in_program = 0b00000000

        # internal registers
        self.pc = 0
        self.ir = 0b00000000
        self.mar = 0b00000000
        self.mdr = 0b00000000
        self.flags = 0b00000000


        # opcode -> function table
        self.command_branch_table = {
            # opcode
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b01000101: self.push,
            0b01000110: self.pop,

            # multiply
            multiply_opcode: self.setup_for_alu
            # 0b10100000: self.add,
            

        }
        self.alu_branch_table = {
            multiply_opcode: self.mul
        }

        # self.stack(for data the program uses outside the registers)
        # self.reg
        # R5 = im
        # R6 = is
        # R7 = sp(stack pointer)
        # self.pc(program counter) location of the ith instruction

        # self.ir(instruction register) the instruction as data

        
        # self.mar(memory address register) the memory address of 
        # what we are reading from or writing to

        # self.mdr (memory data register) the value we are going to write or what we just read


        # 8 bits representing each flag
        # self.fl

        # for example program
        # self.address
        # self.program

        pass

    
    def load2(self):
        """Load a program into memory."""

        self.pc = 0

        # For now, we've just hardcoded a program:

        self.ram = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
    def load(self, file_name):

        with open(file_name,'r') as fh:
            all_lines = fh.readlines()
        # [print(i) for i in all_lines]
        code = []
        ignore_lines = ['#', '\n', '']
        for line in all_lines:
            processed_line = line.split(' ')[0]
            if processed_line not in ignore_lines:
                code.append(int(processed_line, 2))
        # print('code')
        # [print(f'{i:>08b}') for i in code]
        # store code in ram 0 to len(code) - 1

        for i, line in enumerate(code):
            self.ram[i] = line
        self.last_line_in_program = len(code) - 1
    # def add(self):

    #     # use internal registers for this too
    #     reg_a = self.program_entry[self.pc + 1]
    #     reg_b = self.program_entry[self.pc + 2]
        # self.mdr &= 0xff
    #     self.ram_write(reg_a, self.reg[reg_a] + self.reg[reg_b])

    #     # set pc to the next instruction
    #     self.pc += 3
    def get_the_argument_count(self):
        opcode = self.ram[self.pc]
        return (opcode & 0b11000000) >> 6

    def push(self):
        register_number = self.ram[self.pc + 1]
        # decrement the stack pointer
        self.reg[stack_pointer] -= 1
        # copy the value in the given register to the address pointed to by the stack pointer

        # print(register_number)
        register_value = self.reg[register_number]

        # the ram at the value accessed by the stack pointer
        self.ram[ self.reg[stack_pointer] ] = register_value
        self.pc += self.get_the_argument_count() + 1

    def pop(self):

        register_number = self.ram[self.pc + 1]

        # copy the value from the address pointed to be sp to the given register
        self.reg[register_number] = self.ram[ self.reg[stack_pointer] ]

        # increment sp
        self.reg[stack_pointer] += 1

        self.pc += self.get_the_argument_count() + 1

    def ldi(self):
        register = self.ram[self.pc + 1]
        immediate_value = self.ram[self.pc + 2]

        self.reg[register] = immediate_value
        # self.ram_write(register, immediate_value)
        # setting here so the operation is easier to read
        self.mar = register
        self.mdr = immediate_value
        self.pc += self.get_the_argument_count() + 1

    def prn(self):
        register_number = self.ram[self.pc + 1]
        self.mar = register_number
        print(self.reg[register_number])
        self.pc += self.get_the_argument_count() + 1

    def mul(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.mar = reg_a
        # print(reg_a, reg_b)
        self.mdr = self.reg[reg_a] * self.reg[reg_b]
        self.mdr &= 0xff
        self.reg[reg_a] = self.mdr
        # self.ram_write(reg_a, self.mdr)
        self.pc += self.get_the_argument_count() + 1

    def setup_for_alu(self):
        opcode = self.ram[self.pc]
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu(opcode, reg_a, reg_b)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # if op == "ADD":
        #     self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        if op in self.alu_branch_table:
            self.alu_branch_table[op]()
        else:
            raise Exception("Unsupported ALU operation")
    def ram_read(self, address):
        # print(address)
        return self.ram[address]
    # there was something in the specs to use #FF on a result or register
    # to prevent overflow
    def ram_write(self, address, new_value):
        self.ram[address] = new_value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            # assumes everything is in ram
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        print('start cpu')
        counter = 0
        while True:


            # the first insturction is always an opcode
            opcode = self.ram[self.pc]
            self.ir = opcode
            # print(f'{counter}: {self.ir:>08b}')
            if opcode == self.hlt:
                break

            # the argument collecting for the operation is done inside the operation
            # the pc is also advanced inside the operation
            elif opcode in self.command_branch_table:
                self.command_branch_table[opcode]()
            else:
                print(f'{opcode} is an invalid opcode')
                break
            # self.trace()
            counter += 1

        # pass
