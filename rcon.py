from mcrcon import MCRcon

class position:
    def __init__(self,x,y,z): 
        self.x = x
        self.y = y
        self.z = z

def whrite_to_ram(romdata: list[int]):
    origin_position_input = input('Enter position you want to operater: ').split(' ')
    origin_position = position(origin_position_input[0],origin_position_input[1],origin_position_input[2])

    # romdata = [i for i in range(256)]
    # for i in range(len(romdata)):
    #     print(romdata[i])

    try:
        with MCRcon("localhost","12345678") as mcr:

            width = 14
            offset = 5

            for i in range(len(romdata)):
                row = (i & 0b11000000) >> 6
                depth = (i & 0b00011111)
                ditection = ((i & 0b00100000) >> 4) - 1
                nudge = (i & 0b00000001)

                x = int(origin_position.x) + width * row + (offset - nudge) * ditection + offset
                z = int(origin_position.z) + 2 * depth

                data = romdata[i]

                for j in range(16):
                    y = int(origin_position.y) + 2 * j
                    bit = data & 0b0000_0000_0000_0001
                    resp = mcr.command(f"/fill {x} {y} {z} {x} {y} {z} {"minecraft:composter[level=1]" if bit == 1 else "minecraft:black_concrete"}")
                    print(resp)
                    data >>= 1

                if (romdata[i] >> 12) == 1: break
    
    except ConnectionRefusedError:
        print("\033[31mfailed to connect server\033[0m")