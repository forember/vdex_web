use vdex::Enum;
use vdex::pokedex;
use vdex::items::ItemId;
use vdex::moves::MoveId;
use vdex::pokemon::SpeciesId;
use vdex::versions::VersionGroup;
use std::ffi::CString;
use std::fmt::Debug;
use std::ptr::{null, null_mut};

// MEMORY MANAGEMENT //////////////////////////////////////////////////////////

fn allocate_name(s: String) -> *mut i8 {
    CString::new(s).unwrap().into_raw()
}

fn allocate_enum_name<E: Enum + Debug>(repr: <E as Enum>::Repr) -> *mut i8 {
    allocate_name(format!("{:?}", <E as Enum>::from_repr(repr).unwrap()))
}

#[no_mangle]
pub unsafe extern "C" fn vdex_free_name(name: *mut *mut i8) {
    if !(*name).is_null() {
        CString::from_raw(*name);
        *name = null_mut();
    }
}

#[no_mangle]
#[repr(C)] pub struct VDexOpaque { _opaque: [u8; 0] }

trait Opaque {
    type Real;

    fn get(&self) -> *mut VDexOpaque;

    fn get_mut(&mut self) -> &mut *mut VDexOpaque;

    fn real(&self) -> *mut Self::Real {
        self.get() as *mut Self::Real
    }

    unsafe fn init(&mut self, value: Self::Real) {
        self.free();
        *self.get_mut() = Box::into_raw(Box::new(value)) as *mut VDexOpaque;
    }

    unsafe fn free(&mut self) {
        if !self.get().is_null() {
            Box::from_raw(self.get());
            *self.get_mut() = null_mut();
        }
    }

    unsafe fn as_ref(&self) -> &'static Self::Real {
        self.real().as_ref().unwrap()
    }

    unsafe fn as_mut(&self) -> &'static mut Self::Real {
        self.real().as_mut().unwrap()
    }
}

trait OpaqueConst {
    type Real;

    fn get(&self) -> *const VDexOpaque;

    fn get_mut(&mut self) -> &mut *const VDexOpaque;

    fn real(&self) -> *const Self::Real {
        self.get() as *const Self::Real
    }

    unsafe fn init(&mut self, reference: &'static Self::Real) {
        *self.get_mut() = (reference as *const Self::Real) as *const VDexOpaque;
    }

    unsafe fn as_ref(&self) -> &'static Self::Real {
        self.real().as_ref().unwrap()
    }
}

// ENUMS //////////////////////////////////////////////////////////////////////

macro_rules! vdex_enum {
    ($e:ty, $r:ident, $c:ident, $l:ident, $n:ident) => {
        type $r = <$e as Enum>::Repr;

        #[no_mangle]
        pub static $c: usize = <$e as Enum>::COUNT;

        #[no_mangle]
        pub extern "C" fn $l() -> *const $r {
            <$e as Enum>::VALUES.as_ptr() as *const $r
        }

        #[no_mangle]
        pub extern "C" fn $n(repr: $r) -> *mut i8 {
            allocate_enum_name::<$e>(repr)
        }
    };
}

vdex_enum!(vdex::Ability, AbilityRepr, VDEX_ABILITY_COUNT,
        vdex_ability_list, vdex_ability_name);
vdex_enum!(vdex::Efficacy, EfficacyRepr, VDEX_EFFICACY_COUNT,
        vdex_efficacy_list, vdex_efficacy_name);
vdex_enum!(vdex::Nature, NatureRepr, VDEX_NATURE_COUNT,
        vdex_nature_list, vdex_nature_name);
vdex_enum!(vdex::Type, TypeRepr, VDEX_TYPE_COUNT,
        vdex_type_list, vdex_type_name);

vdex_enum!(vdex::items::Category, ItemCategoryRepr, VDEX_ITEM_CATEGORY_COUNT,
        vdex_item_category_list, vdex_item_category_name);
vdex_enum!(vdex::items::Flavor, FlavorRepr, VDEX_FLAVOR_COUNT,
        vdex_flavor_list, vdex_flavor_name);
vdex_enum!(vdex::items::FlingEffect, FlingEffectRepr, VDEX_FLING_EFFECT_COUNT,
        vdex_fling_effect_list, vdex_fling_effect_name);
vdex_enum!(vdex::items::Pocket, PocketRepr, VDEX_POCKET_COUNT,
        vdex_pocket_list, vdex_pocket_name);

vdex_enum!(vdex::moves::Ailment, AilmentRepr, VDEX_AILMENT_COUNT,
        vdex_ailment_list, vdex_ailment_name);
vdex_enum!(vdex::moves::BattleStyle, BattleStyleRepr, VDEX_BATTLE_STYLE_COUNT,
        vdex_battle_style_list, vdex_battle_style_name);
vdex_enum!(vdex::moves::Category, MoveCategoryRepr, VDEX_MOVE_CATEGORY_COUNT,
        vdex_move_category_list, vdex_move_category_name);
vdex_enum!(vdex::moves::DamageClass, DamageClassRepr, VDEX_DAMAGE_CLASS_COUNT,
        vdex_damage_class_list, vdex_damage_class_name);
vdex_enum!(vdex::moves::Effect, MoveEffectRepr, VDEX_MOVE_EFFECT_COUNT,
        vdex_move_effect_list, vdex_move_effect_name);
vdex_enum!(vdex::moves::LearnMethod, LearnMethodRepr, VDEX_LEARN_METHOD_COUNT,
        vdex_learn_method_list, vdex_learn_method_name);
vdex_enum!(vdex::moves::Target, MoveTargetRepr, VDEX_MOVE_TARGET_COUNT,
        vdex_move_target_list, vdex_move_target_name);

vdex_enum!(vdex::pokemon::EggGroup, EggGroupRepr, VDEX_EGG_GROUP_COUNT,
        vdex_egg_group_list, vdex_egg_group_name);
vdex_enum!(vdex::pokemon::EvolutionTrigger, EvolutionTriggerRepr,
        VDEX_EVOLUTION_TRIGGER_COUNT,
        vdex_evolution_trigger_list, vdex_evolution_trigger_name);
vdex_enum!(vdex::pokemon::Gender, GenderRepr, VDEX_GENDER_COUNT,
        vdex_gender_list, vdex_gender_name);

vdex_enum!(vdex::versions::Generation, GenerationRepr, VDEX_GENERATION_COUNT,
        vdex_generation_list, vdex_generation_name);
vdex_enum!(vdex::versions::Version, VersionRepr, VDEX_VERSION_COUNT,
        vdex_version_list, vdex_version_name);
vdex_enum!(vdex::versions::VersionGroup, VersionGroupRepr,
        VDEX_VERSION_GROUP_COUNT,
        vdex_version_group_list, vdex_version_group_name);

// EFFICACY ///////////////////////////////////////////////////////////////////

#[no_mangle]
pub static VDEX_INVALID_DAMAGE_TYPE: EfficacyRepr = std::i8::MAX;
#[no_mangle]
pub static VDEX_INVALID_TARGET_TYPE: EfficacyRepr = std::i8::MAX - 1;

fn efficacy(damage: TypeRepr, target: TypeRepr) -> Result<EfficacyRepr, EfficacyRepr> {
    let damage_type = vdex::Type::from_repr(damage).ok_or(VDEX_INVALID_DAMAGE_TYPE)?;
    let target_type = vdex::Type::from_repr(target).ok_or(VDEX_INVALID_TARGET_TYPE)?;
    Ok(pokedex().efficacy[(damage_type, target_type)].repr())
}

#[no_mangle]
pub extern "C" fn vdex_efficacy(damage: TypeRepr, target: TypeRepr) -> EfficacyRepr {
    efficacy(damage, target).unwrap_or_else(|e| e)
}

// ITEMS //////////////////////////////////////////////////////////////////////

type ItemIdRepr = u16;

#[no_mangle]
#[repr(C)] pub struct VDexItemIter { ptr: *mut VDexOpaque }

impl Opaque for VDexItemIter {
    type Real = std::collections::hash_map::Keys<'static, ItemId, vdex::items::Item>;

    fn get(&self) -> *mut VDexOpaque {
        self.ptr
    }

    fn get_mut(&mut self) -> &mut *mut VDexOpaque {
        &mut self.ptr
    }
}

#[no_mangle]
pub unsafe extern "C" fn vdex_item_iter() -> VDexItemIter {
    let mut iter = VDexItemIter { ptr: null_mut() };
    iter.init(pokedex().items.0.keys());
    iter
}

#[no_mangle]
pub static VDEX_ITEM_ITER_END: ItemIdRepr = std::u16::MAX;

#[no_mangle]
pub unsafe extern "C" fn vdex_item_next(iter: VDexItemIter) -> ItemIdRepr {
    iter.as_mut().next().map_or(VDEX_ITEM_ITER_END, |id| id.0)
}

#[no_mangle]
pub unsafe extern "C" fn vdex_free_item_iter(iter: *mut VDexItemIter) {
    (*iter).free();
}

#[no_mangle]
pub extern "C" fn vdex_item_name(id: ItemIdRepr) -> *mut i8 {
    allocate_name(pokedex().items[ItemId(id)].name.clone())
}

// ITEM DETAILS ///////////////////////////////////////////////////////////////

type BooleanRepr = u8;

type ItemFlagsRepr = u8;
#[no_mangle]
pub static VDEX_ITEM_FLAG_COUNTABLE: ItemFlagsRepr = 0x01;
#[no_mangle]
pub static VDEX_ITEM_FLAG_CONSUMABLE: ItemFlagsRepr = 0x02;
#[no_mangle]
pub static VDEX_ITEM_FLAG_USABLE_OVERWORLD: ItemFlagsRepr = 0x04;
#[no_mangle]
pub static VDEX_ITEM_FLAG_USABLE_IN_BATTLE: ItemFlagsRepr = 0x08;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE: ItemFlagsRepr = 0x10;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE_PASSIVE: ItemFlagsRepr = 0x20;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE_ACTIVE: ItemFlagsRepr = 0x40;
#[no_mangle]
pub static VDEX_ITEM_FLAG_UNDERGROUND: ItemFlagsRepr = 0x80;

#[no_mangle]
pub static VDEX_NO_DOMINANT_FLAVOR: FlavorRepr = std::u8::MAX;

#[no_mangle]
#[repr(C)] pub struct VDexItemDetails {
    pub category: ItemCategoryRepr,
    pub unused: BooleanRepr,
    pub pocket: PocketRepr,
    pub cost: u16,
    pub fling_power: u8,
    pub fling_effect: FlingEffectRepr,
    pub flags: ItemFlagsRepr,
    pub natural_gift_power: u8,
    pub natural_gift_type: TypeRepr,
    pub flavor: FlavorRepr
}

#[no_mangle]
pub extern "C" fn vdex_item_details(id: ItemIdRepr) -> VDexItemDetails {
    let item = &pokedex().items[ItemId(id)];
    VDexItemDetails {
        category: item.category.repr(),
        unused: item.category.unused() as BooleanRepr,
        pocket: item.category.pocket().repr(),
        cost: item.cost,
        fling_power: item.fling_power.unwrap_or(0),
        fling_effect: item.fling_effect.repr(),
        flags: item.flags.bits(),
        natural_gift_power: item.berry.map_or(0, |b| b.natural_gift_power),
        natural_gift_type: item.berry.map_or(vdex::Type::Normal,
                |b| b.natural_gift_type).repr(),
        flavor: item.berry.map_or(VDEX_NO_DOMINANT_FLAVOR,
                |b| b.flavor.map_or(VDEX_NO_DOMINANT_FLAVOR, |f| f.repr())),
    }
}

// MOVES //////////////////////////////////////////////////////////////////////

type MoveIdRepr = u16;

#[no_mangle]
pub static VDEX_MOVE_COUNT: usize = vdex::moves::MOVE_COUNT;

#[no_mangle]
pub extern "C" fn vdex_move_name(id: MoveIdRepr) -> *mut i8 {
    allocate_name(pokedex().moves[MoveId(id)].name.clone())
}

// MOVE DETAILS ///////////////////////////////////////////////////////////////

#[no_mangle]
pub static VDEX_NEVER_MISSES: u8 = 0;

#[no_mangle]
pub static VDEX_CHANGEABLE_STATS: usize = vdex::moves::CHANGEABLE_STATS;
#[no_mangle]
pub static VDEX_STAT_CHANGE_ATTACK: usize = 0;
#[no_mangle]
pub static VDEX_STAT_CHANGE_DEFENSE: usize = 1;
#[no_mangle]
pub static VDEX_STAT_CHANGE_SPEED: usize = 2;
#[no_mangle]
pub static VDEX_STAT_CHANGE_SPECIAL_ATTACK: usize = 3;
#[no_mangle]
pub static VDEX_STAT_CHANGE_SPECIAL_DEFENSE: usize = 4;
#[no_mangle]
pub static VDEX_STAT_CHANGE_ACCURACY: usize = 5;
#[no_mangle]
pub static VDEX_STAT_CHANGE_EVASION: usize = 6;

type MoveFlagsRepr = u16;
#[no_mangle]
pub static VDEX_MOVE_FLAG_CONTACT: MoveFlagsRepr = 0x0001;
#[no_mangle]
pub static VDEX_MOVE_FLAG_CHARGE: MoveFlagsRepr = 0x0002;
#[no_mangle]
pub static VDEX_MOVE_FLAG_RECHARGE: MoveFlagsRepr = 0x0004;
#[no_mangle]
pub static VDEX_MOVE_FLAG_PROTECT: MoveFlagsRepr = 0x0008;
#[no_mangle]
pub static VDEX_MOVE_FLAG_REFLECTABLE: MoveFlagsRepr = 0x0010;
#[no_mangle]
pub static VDEX_MOVE_FLAG_SNATCH: MoveFlagsRepr = 0x0020;
#[no_mangle]
pub static VDEX_MOVE_FLAG_MIRROR: MoveFlagsRepr = 0x0040;
#[no_mangle]
pub static VDEX_MOVE_FLAG_PUNCH: MoveFlagsRepr = 0x0080;
#[no_mangle]
pub static VDEX_MOVE_FLAG_SOUND: MoveFlagsRepr = 0x0100;
#[no_mangle]
pub static VDEX_MOVE_FLAG_GRAVITY: MoveFlagsRepr = 0x0200;
#[no_mangle]
pub static VDEX_MOVE_FLAG_DEFROST: MoveFlagsRepr = 0x0400;
#[no_mangle]
pub static VDEX_MOVE_FLAG_DISTANCE: MoveFlagsRepr = 0x0800;
#[no_mangle]
pub static VDEX_MOVE_FLAG_HEAL: MoveFlagsRepr = 0x1000;
#[no_mangle]
pub static VDEX_MOVE_FLAG_AUTHENTIC: MoveFlagsRepr = 0x2000;

#[no_mangle]
#[repr(C)] pub struct VDexMoveDetails {
    pub generation: GenerationRepr,
    pub typ: TypeRepr,
    pub power: u8,
    pub pp: u8,
    pub accuracy: u8,
    pub priority: i8,
    pub target: MoveTargetRepr,
    pub damage_class: DamageClassRepr,
    pub effect: MoveEffectRepr,
    pub effect_chance: u8,
    pub category: MoveCategoryRepr,
    pub ailment: AilmentRepr,
    pub ailment_volatile: BooleanRepr,
    pub min_hits: u8,
    pub max_hits: u8,
    pub min_turns: u8,
    pub max_turns: u8,
    pub recoil: i8,
    pub healing: i8,
    pub critical_rate: i8,
    pub ailment_chance: u8,
    pub flinch_chance: u8,
    pub stat_chance: u8,
    pub stat_changes: [i8; vdex::moves::CHANGEABLE_STATS],
    pub flags: MoveFlagsRepr,
}

#[no_mangle]
pub extern "C" fn vdex_move_details(id: MoveIdRepr) -> VDexMoveDetails {
    let mov = &pokedex().moves[MoveId(id)];
    VDexMoveDetails {
        generation: mov.generation.repr(),
        typ: mov.typ.repr(),
        power: mov.power,
        pp: mov.pp,
        accuracy: mov.accuracy.unwrap_or(VDEX_NEVER_MISSES),
        priority: mov.priority,
        target: mov.target.repr(),
        damage_class: mov.damage_class.repr(),
        effect: mov.effect.repr(),
        effect_chance: mov.effect_chance.unwrap_or(0),
        category: mov.meta.category.repr(),
        ailment: mov.meta.ailment.repr(),
        ailment_volatile: mov.meta.ailment.volatile() as BooleanRepr,
        min_hits: mov.meta.hits.map_or(1, |p| p.0),
        max_hits: mov.meta.hits.map_or(1, |p| p.1),
        min_turns: mov.meta.turns.map_or(1, |p| p.0),
        max_turns: mov.meta.turns.map_or(1, |p| p.1),
        recoil: mov.meta.recoil,
        healing: mov.meta.healing,
        critical_rate: mov.meta.critical_rate,
        ailment_chance: mov.meta.ailment_chance,
        flinch_chance: mov.meta.flinch_chance,
        stat_chance: mov.meta.stat_chance,
        stat_changes: mov.meta.stat_changes,
        flags: mov.meta.flags.bits(),
    }
}

// PALACE /////////////////////////////////////////////////////////////////////

#[no_mangle]
pub static VDEX_PALACE_COUNT: usize = VDEX_NATURE_COUNT;

#[no_mangle]
pub extern "C" fn vdex_palace_low_attack() -> *const u8 {
    pokedex().palace.low.attack.as_ptr() as *const u8
}

#[no_mangle]
pub extern "C" fn vdex_palace_low_defense() -> *const u8 {
    pokedex().palace.low.defense.as_ptr() as *const u8
}

#[no_mangle]
pub extern "C" fn vdex_palace_high_attack() -> *const u8 {
    pokedex().palace.high.attack.as_ptr() as *const u8
}

#[no_mangle]
pub extern "C" fn vdex_palace_high_defense() -> *const u8 {
    pokedex().palace.high.defense.as_ptr() as *const u8
}

// SPECIES ////////////////////////////////////////////////////////////////////

type SpeciesIdRepr = u16;
type PokemonIdRepr = u16;

#[no_mangle]
pub static VDEX_SPECIES_COUNT: usize = vdex::pokemon::SPECIES_COUNT;
#[no_mangle]
pub static VDEX_POKEMON_COUNT: usize = vdex::pokemon::POKEMON_COUNT;

#[no_mangle]
pub extern "C" fn vdex_species_name(id: SpeciesIdRepr) -> *mut i8 {
    allocate_name(pokedex().species[SpeciesId(id)].name.clone())
}

// SPECIES DETAILS ////////////////////////////////////////////////////////////

#[no_mangle]
pub static VDEX_NO_STAT_DEPENDENCE: i8 = std::i8::MAX;

#[derive(Default)]
#[no_mangle]
#[repr(C)] pub struct VDexEvolvesFrom {
    pub from: PokemonIdRepr,
    pub trigger: EvolutionTriggerRepr,
    pub level: u8,
    pub gender: GenderRepr,
    pub mov: MoveIdRepr,
    pub relative_physical_stats: i8,
}

#[no_mangle]
#[repr(C)] pub struct VDexSpeciesDetails {
    pub generation: GenerationRepr,
    pub egg_group1: EggGroupRepr,
    pub has_egg_group2: BooleanRepr,
    pub egg_group2: EggGroupRepr,
    pub evolved: BooleanRepr,
    pub evolves_from: VDexEvolvesFrom,
}

#[no_mangle]
pub extern "C" fn vdex_species_details(id: SpeciesIdRepr) -> VDexSpeciesDetails {
    let species = &pokedex().species[SpeciesId(id)];
    VDexSpeciesDetails {
        generation: species.generation.repr(),
        egg_group1: species.egg_groups.first().repr(),
        has_egg_group2: species.egg_groups.second().is_some() as BooleanRepr,
        egg_group2: species.egg_groups.second().unwrap_or_default().repr(),
        evolved: species.evolves_from.is_some() as BooleanRepr,
        evolves_from: match species.evolves_from {
            None => Default::default(),
            Some(e) => VDexEvolvesFrom {
                from: e.from_id.0,
                trigger: e.trigger.repr(),
                level: e.level,
                gender: e.gender.repr(),
                mov: e.move_id.0,
                relative_physical_stats:
                    e.relative_physical_stats.unwrap_or(VDEX_NO_STAT_DEPENDENCE),
            },
        },
    }
}

// POKEMON ////////////////////////////////////////////////////////////////////

#[no_mangle]
pub extern "C" fn vdex_pokemon_count(species: SpeciesIdRepr) -> usize {
    pokedex().species[SpeciesId(species)].pokemon.len()
}

#[no_mangle]
#[repr(C)] pub struct VDexPokemon { ptr: *const VDexOpaque }

impl OpaqueConst for VDexPokemon {
    type Real = vdex::pokemon::Pokemon;

    fn get(&self) -> *const VDexOpaque {
        self.ptr
    }

    fn get_mut(&mut self) -> &mut *const VDexOpaque {
        &mut self.ptr
    }
}

#[no_mangle]
pub unsafe extern "C" fn vdex_pokemon(
    species: SpeciesIdRepr, pokemon_index: usize
) -> VDexPokemon {
    let mut pokemon: VDexPokemon = VDexPokemon { ptr: null() };
    pokemon.init(&pokedex().species[SpeciesId(species)].pokemon[pokemon_index]);
    pokemon
}

// POKEMON DETAILS ////////////////////////////////////////////////////////////

#[no_mangle]
pub static VDEX_PERMANENT_STATS: usize = vdex::pokemon::PERMANENT_STATS;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_HP: usize = 0;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_ATTACK: usize = 1;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_DEFENSE: usize = 2;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_SPECIAL_ATTACK: usize = 3;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_SPECIAL_DEFENSE: usize = 4;
#[no_mangle]
pub static VDEX_STAT_PERMANENT_SPEED: usize = 5;

#[no_mangle]
#[repr(C)] pub struct VDexPokemonDetails {
    ability1: AbilityRepr,
    has_ability2: BooleanRepr,
    ability2: AbilityRepr,
    has_hidden_ability: BooleanRepr,
    hidden_ability: AbilityRepr,
    stats: [u8; vdex::pokemon::PERMANENT_STATS],
    type1: TypeRepr,
    has_type2: BooleanRepr,
    type2: TypeRepr,
}

#[no_mangle]
pub unsafe extern "C" fn vdex_pokemon_details(
    pokemon: VDexPokemon
) -> VDexPokemonDetails {
    let pokemon_ref = pokemon.as_ref();
    VDexPokemonDetails {
        ability1: pokemon_ref.abilities.first().repr(),
        has_ability2: pokemon_ref.abilities.second().is_some() as BooleanRepr,
        ability2: pokemon_ref.abilities.second().unwrap_or_default().repr(),
        has_hidden_ability: pokemon_ref.hidden_ability.is_some() as BooleanRepr,
        hidden_ability: pokemon_ref.hidden_ability.unwrap_or_default().repr(),
        stats: pokemon_ref.stats.0,
        type1: pokemon_ref.types.first().repr(),
        has_type2: pokemon_ref.types.second().is_some() as BooleanRepr,
        type2: pokemon_ref.types.second().unwrap_or_default().repr(),
    }
}

// FORMS /////////////////////////////////////////////////////////////////////

#[no_mangle]
pub unsafe extern "C" fn vdex_form_count(pokemon: VDexPokemon) -> usize {
    pokemon.as_ref().forms.len()
}

#[no_mangle]
pub unsafe extern "C" fn vdex_form_veekun_id(
    pokemon: VDexPokemon, index: usize
) -> u16 {
    pokemon.as_ref().forms[index].id
}

#[no_mangle]
pub unsafe extern "C" fn vdex_form_battle_only(
    pokemon: VDexPokemon, index: usize
) -> BooleanRepr {
    pokemon.as_ref().forms[index].battle_only as BooleanRepr
}

#[no_mangle]
pub unsafe extern "C" fn vdex_form_name(
    pokemon: VDexPokemon, index: usize
) -> *mut i8 {
    match pokemon.as_ref().forms[index].name.clone() {
        Some(n) => allocate_name(n),
        None => null_mut(),
    }
}

// MOVESETS ///////////////////////////////////////////////////////////////////

#[no_mangle]
pub unsafe extern "C" fn vdex_moveset_entry_count(
    pokemon: VDexPokemon, vg: VersionGroupRepr
) -> usize {
    let e = &VersionGroup::from_repr(vg).unwrap();
    pokemon.as_ref().moves.get(e).map_or(0, |s| s.len())
}

#[no_mangle]
#[repr(C)] pub struct VDexMovesetEntry {
    pub mov: MoveIdRepr,
    pub learn_method: LearnMethodRepr,
    pub level: u8,
}

#[no_mangle]
pub unsafe extern "C" fn vdex_moveset_entry(
    pokemon: VDexPokemon, vg: VersionGroupRepr, index: usize
) -> VDexMovesetEntry {
    let e = &VersionGroup::from_repr(vg).unwrap();
    let entry = &pokemon.as_ref().moves[e][index];
    VDexMovesetEntry {
        mov: entry.move_id.0,
        learn_method: entry.learn_method.repr(),
        level: entry.level,
    }
}
