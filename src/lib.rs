use vdex::*;
use std::ffi::CString;
use std::fmt::Debug;
use std::ptr::null_mut;

type Boolean = u8;

// MEMORY MANAGEMENT //////////////////////////////////////////////////////////

fn allocate_name(s: String) -> *mut i8 {
    CString::new(s).unwrap().into_raw()
}

fn allocate_enum_name<E: Enum + Debug>(repr: <E as Enum>::Repr) -> *mut i8 {
    allocate_name(format!("{:?}", <E as Enum>::from_repr(repr).unwrap()))
}

#[no_mangle]
pub unsafe extern "C" fn vdex_free_name(name: *mut i8) {
    CString::from_raw(name);
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

// POKEDEX ////////////////////////////////////////////////////////////////////

#[no_mangle]
#[repr(C)] pub struct VDexPokedex { ptr: *mut VDexOpaque }

impl Opaque for VDexPokedex {
    type Real = Pokedex;

    fn get(&self) -> *mut VDexOpaque {
        self.ptr
    }

    fn get_mut(&mut self) -> &mut *mut VDexOpaque {
        &mut self.ptr
    }
}

#[no_mangle]
pub extern "C" fn vdex_load_dex() -> VDexPokedex {
    let mut dex = VDexPokedex { ptr: null_mut() };
    unsafe {
        dex.init(Pokedex::new());
    }
    dex
}

#[no_mangle]
pub unsafe extern "C" fn vdex_free_dex(dex: *mut VDexPokedex) {
    (*dex).free();
}

// TYPES //////////////////////////////////////////////////////////////////////

type TypeRepr = <Type as Enum>::Repr;
type EfficacyRepr = <Efficacy as Enum>::Repr;

#[no_mangle]
pub static VDEX_TYPE_COUNT: usize = Type::COUNT;

#[no_mangle]
pub extern "C" fn vdex_type_list() -> *const TypeRepr {
    Type::VALUES.as_ptr() as *const TypeRepr
}

#[no_mangle]
pub extern "C" fn vdex_type_name(typ: TypeRepr) -> *mut i8 {
    allocate_enum_name::<Type>(typ)
}

#[no_mangle]
pub unsafe extern "C" fn vdex_efficacy(
    dex: VDexPokedex, damage: TypeRepr, target: TypeRepr
) -> EfficacyRepr {
    let damage_type = Type::from_repr(damage).unwrap();
    let target_type = Type::from_repr(target).unwrap();
    dex.as_ref().efficacy[(damage_type, target_type)].repr()
}

// ITEMS //////////////////////////////////////////////////////////////////////

type ItemId = u16;

#[no_mangle]
#[repr(C)] pub struct VDexItemIter { ptr: *mut VDexOpaque }

impl Opaque for VDexItemIter {
    type Real = std::collections::hash_map::Keys<'static, ItemId, items::Item>;

    fn get(&self) -> *mut VDexOpaque {
        self.ptr
    }

    fn get_mut(&mut self) -> &mut *mut VDexOpaque {
        &mut self.ptr
    }
}

#[no_mangle]
pub unsafe extern "C" fn vdex_item_iter(dex: VDexPokedex) -> VDexItemIter {
    let mut iter = VDexItemIter { ptr: null_mut() };
    iter.init(dex.as_ref().items.0.keys());
    iter
}

#[no_mangle]
pub static VDEX_ITEM_ITER_END: ItemId = std::u16::MAX;

#[no_mangle]
pub unsafe extern "C" fn vdex_item_next(iter: VDexItemIter) -> ItemId {
    iter.as_mut().next().map_or(VDEX_ITEM_ITER_END, |id| *id)
}

#[no_mangle]
pub unsafe extern "C" fn vdex_free_item_iter(iter: *mut VDexItemIter) {
    (*iter).free();
}

#[no_mangle]
pub unsafe extern "C" fn vdex_item_name(dex: VDexPokedex, id: ItemId) -> *mut i8 {
    allocate_name(dex.as_ref().items[id].name.clone())
}

// ITEM DETAILS ///////////////////////////////////////////////////////////////

type CategoryRepr = <items::Category as Enum>::Repr;
type PocketRepr = <items::Pocket as Enum>::Repr;
type FlingEffectRepr = <items::FlingEffect as Enum>::Repr;
type ItemFlags = u8;
type FlavorRepr = <items::Flavor as Enum>::Repr;

#[no_mangle]
pub static VDEX_ITEM_FLAG_COUNTABLE: ItemFlags = 0x01;
#[no_mangle]
pub static VDEX_ITEM_FLAG_CONSUMABLE: ItemFlags = 0x02;
#[no_mangle]
pub static VDEX_ITEM_FLAG_USABLE_OVERWORLD: ItemFlags = 0x04;
#[no_mangle]
pub static VDEX_ITEM_FLAG_USABLE_IN_BATTLE: ItemFlags = 0x08;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE: ItemFlags = 0x10;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE_PASSIVE: ItemFlags = 0x20;
#[no_mangle]
pub static VDEX_ITEM_FLAG_HOLDABLE_ACTIVE: ItemFlags = 0x40;
#[no_mangle]
pub static VDEX_ITEM_FLAG_UNDERGROUND: ItemFlags = 0x80;

#[no_mangle]
pub static VDEX_NO_DOMINANT_FLAVOR: FlavorRepr = std::u8::MAX;

#[no_mangle]
#[repr(C)] pub struct VDexItemDetails {
    pub category: CategoryRepr,
    pub unused: Boolean,
    pub pocket: PocketRepr,
    pub cost: u16,
    pub fling_power: u8,
    pub fling_effect: FlingEffectRepr,
    pub flags: ItemFlags,
    pub natural_gift_power: u8,
    pub natural_gift_type: TypeRepr,
    pub flavor: FlavorRepr
}

#[no_mangle]
pub unsafe extern "C" fn vdex_item_details(dex: VDexPokedex, id: ItemId) -> VDexItemDetails {
    let item = &dex.as_ref().items[id];
    VDexItemDetails {
        category: item.category.repr(),
        unused: item.category.unused() as Boolean,
        pocket: item.category.pocket().repr(),
        cost: item.cost,
        fling_power: item.fling_power.unwrap_or(0),
        fling_effect: item.fling_effect.repr(),
        flags: item.flags.bits(),
        natural_gift_power: item.berry.map_or(0, |b| b.natural_gift_power),
        natural_gift_type: item.berry.map_or(Type::Normal, |b| b.natural_gift_type).repr(),
        flavor: item.berry.map_or(VDEX_NO_DOMINANT_FLAVOR,
                |b| b.flavor.map_or(VDEX_NO_DOMINANT_FLAVOR, |f| f.repr())),
    }
}

#[no_mangle]
pub extern "C" fn vdex_category_name(category: CategoryRepr) -> *mut i8 {
    allocate_enum_name::<items::Category>(category)
}

#[no_mangle]
pub extern "C" fn vdex_pocket_name(pocket: PocketRepr) -> *mut i8 {
    allocate_enum_name::<items::Pocket>(pocket)
}

#[no_mangle]
pub extern "C" fn vdex_fling_effect_name(fling_effect: FlingEffectRepr) -> *mut i8 {
    allocate_enum_name::<items::FlingEffect>(fling_effect)
}

#[no_mangle]
pub extern "C" fn vdex_flavor_name(flavor: FlavorRepr) -> *mut i8 {
    allocate_enum_name::<items::Flavor>(flavor)
}

// MOVES //////////////////////////////////////////////////////////////////////
