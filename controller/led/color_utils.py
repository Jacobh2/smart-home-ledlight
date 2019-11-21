from colorsys import rgb_to_hsv


def dec_to_hex(red, green, blue):
    return "#{r}{g}{b}".format(
        r=hex(red)[2:].zfill(2), g=hex(green)[2:].zfill(2), b=hex(blue)[2:].zfill(2)
    )


def rgb_dec_to_hex(value):
    return hex(value)[2:].rjust(6, "0")


def hex_to_rgb_dec(value):
    return int("0x{}".format(value), 0)


def split_hex(value):
    n = 2
    return [value[i : i + n] for i in range(0, len(value), n)]
