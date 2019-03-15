from ctypes import *
from os import path

P = POINTER
vdex = CDLL(path.join(path.dirname(__file__), "target/debug/libvdex_web.so"))

def _f(name, restype, *argtypes, errcheck=None):
    f = getattr(vdex, "vdex_" + name)
    f.restype = restype
    f.argtypes = argtypes
    if errcheck is not None:
        f.errcheck = errcheck
    globals().put(name, f)

def _c(name, typ):
    globals().put(name, typ.in_dll(vdex, "VDEX_" + name))

_f("free_name", None, P(c_char_p))

# Pokedex

class Pokedex (Structure):
    _fields_ = [("ptr", c_void_p)]

_f("load_dex", Pokedex)
_f("free_dex", None, P(Pokedex))

# Types

Type = c_uint8
Efficacy = c_int8
_c("TYPE_COUNT", c_size_t)
_f("type_list", P(Type * TYPE_COUNT.value))
_f("type_name", c_char_p, Type)

_c("INVALID_DAMAGE_TYPE", Efficacy)
_c("INVALID_TARGET_TYPE", Efficacy)

class InvalidTypeError (Exception):
    pass

def _efficacy_errcheck(result, func, arguments):
    if result == INVALID_DAMAGE_TYPE:
        raise InvalidTypeError("Invalid damage type: {}".format(arguments[1]))
    elif result == INVALID_TARGET_TYPE:
        raise InvalidTypeError("Invalid target type: {}".format(arguments[2]))
    else:
        return result

_f("efficacy", Efficacy, Pokedex, Type, Type, errcheck=_efficacy_errcheck)

# Items

Item = c_uint16

class ItemIter (Structure):
    _fields_ = [("ptr", c_void_p)]

_f("item_iter", ItemIter, Pokedex)
_c("ITEM_ITER_END", Item)
_f("item_next", Item, ItemIter)
_f("free_item_iter", None, P(ItemIter))
_f("item_name", c_char_p, Pokedex, Item)

# Item Details

ItemCategory = c_uint8
Boolean = c_uint8
Pocket = c_uint8
FlingEffect = c_uint8
ItemFlags = c_uint8
Flavor = c_uint8

def _load_item_flag_constants(*names):
    for name in names:
        _c("ITEM_FLAG_" + name.strip(), ItemFlags)

_load_item_flag_constants("""
 COUNTABLE CONSUMABLE USABLE_OVERWORLD USABLE_IN_BATTLE
 HOLDABLE HOLDABLE_PASSIVE HOLDABLE_ACTIVE UNDERGROUND
""".strip().split(" "))

_c("NO_DOMINANT_FLAVOR", Flavor)

class ItemDetails (Structure):
    _fields_ = [
            ("category", ItemCategory),
            ("unused", Boolean),
            ("pocket", Pocket),
            ("cost", c_uint16),
            ("fling_power", c_uint8),
            ("fling_effect", FlingEffect),
            ("flags", ItemFlags),
            ("natural_gift_power", c_uint8),
            ("natural_gift_type", Type),
            ("flavor", Flavor),
            ]

_f("item_details", ItemDetails, Pokedex, Item)

# Moves
