#!/usr/bin/env python3
import _vdex
import sys
from collections import OrderedDict
from itertools import combinations

def get_types(details):
    if details.has_type2:
        return (details.type1, details.type2)
    else:
        return (details.type1,)

GROUND_TYPE = 4
LEVITATE = 26

FIRE_TYPE = 9
FLASH_FIRE = 18

WATER_TYPE = 10
WATER_ABSORB = 11

ELECTRIC_TYPE = 12
VOLT_ABSORB = 10

def get_immunity(details):
    if details.ability1 == LEVITATE or details.ability2 == LEVITATE:
        return GROUND_TYPE
    elif details.ability1 == FLASH_FIRE or details.ability2 == FLASH_FIRE:
        return FIRE_TYPE
    elif details.ability1 == WATER_ABSORB or details.ability2 == WATER_ABSORB:
        return WATER_TYPE
    elif details.ability1 == VOLT_ABSORB or details.ability2 == VOLT_ABSORB:
        return ELECTRIC_TYPE
    else:
        return None

EFFICACY = { -2: 0, -1: 2, 0: 4, 1: 8}
EFFICACY_RATING = { 0: 4, 1: 3, 2: 2, 4: 0, 8: -4, 16: -6 }

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

def gen_evolves(generations):
    for species in range(_vdex.SPECIES_COUNT):
        species_details = _vdex.species_details(species)
        if species_details.generation not in generations:
            continue
        from_id = species_details.evolves_from.from_id
        from_details = _vdex.species_details(from_id)
        if from_details.generation not in generations:
            continue
        yield from_id

def rank_all(generations=None, final=False):
    if not generations:
        generations = list(range(5))
    evolves = set(gen_evolves(generations))
    all_rated = []
    for species in range(_vdex.SPECIES_COUNT):
        species_details = _vdex.species_details(species)
        if species_details.generation not in generations:
            continue
        if final and species in evolves:
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

def print_ranked(generations=None, final=False):
    all_rated = rank_all(generations, final)
    for rating, name in all_rated:
        print("{: 4d} {}".format(rating, name))

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
    totals = [sum(a) for a in zip(*ratings)]
    print(" ".join(["{:3d}".format(t) for t in totals] + ["TOTAL", str(sum(totals))]))

def score_team(*team):
    ratings = []
    for species in team:
        name = _vdex.species_name(species)
        pokemon = _vdex.pokemon(species, 0)
        details = _vdex.pokemon_details(pokemon)
        types = get_types(details)
        resistance = rate_resistance(types, get_immunity(details))
        offense = rate_offense(types)
        ratings.append([resistance[typ] + (5 * offense[typ])
            for typ in range(_vdex.TYPE_COUNT)])
    totals = [sum(a) for a in zip(*ratings)]
    mintotal = min(totals)
    mincount = totals.count(mintotal)
    fulltotal = sum(totals)
    return (mintotal, -mincount, fulltotal, team)

def score_combinations(pokemon, size, cutoff):
    combs = list(combinations(pokemon, size))
    scores = []
    for i, team in enumerate(combs):
        if i % 1000 == 0:
            print("{}/{}".format(i, len(combs)), file=sys.stderr)
        score = score_team(*team)
        if score[0] >= cutoff:
          scores.append(score)
    print("Sorting...", file=sys.stderr)
    scores.sort()
    for mt, mc, ft, team in scores:
        print("TEAM: {}".format(" ".join(_vdex.species_name(species) for species in team)))
        print_team(*team)
        print("MINIMUM: {} {}s; FULL TOTAL: {}".format(-mc, mt, ft))
        print()

def load_effects():
    effects = OrderedDict([(_vdex.move_effect_name(e), []) for e in _vdex.move_effect_list()])
    for i in range(_vdex.MOVE_COUNT):
        move = _vdex.move_name(i)
        effect = _vdex.move_effect_name(_vdex.move_details(i).effect)
        effects[effect].append(move)
    return effects

EFFECTS = load_effects()

def print_effects():
    for effect, moves in EFFECTS.items():
        print(effect)
        for move in moves:
            print("  " + move)

SPECIES = dict([(_vdex.species_name(i), i) for i in range(_vdex.SPECIES_COUNT)])

def usage():
    print("""Usage: {0} <command> [arguments...]
team [Pokemon...]
    Print a type analysis table for a team.
coverage <team size> <cutoff> [Pokemon...]
    Determine coverage teams of a given size and cutoff.
rank all [Generations...]
    Rank Pokémon based on stats and type from the given generations.
rank final [Generations...]
    Rank final evolutions  from the given generations.
effects
    List pbirch move effects and their associated move lists.
""".format(sys.argv[0]))

def main():
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == 'team':
        print_team(*[SPECIES[name] for name in sys.argv[2:]])
    elif sys.argv[1] == 'coverage' and len(sys.argv) > 4:
        score_combinations([SPECIES[name] for name in sys.argv[4:]],
                int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == 'rank':
        generations = set([int(num) - 1 for num in sys.argv[3:]])
        if len(sys.argv) < 3:
            usage()
        elif sys.argv[2] == 'all':
            print_ranked(generations, final=False)
        elif sys.argv[2] == 'final':
            print_ranked(generations, final=True)
    elif sys.argv[1] == 'effects':
        print_effects()
    else:
        usage()

if __name__ == '__main__':
    main()
