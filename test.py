import ctypes
from os import path
from sys import stderr

vdex = ctypes.CDLL(path.join(path.dirname(__file__),
        "target/debug/libvdex_web.so"))

class Opaque (ctypes.Structure):
    _fields_ = []

vdex.vdex_pokemon.restype = ctypes.POINTER(Opaque)
vdex.vdex_pokemon.argtypes = [ctypes.c_uint16, ctypes.c_size_t]

VDEX_PERMANENT_STATS = (ctypes.c_size_t
        .in_dll(vdex, "VDEX_PERMANENT_STATS").value)

class VDexPokemonDetails (ctypes.Structure):
    _fields_ = [
            ("id", ctypes.c_uint16),
            ("ability1", ctypes.c_uint8),
            ("has_ability2", ctypes.c_uint8),
            ("ability2", ctypes.c_uint8),
            ("has_hidden_ability", ctypes.c_uint8),
            ("hidden_ability", ctypes.c_uint8),
            ("stats", ctypes.c_uint8),
            ("type1", ctypes.c_uint8),
            ("has_type2", ctypes.c_uint8),
            ("type2", ctypes.c_uint8),
            ]

vdex.vdex_pokemon_details.restype = VDexPokemonDetails
vdex.vdex_pokemon_details.argtypes = [ctypes.POINTER(Opaque)]

def main():
    pokemon = vdex.vdex_pokemon(0, 0)
    address = ctypes.addressof(pokemon.contents)
    print("pointer (Python): 0x{:x}".format(address), file=stderr)
    details = vdex.vdex_pokemon_details(pokemon)
    print("ability: {}".format(details.ability1), file=stderr)

if __name__ == '__main__':
    main()
