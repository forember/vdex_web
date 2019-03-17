from ctypes import *
from os import path
import re

P = POINTER
vdex = CDLL(path.join(path.dirname(__file__), "target/debug/libvdex_web.so"))

def _f(name, restype, *argtypes, errcheck=None):
    f = getattr(vdex, "vdex_" + name.lstrip("_"))
    f.restype = restype
    f.argtypes = argtypes
    if errcheck is not None:
        f.errcheck = errcheck
    globals()[name] = f

def _c(name, typ):
    globals()[name] = typ.in_dll(vdex, "VDEX_" + name.lstrip("_")).value

_f("_free_name", None, P(P(c_char)))

def _cstr_errcheck(result, func, arguments):
    if not result:
        return None
    buf = string_at(addressof(result.contents))
    _free_name(result)
    return buf

def _e(name, typ=c_uint8):
    globals()[name] = typ
    lname = re.sub(r"(?!^)([A-Z])", r"_\1", name).lower()
    uname = lname.upper()
    _c(uname + "_COUNT", c_size_t)
    _f(lname + "_list", typ)
    _f(lname + "_name", P(c_char), typ, errcheck=_cstr_errcheck)

def _cg(base, typ, names):
    for name in names.strip().split(" "):
        _c(base + "_" + name.strip(), typ)

# Enums

_e("Ability")
_e("Efficacy", c_int8)
_e("Nature")
_e("Type")

_e("ItemCategory")
_e("Flavor")
_e("FlingEffect")
_e("Pocket")

_e("Ailment", c_int8)
_e("BattleStyle")
_e("MoveCategory")
_e("DamageClass")
_e("MoveEffect", c_uint16)
_e("LearnMethod")
_e("MoveTarget")

_e("EggGroup")
_e("EvolutionTrigger")
_e("Gender")

_e("Generation")
_e("Version")
_e("VersionGroup")

# Efficacy

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

_f("efficacy", Efficacy, Type, Type, errcheck=_efficacy_errcheck)

# Items

Item = c_uint16

class _ItemIter (Structure):
    _fields_ = [("ptr", c_void_p)]

_f("_item_iter", _ItemIter)
_c("_ITEM_ITER_END", Item)
_f("_item_next", Item, _ItemIter)
_f("_free_item_iter", None, P(_ItemIter))

class ItemIter:
    def __init__(self):
        self._iterator = _item_iter()

    def __iter__(self):
        return self

    def __next__(self):
        if type(self._iterator) != _ItemIter:
            raise StopIteration
        item = _item_next(self._iterator)
        if item == _ITEM_ITER_END:
            raise StopIteration
        return item

    def __del__(self):
        if self._iterator is not None:
            _free_item_iter(self._iterator)
            self._iterator = None

item_iter = ItemIter

_f("item_name", P(c_char), Item, errcheck=_cstr_errcheck)

# Item Details

Boolean = c_uint8

ItemFlags = c_uint8
_cg("ITEM_FLAG", ItemFlags, """
 COUNTABLE CONSUMABLE USABLE_OVERWORLD USABLE_IN_BATTLE
 HOLDABLE HOLDABLE_PASSIVE HOLDABLE_ACTIVE UNDERGROUND
""")

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

_f("item_details", ItemDetails, Item)

# Moves

Move = c_uint16
_c("MOVE_COUNT", Move)
_f("move_name", P(c_char), Move, errcheck=_cstr_errcheck)

# Move Details

_c("NEVER_MISSES", c_uint8)

_c("CHANGEABLE_STATS", c_size_t)
_cg("STAT_CHANGE", c_size_t, """
 ATTACK DEFENSE SPEED SPECIAL_ATTACK SPECIAL_DEFENSE ACCURACY EVASION
""")

MoveFlags = c_uint16
_cg("MOVE_FLAG", MoveFlags, """
 CONTACT CHARGE RECHARGE PROTECT REFLECTABLE SNATCH MIRROR
 PUNCH SOUND GRAVITY DEFROST DISTANCE HEAL AUTHENTIC
""")

class MoveDetails (Structure):
    _fields_ = [
            ("generation", Generation),
            ("typ", Type),
            ("power", c_uint8),
            ("pp", c_uint8),
            ("accuracy", c_uint8),
            ("priority", c_int8),
            ("target", MoveTarget),
            ("damage_class", DamageClass),
            ("effect", MoveEffect),
            ("effect_chance", c_uint8),
            ("category", MoveCategory),
            ("ailment", Ailment),
            ("ailment_volatile", Boolean),
            ("min_hits", c_uint8),
            ("max_hits", c_uint8),
            ("min_turns", c_uint8),
            ("max_turns", c_uint8),
            ("recoil", c_int8),
            ("healing", c_int8),
            ("critical_rate", c_int8),
            ("ailment_chance", c_uint8),
            ("flinch_chance", c_uint8),
            ("stat_chance", c_uint8),
            ("stat_changes", c_int8 * CHANGEABLE_STATS),
            ("flags", MoveFlags),
            ]

_f("move_details", MoveDetails, Move)

# Palace

_c("PALACE_COUNT", c_size_t)
_f("palace_low_attack", P(c_uint8 * PALACE_COUNT))
_f("palace_low_defense", P(c_uint8 * PALACE_COUNT))
_f("palace_high_attack", P(c_uint8 * PALACE_COUNT))
_f("palace_high_defense", P(c_uint8 * PALACE_COUNT))

# Species
