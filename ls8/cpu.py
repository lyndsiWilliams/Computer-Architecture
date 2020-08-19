"""CPU functionality."""

import sys

"""Instruction definitions"""
HLT = 0b00000001    # Halt
LDI = 0b10000010    # Set value of a reg to an int
PRN = 0b01000111    # Print
"""ALU"""
ADD = 0b10100000    # Add
SUB = 0b10100001    # Subtract
MUL = 0b10100010    # Multiply
DIV = 0b10100011    # Divide

"""
    AA-B-C-DD
    ---------
AA:   Number of operands for this opcode, 0-2
B:    1 if this is an ALU operation
C:    1 if this instruction sets the PC
DDDD: Instruction identifier
"""

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Holds 256 bytes of memory
        self.ram = [0] * 256
        # 8 general-purpose registors
        self.reg = [0] * 8
        # Program Counter: the index into memory of the currently-executing instruction
        self.pc = 0
        # Boolean to start/stop the program
        self.running = False

    def load(self):
        """Load a program into memory."""

        address = 0

        # If there are less than 2 arguments entered, return error
        if len(sys.argv) != 2:
            print("Usage: comp.py program_name")
            sys.exit(1)
        
        # Otherwise, go on with the load method
        try:
            # Open the file entered
            with open(sys.argv[1]) as f:
                # Loop through the lines in the file
                for line in f:
                    # Remove all white space
                    line = line.strip()
                    # Split into a workable list
                    temp = line.split()

                    # Bypass blank lines
                    if len(temp) == 0:
                        continue

                    # Bypass comments
                    if temp[0][0] == '#':
                        continue

                    # Now that the file is cleaned up and
                    # the unneccesary stuff is bypassed,
                    # continue with the load process
                    try:
                        # Set the address of the ram to be
                        # JUST the binary part of the file
                        self.ram[address] = int(temp[0], 2)

                    # Set an error to catch invalid numbers
                    except ValueError:
                        print(f"Invalid number: {temp[0]}")
                        sys.exit(1)

                    # Increment the address by 1
                    address += 1

        # Set an error to catch invalid file
        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(2)

        # If the address is zero, return error and exit
        if address == 0:
            print("Program was empty!")
            sys.exit(3)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # Add the value in two registers and
        # store the result in registerA.
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # Subtract the value in the second register from the first,
        # storing the result in registerA.
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        # Multiply the values in two registers together and
        # store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # Divide the value in the first register by the value in the second,
        # storing the result in registerA.
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

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

    """
    ---------- Ram functions ----------
    """
    def ram_read(self, MAR):
        # Address = MAR = Memory Address Register:
            # holds the memory address we're reading or writing
        # This returns the register at the parameter address
        return self.reg[MAR]

    def ram_write(self, MAR, MDR):
        # Value = MDR = Memory Data Register:
            # holds the value to write or the value just read
        # This sets the parameter value (MDR) at the parameter address in memory (MAR)
        self.reg[MAR] = MDR

    def run(self):
        """Run the CPU."""
        # Start the program
        self.running = True

        while self.running:
            # Read the memory address that's stored in the register's PC
            # And store the result in the Instruction Register (ir)
            ir = self.ram[self.pc]

            # Halt the CPU (and exit the emulator)
            if ir == HLT:
                self.running = False

            # Set the value of a register to an integer
            elif ir == LDI:
                # Set and store the address (+1 bit) and value (+1 bit) in ram
                address = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                # Run the ram_write helper function with the current
                # address/value as parameters
                self.ram_write(address, value)
                # Increment the pc by 3
                # because this is a 3-bit operation
                self.pc += 3

            # Print to the console the decimal integer value
            # that is stored in the given register.
            elif ir == PRN:
                # Set the address stored in ram (1 bit)
                address = self.ram[self.pc + 1]
                # Run the ram_read helper function with
                # the current address and print it
                print(self.ram_read(address))
                # Increment the pc by 2 (2-bit operation)
                self.pc += 2

            # Multiply the values in two registers together and
            # store the result in registerA.
            elif ir == MUL:
                # Set and store the first and second parameter values in ram
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                # Call the ALU method and pass it the operation and values
                self.alu("MUL", reg_a, reg_b)
                # Increment the pc by 3 (3-bit operation)
                self.pc += 3

