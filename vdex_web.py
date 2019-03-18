import _vdex
import sys

GENERATION_IV = 3

all_rated = []

def rate_defense():
    pass

for species in range(_vdex.SPECIES_COUNT):
    species_details = _vdex.species_details(species)
    if species_details.generation > GENERATION_IV:
        continue
    name = _vdex.species_name(species)
    pokemon = _vdex.pokemon(species, 0)
    details = _vdex.pokemon_details(pokemon)
    total_stats = sum(details.stats)
    if details.has_type2:
        types = (details.type1, details.type2)
    else:
        types = (details.type1,)
    rating = (total_stats - 400)
    all_rated.append((rating, name))

all_rated.sort(reverse=True)

for x in range(100):
    rating, name = all_rated[x]
    print("{: 4d} {}".format(rating, name))
