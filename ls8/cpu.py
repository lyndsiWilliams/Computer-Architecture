"""CPU functionality."""

import sys

"""Instruction definitions"""
HLT = 0b00000001    # Halt
LDI = 0b10000010    # Set value of a reg to an int
PRN = 0b01000111    # Print
PUSH = 0b01000101   # Push
POP = 0b01000110    # Pop
"""PC mutators"""
CALL = 0b01010000   # Call
RET = 0b00010001    # Return
JMP = 0b01010100    # Jump
JEQ = 0b01010101    # Jump - Equal
JNE = 0b01010110    # Jump - Not equal
"""ALU"""
ADD = 0b10100000    # Add
SUB = 0b10100001    # Subtract
MUL = 0b10100010    # Multiply
DIV = 0b10100011    # Divide
MOD = 0b10100100    # Modulus
CMP = 0b10100111    # Compare
AND = 0b10101000    # Bitwise-AND
NOT = 0b01101001    # Bitwise-NOT
OR  = 0b10101010    # Bitwise-OR
XOR = 0b10101011    # Bitwise-XOR
SHL = 0b10101100    # Shift bits left
SHR = 0b10101101    # Shift bits right

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
        # Stack pointer
        self.reg[7] = 0xF4
        # Flags: 8 bits, if a particular bit is set, that flag is "true"
        self.FL = [0] * 8
        # Program Counter: the index into memory of the currently-executing instruction
        self.pc = 0
        # Boolean to start/stop the program
        self.running = False
        # Branch table
        self.branchtable = {}
        # Instruction branches
        self.branchtable[HLT] = self.HLT        # Halt
        self.branchtable[LDI] = self.LDI        # Set value of a reg to an int
        self.branchtable[PRN] = self.PRN        # Print
        self.branchtable[PUSH] = self.PUSH      # Push
        self.branchtable[POP] = self.POP        # Pop
        self.branchtable[CALL] = self.CALL      # Call
        self.branchtable[RET] = self.RET        # Return
        self.branchtable[JMP] = self.JMP        # Jump
        self.branchtable[JEQ] = self.JEQ        # Jump - Equal
        self.branchtable[JNE] = self.JNE        # Jump - not equal
        self.branchtable[ADD] = self.ADD        # Add
        self.branchtable[SUB] = self.SUB        # Subtract
        self.branchtable[MUL] = self.MUL        # Multiply
        self.branchtable[DIV] = self.DIV        # Divide
        self.branchtable[MOD] = self.MOD        # Modulus
        self.branchtable[CMP] = self.CMP        # Compare
        self.branchtable[AND] = self.AND        # Bitwise-AND
        self.branchtable[NOT] = self.NOT        # Bitwise-NOT
        self.branchtable[OR] = self.OR          # Bitwise-OR
        self.branchtable[XOR] = self.XOR        # Bitwise-XOR
        self.branchtable[SHL] = self.SHL        # Shift bits left
        self.branchtable[SHR] = self.SHR        # Shift bits right

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
        # Divide the value in the first register by the value in the second,
        # storing the remainder of the result in registerA.
        elif op == "MOD":
            # If the value in the second register is 0...
            if reg_b == 0:
                # Print an error message and halt.
                print("Second value can not be 0")
                sys.exit()
            # Otherwise, do the modulus operation
            else:
                self.reg[reg_a] %= self.reg[reg_b]
        # Compare the values in two registers
        #   Sets the flag bits: 00000LGE
        #                            <>=
        elif op == "CMP":
            # If equal, set E to 1 (true)
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL[-1] = 1
            # If a > b, set G to 1 (true)
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[-2] = 1
            # If a < b, set L to 1 (true)
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL[-3] = 1
        # Bitwise-AND the values in registerA and registerB, then store the result in registerA.
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        # Perform a bitwise-NOT on the value in a register, storing the result in the register.
        elif op == "NOT":
            self.reg[reg_a] = ~(self.reg[reg_a])
        # Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        # Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
        #   Bitwise XOR sets the bits in the result to 1 if either, but not both,
        #   of the corresponding bits in the two operands is 1.
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        # Shift the value in registerA left by the number of bits specified in registerB
        # filling the low bits with 0
        elif op == "SHL":
            self.reg[reg_a] = (self.reg[reg_a] << self.reg[reg_b])
        # Shift the value in registerA right by the number of bits specified in registerB
        # filling the high bits with 0.
        elif op == "SHR":
            self.reg[reg_a] = (self.reg[reg_a] >> self.reg[reg_b])
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

    def ram_write(self, MDR, MAR):
        # Value = MDR = Memory Data Register:
            # holds the value to write or the value just read
        # This sets the parameter value (MDR) at the parameter address in memory (MAR)
        self.reg[MAR] = MDR

    """
    ---------- Instruction functions ----------
    """
    # Halt the CPU (and exit the emulator)
    def HLT(self):
        self.running = False

    # Set the value of a register to an integer
    def LDI(self):
        # Set and store the address (+1 bit) and value (+1 bit) in ram
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        # Run the ram_write helper function with the current
        # address/value as parameters
        self.ram_write(value, address)
        # Increment the pc by 3
        # because this is a 3-bit operation
        self.pc += 3

    # Print to the console the decimal integer value
    # that is stored in the given register.
    def PRN(self):
        # Set the address stored in ram (1 bit)
        address = self.ram[self.pc + 1]
        # Run the ram_read helper function with
        # the current address and print it
        print(self.ram_read(address))
        # Increment the pc by 2 (2-bit operation)
        self.pc += 2

    def PUSH(self):
        # Decrement the stack pointer
        self.reg[7] -= 1
        # Get value from register
        reg_num = self.ram[self.pc + 1]
        # Value to push
        value = self.reg[reg_num]
        # Store it on the stack
        top_of_stack_address = self.reg[7]
        # Push the value from the register to the RAM
        self.ram[top_of_stack_address] = value
        # Increment the pc by 2 (2-bit operation)
        self.pc += 2

    def POP(self):
        # Point at the top of the stack
        top_of_stack_address = self.reg[7]
        # Value to pop
        value = self.ram[top_of_stack_address]
        # Get value from register
        reg_num = self.ram[self.pc + 1]
        # Overwrite the register number's value to the popped value
        self.reg[reg_num] = value
        # Increment the stack pointer
        self.reg[7] += 1
        # Increment the pc by 2 (2-bit operation)
        self.pc += 2

    """
    ---------- ALU functions ----------
    """
    # Add the value in two registers and
    # store the result in registerA.
    def ADD(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("ADD", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Subtract the value in the second register from the first,
    # storing the result in registerA.
    def SUB(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("SUB", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Multiply the values in two registers together and
    # store the result in registerA.
    def MUL(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("MUL", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Divide the value in the first register by the value in the second,
    # storing the result in registerA.
    def DIV(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("DIV", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Divide the value in the first register by the value in the second,
    # storing the remainder of the result in registerA.
    def MOD(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("MOD", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Compare the values in two registers
    def CMP(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("CMP", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Bitwise-AND the values in registerA and registerB, then store the result in registerA.
    def AND(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("AND", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Perform a bitwise-NOT on the value in a register, storing the result in the register.
    def NOT(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("NOT", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
    def OR(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("OR", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
    #   Bitwise XOR sets the bits in the result to 1 if either, but not both,
    #   of the corresponding bits in the two operands is 1.
    def XOR(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("XOR", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Shift the value in registerA left by the number of bits specified in registerB
    # filling the low bits with 0
    def SHL(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("SHL", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    # Shift the value in registerA right by the number of bits specified in registerB
    # filling the high bits with 0.
    def SHR(self):
        # Set and store the first and second parameter values in ram
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        # Call the ALU method and pass it the operation and values
        self.alu("SHR", reg_a, reg_b)
        # Increment the pc by 3 (3-bit operation)
        self.pc += 3

    """
    ---------- PC mutator functions ----------
    """
    # Calls a subroutine (function) at the address stored in the register
    def CALL(self):
        # Push return address
        ret_address = self.pc + 2
        # Decrement the stack pointer
        self.reg[7] -= 1
        self.ram[self.reg[7]] = ret_address
        # Set the PC to the address stored in the given register
        regnum = self.ram[self.pc + 1]
        subroutine_address = self.reg[regnum]
        self.pc = subroutine_address

    # Pop the value from the top of the stack and store it in the PC
    def RET(self):
        # Pop the return addr off the stack
        ret_address = self.ram[self.reg[7]]
        self.reg[7] += 1
        # Set the PC to it
        self.pc = ret_address

    # Set the PC to the address stored in the given register
    def JMP(self):
        # Grab the address from memory
        memory_address = self.ram[self.pc + 1]
        # Set the PC to it
        self.pc = self.reg[memory_address]

    # If equal flag is set (true), jump to the address stored in the given register
    def JEQ(self):
        # If the E flag is marked 1 (true)
        if self.FL[-1] == 1:
            # Set the address to jump to
            address = self.ram[self.pc + 1]
            # Set the new address
            new_address = self.reg[address]
            # Set the PC to the new address
            self.pc = new_address
        # If it's set to false, continue by only incrementing the PC counter
        # (because this operation was still run)
        else:
            # 2 bits!
            self.pc += 2

    # If E flag is clear (false, 0), jump to the address stored in the given register.
    def JNE(self):
        # If the E flag is marked 0 (false)
        if self.FL[-1] == 0:
            # Set the address to jump to
            address = self.ram[self.pc + 1]
            # Set the new address
            new_address = self.reg[address]
            # Set the PC to the new address
            self.pc = new_address
        # If it's set to false, continue by only incrementing the PC counter
        # (because this operation was still run)
        else:
            # 2 bits!
            self.pc += 2



    """
    ---------- Run the CPU ----------
    """
    def run(self):
        # Start the program
        self.running = True

        while self.running:
            # Read the memory address that's stored in the register's PC
            # And store the result in the Instruction Register (ir)
            ir = self.ram[self.pc]

            if ir and 0b00010000 == 0:
                self.pc += (ir >> 6) + 1
            else:
                # Find the ir method in the branchtable and execute it
                self.branchtable[ir]()