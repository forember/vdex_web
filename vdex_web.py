import _vdex
import sys

GENERATION_IV = 3

all_rated = []

for species in range(_vdex.SPECIES_COUNT):
    species_details = _vdex.species_details(species)
    if species_details.generation > GENERATION_IV:
        continue
    name = _vdex.species_name(species)
    print("pokemon: {}".format(name), file=sys.stderr)
    pokemon = _vdex.pokemon(species, 0)
    _address = _vdex._opaque_pointer_as_address(pokemon.ptr)
    print("pointer (Python): 0x{:x}".format(_address), file=sys.stderr)
    details = _vdex.pokemon_details(pokemon)
    print("stats:")
    print(list(details.stats))
    total_stats = sum(details.stats)
    if details.has_type2:
        types = (details.type1, details.type2)
    else:
        types = (details.type1,)
    rating = (total_stats - 400)
    all_rated.append((rating, name))
    print("completed: {}".format(rating), file=sys.stderr)

all_rated.sort()

for x in range(100):
    rating, name = all_rated[x]
    print("{: 4d} {}".format(rating, name))
