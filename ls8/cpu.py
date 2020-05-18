"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # special registers
        # general purpose registers(reg)
        # program (ram)
        # self.ram
        self.program_entry = []
        self.stack = []

        # make 8 empty registers
        self.reg = [0b00000000] * 8

        # special instruction
        self.hlt =0b00000001

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
            0b10100000: self.add,
            

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

    def load(self):
        """Load a program into memory."""

        self.pc = 0

        # For now, we've just hardcoded a program:

        self.program_entry = [
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

    def add(self):

        # use internal registers for this too
        reg_a = self.program_entry[self.pc + 1]
        reg_b = self.program_entry[self.pc + 2]

        self.ram_write(reg_a, self.reg[reg_a] + self.reg[reg_b])

        # set pc to the next instruction
        self.pc += 3
    def ldi(self):
        register = self.program_entry[self.pc + 1]
        immediate_value = self.program_entry[self.pc + 2]

        self.ram_write(register, immediate_value)
        # setting here so the operation is easier to read
        self.mar = register
        self.mdr = immediate_value
        self.pc += 3
    def prn(self):
        register_number = self.program_entry[self.pc + 1]
        self.mar = register_number
        print(self.ram_read(register_number))
        self.pc += 2
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")
    def ram_read(self, address):
        return self.reg[address]
    
    def ram_write(self, address, new_value):
        self.reg[address] = new_value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while True:


            # the first insturction is always an opcode
            opcode = self.program_entry[self.pc]
            self.ir = opcode
            if opcode == self.hlt:
                break

            # the argument collecting for the operation is done inside the operation
            # the pc is also advanced inside the operation
            elif opcode in self.command_branch_table:
                self.command_branch_table[opcode]()
            else:
                print(f'{opcode} is an invalid opcode')

        # pass
