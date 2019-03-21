import _vdex
import sys

def get_types(details):
    if details.has_type2:
        return (details.type1, details.type2)
    else:
        return (details.type1,)

LEVITATE = 26
GROUND_TYPE = 4
FLASH_FIRE = 18
FIRE_TYPE = 9

def get_immunity(details):
    if details.ability1 == LEVITATE or details.ability2 == LEVITATE:
        return GROUND_TYPE
    elif details.ability1 == FLASH_FIRE or details.ability2 == FLASH_FIRE:
        return FIRE_TYPE
    else:
        return None

EFFICACY = { -2: 0, -1: 2, 0: 4, 1: 8}
EFFICACY_RATING = { 0: 4, 1: 3, 2: 2, 4: 0, 8: -4, 16: -8 }

def rate_resistance(types, immunity=None):
    count = _vdex.TYPE_COUNT
    efficacies = [4] * count
    if immunity is not None:
        efficacies[immunity] = 0
    for typ in types:
        for damage in range(count):
            efficacies[damage] *= EFFICACY[_vdex.efficacy(damage, typ)]
            efficacies[damage] //= 4
    return [EFFICACY_RATING[efficacies[damage]] for damage in range(count)]

def rate_offense(types):
    count = _vdex.TYPE_COUNT
    have_super = [0] * count
    for typ in types:
        for target in range(count):
            if have_super[target] == 0:
                have_super[target] = int(_vdex.efficacy(typ, target) > 0)
    return have_super

GENERATION_IV = 3

def rank_all():
    all_rated = []
    for species in range(_vdex.SPECIES_COUNT):
        species_details = _vdex.species_details(species)
        if species_details.generation > GENERATION_IV:
            continue
        name = _vdex.species_name(species)
        pokemon = _vdex.pokemon(species, 0)
        details = _vdex.pokemon_details(pokemon)
        rating = sum(details.stats) - 400
        types = get_types(details)
        rating += 6 * sum(rate_resistance(types, get_immunity(details)))
        # TODO: Make offense less simplistic
        rating += 30 * sum(rate_offense(types))
        all_rated.append((rating, name))
    all_rated.sort(reverse=True)
    return all_rated

def print_team(*team):
    print("Nrm Fit Fly Psn Gnd Rck Bug Gst Stl Fir Wtr Grs Elc Psy Ice Dgn Drk Pokemon")
    ratings = []
    for species in team:
        name = _vdex.species_name(species)
        pokemon = _vdex.pokemon(species, 0)
        details = _vdex.pokemon_details(pokemon)
        types = get_types(details)
        resistance = rate_resistance(types, get_immunity(details))
        print(" ".join([("({})" if r < 0 else " {} ").format(abs(r)) for r in resistance] + [name]))
        offense = rate_offense(types)
        print("  ".join([(" +" if h else "  ") for h in offense]))
        ratings.append([resistance[typ] + (5 * offense[typ])
            for typ in range(_vdex.TYPE_COUNT)])
    print(" ".join(["{:3d}".format(sum(a)) for a in zip(*ratings)] + ["TOTAL"]))

SPECIES = dict([(_vdex.species_name(i), i) for i in range(_vdex.SPECIES_COUNT)])

def main():
    #all_rated = rank_all()
    #if len(sys.argv) > 1:
    #    with open(sys.argv[1], "w") as f:
    #        for rating, name in all_rated:
    #            print("{: 4d} {}".format(rating, name), file=f)
    #else:
    #    for x in range(50):
    #        rating, name = all_rated[x]
    #        print("{: 4d} {}".format(rating, name))
    print_team(*[SPECIES[name] for name in sys.argv[1:]])

if __name__ == '__main__':
    main()
