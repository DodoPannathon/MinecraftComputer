import sys
from rcon import whrite_to_ram

args = sys.argv[1:]
asmfile = args[0] if len(args) >= 1 else ".asm/test.asm"

def parsenum(word: str) -> int:
    try:
        output = 0
        if(word.startswith('0b')): output = int(word[2:], 2)
        elif(word.startswith('0x')): output = int(word[2:], 16)
        else: output = int(word, 10)
        if output < 0:
            output = abs(output)
            output = (output ^ 0b11111111) + 1
            return output
        else:return output
    except:
        lookup = symboltable[word]
        if lookup is None:
            raise KeyError("Unknown symbol")
        return lookup

def getregisternum(r: str) -> int:
    return int(r[1:])

def setrd(r: str) -> int:
    return getregisternum(r) << 9

def setra(r: str) -> int:
    return getregisternum(r) << 3

def setrb(r: str) -> int:
    return getregisternum(r)

romdata = [0 for i in range(256)]
linecounter = 0
symboltable = dict()
instructioncounter = 0

try:
    with open(asmfile) as file:
        lines = file.read().split("\n")

        for line in lines:
            if line.strip() == '':continue
            line = line.split(";")[0].strip().lower().split(":")
            if len(line) > 1:
                symbol = line[0]
                symboltable[symbol] = linecounter
            linecounter += 1

        linecounter = 0

        for line in lines:
            
            linecounter += 1

            if line.strip() == '': continue
            line = line.split(";")[0].strip().lower().split(":")[-1]
            instruction = line.split(" ")

            # print(f"'{line}'")
            # print(instruction[0])

            binary = 0x0000
            opcode = instruction[0]
            match opcode:
                case 'nop': binary |= 0x0000
                case 'hlt': binary |= 0x1000
                case 'ldi': binary |= 0x2000 | setrd(instruction[1]) | parsenum(instruction[2])
                case 'ldm': binary |= 0x3000 | setrd(instruction[1]) | setrb('r7')
                case 'stm': binary |= 0x4000 | setra(instruction[1]) | setrb('r7')
                case 'jmp': binary |= 0x5000 | parsenum(instruction[1])
                case 'bin': binary |= 0x6000 | parsenum(instruction[1])
                case 'biz': binary |= 0x7000 | parsenum(instruction[1])
                case 'add': binary |= 0x8000 | setrd(instruction[1]) | setra(instruction[2]) | setrb(instruction[3])
                case 'sub': binary |= 0x9000 | setrd(instruction[1]) | setra(instruction[2]) | setrb(instruction[3])
                case 'or' : binary |= 0xa000 | setrd(instruction[1]) | setra(instruction[2]) | setrb(instruction[3])
                case 'and': binary |= 0xb000 | setrd(instruction[1]) | setra(instruction[2]) | setrb(instruction[3])
                case 'xor': binary |= 0xc000 | setrd(instruction[1]) | setra(instruction[2]) | setrb(instruction[3])
                case 'inc': binary |= 0xd000 | setrd(instruction[1]) | setra(instruction[2]) | setrb('r0')
                case 'dec': binary |= 0xe000 | setrd(instruction[1]) | setra(instruction[2]) | setrb('r0')
                case 'shr': binary |= 0xf000 | setrd(instruction[1]) | setra(instruction[2]) | setrb('r0')

            # binstr = bin(binary)[2:]
            # print('0' * (16 - len(binstr)) + binstr)

            romdata[instructioncounter] = binary
            instructioncounter += 1

except FileNotFoundError:
    print(f"\033[31mNo file name {asmfile}\033[0m")
    exit()

except IndexError:
    print(f"\033[31msyntax error at line {linecounter}\033[0m")
    exit()

except KeyError as e:
    print(f"/033[31m{e} at line {linecounter}")
    exit()

# for data in romdata:
#     binstr = bin(data)[2:]
#     print('0' * (16 - len(binstr)) + binstr)
#     if (data >> 12) == 1: break

whrite_to_ram(romdata)