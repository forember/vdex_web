from ctypes import *
from os import path
import re

P = POINTER
vdex = CDLL(path.join(path.dirname(__file__), "target/debug/libvdex_web.so"))

class Opaque (Structure):
    _fields_ = []

def _opaque_pointer_as_address(ptr):
    return addressof(ptr.contents)

def _f(name, restype, *argtypes, errcheck=None):
    f = getattr(vdex, "vdex_" + name.lstrip("_"))
    f.restype = restype
    f.argtypes = argtypes
    if errcheck is not None:
        f.errcheck = errcheck
    globals()[name] = f
    return f

def _c(name, typ):
    c = typ.in_dll(vdex, "VDEX_" + name.lstrip("_")).value
    globals()[name] = c
    return c

_f("_free_name", None, P(P(c_char)))

def to_snake_case(name):
    return re.sub(r"(?!^)([A-Z0-9])", r"_\1", name).lower()

def _const_array_errcheck(result, func, arguments):
    if not result:
        return None
    return result.contents

def _cstr_errcheck(result, func, arguments):
    if not result:
        return None
    buf = str(string_at(addressof(result.contents)), 'utf-8')
    _free_name(result)
    return buf

def _e(name, typ=c_uint8):
    globals()[name] = typ
    sname = to_snake_case(name)
    count = _c(sname.upper() + "_COUNT", c_size_t)
    _f(sname + "_list", P(typ * count), errcheck=_const_array_errcheck)
    _f(sname + "_name", P(c_char), typ, errcheck=_cstr_errcheck)

def _cg(base, typ, names):
    s = [name.strip() for name in names.strip().split(" ")]
    globals()[base] = s
    for name in s:
        _c(base + "_" + name, typ)

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
    _fields_ = [("ptr", P(Opaque))]

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
_f("palace_low_attack", P(c_uint8 * PALACE_COUNT), errcheck=_const_array_errcheck)
_f("palace_low_defense", P(c_uint8 * PALACE_COUNT), errcheck=_const_array_errcheck)
_f("palace_high_attack", P(c_uint8 * PALACE_COUNT), errcheck=_const_array_errcheck)
_f("palace_high_defense", P(c_uint8 * PALACE_COUNT), errcheck=_const_array_errcheck)

# Species

Species = c_uint16
Pokemon = c_uint16
_c("SPECIES_COUNT", c_size_t)
_c("POKEMON_COUNT", c_size_t)

_f("species_name", P(c_char), Species, errcheck=_cstr_errcheck)

# Species Details

_c("NO_STAT_DEPENDENCE", c_int8)

class EvolvesFrom (Structure):
    _fields_ = [
            ("from", Pokemon),
            ("trigger", EvolutionTrigger),
            ("level", c_uint8),
            ("gender", Gender),
            ("mov", Move),
            ("relative_physical_stats", c_int8),
            ]

class SpeciesDetails (Structure):
    _fields_ = [
            ("generation", Generation),
            ("egg_group1", EggGroup),
            ("has_egg_group2", Boolean),
            ("egg_group2", EggGroup),
            ("evolved", Boolean),
            ("evolves_from", EvolvesFrom),
            ]

_f("species_details", SpeciesDetails, Species)

# Pokemon

_f("pokemon_count", c_size_t, Species)

class PokemonHandle (Structure):
    _fields_ = [("ptr", P(Opaque))]

_f("pokemon", PokemonHandle, Species, c_size_t)

# Pokemon Details

_c("PERMANENT_STATS", c_size_t)
_cg("STAT_PERMANENT", c_size_t, """
 HP ATTACK DEFENSE SPEED SPECIAL_ATTACK SPECIAL_DEFENSE 
""")

class PokemonDetails (Structure):
    _fields_ = [
            ("id", Pokemon),
            ("ability1", Ability),
            ("has_ability2", Boolean),
            ("ability2", Ability),
            ("has_hidden_ability", Boolean),
            ("hidden_ability", Ability),
            ("stats", c_uint8 * PERMANENT_STATS),
            ("type1", Type),
            ("has_type2", Boolean),
            ("type2", Type),
            ]

_f("pokemon_details", PokemonDetails, PokemonHandle)

# Forms

_f("form_count", c_size_t, PokemonHandle)
_f("form_veekun_id", c_uint16, PokemonHandle, c_size_t)
_f("form_battle_only", Boolean, PokemonHandle, c_size_t)
_f("form_name", P(c_char), PokemonHandle, c_size_t, errcheck=_cstr_errcheck)

# Movesets

_f("moveset_entry_count", c_size_t, PokemonHandle, VersionGroup)

class MovesetEntry (Structure):
    _fields_ = [
            ("mov", Move),
            ("learn_method", LearnMethod),
            ("level", c_uint8),
            ]

_f("moveset_entry", MovesetEntry, PokemonHandle, VersionGroup, c_size_t)
