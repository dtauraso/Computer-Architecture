"""CPU functionality."""

import sys

# for branch table in ALU
multiply_opcode = 0b10100010
add_opcode = 0b10100000

# last 3 general purpose registers
interrupt_mask = 5
interrupt_status = 6
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

        # 2 interrupt branch functions
        # 1 interrupt setup in run
        # 1 interrupt detector flag
        # 1 table of interrupts
        # opcode -> function table
        self.command_branch_table = {
            # opcode
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b01000101: self.push,
            0b01010000: self.call,
            0b01000110: self.pop,
            0b00010001: self.ret,

            # tell us the interrupt to process
            0b01010010: self.interupt,
            0b00010011: self.iret,

            0b10100111: self.cmp,
            0b01010100: self.jmp,
            0b01010101: self.jeq,
            0b01010110: self.jne,


            # multiply
            multiply_opcode: self.setup_for_alu,
            add_opcode: self.setup_for_alu
            # 0b10100000: self.add,
            

        }
        self.alu_branch_table = {
            multiply_opcode: self.mul,
            add_opcode: self.add
        }

        self.interrupt_vector_table = {
            0b00000001: 'timer interrupt',
            0b00000010: 'keyboard interrupt'
        }
        # Don't know how to setup interrupts yet
        self.active_interrupts = False

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

    
    def load(self, file_name):

        with open(file_name,'r') as fh:
            all_lines = fh.readlines()
        # [print(i) for i in all_lines]
        code = []
        ignore_lines = ['#', '\n', '', '#\n']
        for line in all_lines:
            processed_line = line.split(' ')[0]
            # print(f'|{processed_line}|')
            if processed_line not in ignore_lines:
                code.append(int(processed_line, 2))
        # print('code', code)
        # [print(f'{i:>08b}') for i in code]
        # store code in ram 0 to len(code) - 1

        for i, line in enumerate(code):
            self.ram[i] = line
        self.last_line_in_program = len(code) - 1
    def get_the_argument_count(self):
        opcode = self.ram[self.pc]
        # right shift the highest 2 bits by 6
        return (opcode & 0b11000000) >> 6

    def push(self):
        register_number = self.ram[self.pc + 1]

        if self.reg[stack_pointer] - 1 == self.last_line_in_program:
            print('we have a stack overflow')

        # decrement the stack pointer
        self.reg[stack_pointer] -= 1
        # copy the value in the given register to the address pointed to by the stack pointer

        # print(register_number)
        register_value = self.reg[register_number]

        # the ram at the value accessed by the stack pointer
        self.ram[ self.reg[stack_pointer] ] = register_value
        self.pc += self.get_the_argument_count() + 1

    def call(self):
        register_number = self.ram[self.pc + 1]

        # the address of the next instruction is pushed onto the stack

        address_of_next_instruction = self.pc + 2

        # push
        self.reg[stack_pointer] -= 1

        self.ram[ self.reg[stack_pointer] ] = address_of_next_instruction

        # save the value in the given register to the program counter
        self.pc = self.reg[register_number]


    def pop(self):

        register_number = self.ram[self.pc + 1]

        # copy the value from the address pointed to be sp to the given register
        self.reg[register_number] = self.ram[ self.reg[stack_pointer] ]

        # increment sp
        self.reg[stack_pointer] += 1

        self.pc += self.get_the_argument_count() + 1

    def ret(self):

        # pop the value from the top of the stack and store it in the pc
        self.pc = self.ram[ self.reg[stack_pointer] ]

        #increment sp
        self.reg[stack_pointer] += 1

    # not tested(not used)
    def interupt(self):
        register_number = self.ram[self.pc + 1]
        interrupt_number = self.reg[register_number]

        _nth_th_bit = 0b00000001 << interrupt_number

        # turn on the interrupt bit without modifying
        # the other bits
        self.reg[interrupt_status] |= _nth_th_bit

        # move cp?

    # not tested
    def iret(self):

        # pop the registers
        ith_register = 6
        while ith_register >= 0:

            self.reg[ith_register] = self.ram[ self.reg[stack_pointer] ]

            #increment sp
            self.reg[stack_pointer] += 1
        
        # pop the flag register
        self.fl = self.ram[ self.reg[stack_pointer] ]
        self.reg[stack_pointer] += 1

        # pop the pc
        self.pc = self.ram[ self.reg[stack_pointer] ]

        self.reg[stack_pointer] += 1


        # reactivate interrupts
        self.active_interrupts = True

    def update_comparison_flag(self, flag):
        if flag == 'equal':
            equal_flag = 0b00000001

            # add the bit
            self.flags |= equal_flag

            # deactivate the other 2 bits
            self.flags &= equal_flag

        if flag == 'greater than':

            greater_than_flag = 0b00000010

            # add the bit
            self.flags |= greater_than_flag

            # deactivate the other 2 bits
            self.flags &= greater_than_flag
    
        if flag == 'less than':

            less_than_flag = 0b00000100

            # add the bit
            self.flags |= less_than_flag

            # deactivate the other 2 bits
            self.flags &= less_than_flag

    def cmp(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        # we only want the comparison bit we are looking at to be on
        if(self.reg[reg_a] == self.reg[reg_b]):

            self.update_comparison_flag('equal')

        elif(self.reg[reg_a] > self.reg[reg_b]):

            self.update_comparison_flag('greater than')

        elif(self.reg[reg_a] < self.reg[reg_b]):

            self.update_comparison_flag('less than')

        self.pc += self.get_the_argument_count() + 1

    def jmp(self):
        register_number = self.ram[self.pc + 1]

        self.pc = self.reg[register_number]

    def jeq(self):
        register_number = self.ram[self.pc + 1]
        equal_flag = 0b00000001
        if self.flags & equal_flag:

            self.pc = self.reg[register_number]
        else:
            self.pc += self.get_the_argument_count() + 1
    def jne(self):
        register_number = self.ram[self.pc + 1]
        equal_flag = 0b00000001

        if self.flags & equal_flag == 0b00000000:

            self.pc = self.reg[register_number]
        else:
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

    def add(self):

        # use internal registers for this too
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.mar = reg_a
        self.mdr = self.reg[reg_a] + self.reg[reg_b]


        self.mdr &= 0xff
        self.reg[reg_a] = self.mdr

        # set pc to the next instruction
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

        print(f' {self.flags:>08b}')
        print()

    def run(self):
        """Run the CPU."""
        print('start cpu')
        counter = 0
        while True:

            # when interrupt occurres from an external source
            # external source:
                # do we look for keyboard input before checking the instructions?

            # or from an interrupt instruction
                # figure out what interupt it was
            # if it was an interrupt
                # turn off further interrupts(self.active_interrupts)
                # save data from registers to the stack
                # set pc to handler address

            #             if self.active_interrupts:
            #     # figure out what interrupt whould be 
            # else:
            # just for the interrupt instruction
            # How do I know when the interrupt may occurr?
            # Is this supposed to detect an interrupt after the command was run
            # last round?
            if self.active_interrupts:
                maskedInterrupts = self.reg[interrupt_mask] & self.reg[interrupt_status]

                # find the first bit set in
                i = 0b00000001
                while (maskedInterrupts & i) == 0:
                    i <<= 1

                # an_interrupt_is_set
                if(maskedInterrupts & i) > 0:
                    self.active_interrupts = False
                    self.reg[interrupt_status] = 0b00000000

                    # push pc to stack
                    self.reg[stack_pointer] -= 1
                    self.ram[ self.reg[stack_pointer] ] = self.pc
                    
                    # push fl to stack
                    self.reg[stack_pointer] -= 1
                    self.ram[ self.reg[stack_pointer] ] = self.pc

                    # push registers to memory
                    ith_register = 0
                    while ith_register < 6:

                        # decrement sp
                        self.reg[stack_pointer] -= 1

                        self.reg[ith_register] = self.ram[ self.reg[stack_pointer] ]

                        # find the correct interrupt handler

                        # self.interrupt_vector_table[maskedInterrupts & i]
                        # set the pc to the handler address
                        # how?
                        # where?

            else:

                # the first insturction is always an opcode
                opcode = self.ram[self.pc]
                self.ir = opcode
                # if counter == 10:
                #     exit()
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
