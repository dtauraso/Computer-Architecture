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

        self.ram = []
        # stack pointer is the last gen register

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
            0b10100010: self.mul
            # 0b10100000: self.add,
            

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
        [print(i) for i in all_lines]
        code = []
        for line in all_lines:
            processed_line = line.split(' ')[0]
            if processed_line != '#' and processed_line != '\n':
                code.append(int(processed_line, 2))
        print('code')
        [print(f'{i:>08b}') for i in code]
        self.ram = code
    # def add(self):

    #     # use internal registers for this too
    #     reg_a = self.program_entry[self.pc + 1]
    #     reg_b = self.program_entry[self.pc + 2]
        # self.mdr &= 0xff
    #     self.ram_write(reg_a, self.reg[reg_a] + self.reg[reg_b])

    #     # set pc to the next instruction
    #     self.pc += 3
    def mul(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.mar = reg_a
        print(reg_a, reg_b)
        self.mdr = self.reg[reg_a] * self.reg[reg_b]
        self.mdr &= 0xff
        self.reg[reg_a] = self.mdr
        # self.ram_write(reg_a, self.mdr)
        self.pc += 3

    def ldi(self):
        register = self.ram[self.pc + 1]
        immediate_value = self.ram[self.pc + 2]

        self.reg[register] = immediate_value
        # self.ram_write(register, immediate_value)
        # setting here so the operation is easier to read
        self.mar = register
        self.mdr = immediate_value
        self.pc += 3
    def prn(self):
        register_number = self.ram[self.pc + 1]
        self.mar = register_number
        print(self.reg[register_number])
        self.pc += 2
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")
    def ram_read(self, address):
        print(address)
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
            print(f'{counter}: {self.ir:>08b}')
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
