import flask
import _vdex
import math

app = flask.Flask(__name__)

def get_types(details):
    if details.has_type2:
        return (details.type1, details.type2)
    else:
        return (details.type1,)

def rate_offense(types):
    count = _vdex.TYPE_COUNT
    have_super = [0] * count
    for typ in types:
        for target in range(count):
            if have_super[target] == 0:
                have_super[target] = int(_vdex.efficacy(typ, target) > 0)
    return have_super

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

def gen_evolves(maxgen):
    for species in range(_vdex.SPECIES_COUNT):
        species_details = _vdex.species_details(species)
        if species_details.generation > maxgen:
            continue
        from_id = species_details.evolves_from.from_id
        from_details = _vdex.species_details(from_id)
        if from_details.generation > maxgen:
            continue
        yield from_id

SPECIES = dict([(_vdex.species_name(i), i) for i in range(_vdex.SPECIES_COUNT)])

def rate(name):
    species = SPECIES[name]
    species_details = _vdex.species_details(species)
    pokemon = _vdex.pokemon(species, 0)
    details = _vdex.pokemon_details(pokemon)
    types = get_types(details)
    offense = rate_offense(types)
    resistance = rate_resistance(types, get_immunity(details))
    stats = list(details.stats)
    rating = 30 * sum(offense) + 6 * sum(resistance) + sum(stats) - 400
    r = {   "offense": offense,
            "resistance": resistance,
            "stats": stats,
            "rating": rating}
    #print(r)
    return r

RATINGS = dict([(name, rate(name)) for name in SPECIES])

@app.route("/rate/<name>")
def route_rate(name):
    return flask.jsonify(rate(name))

def team(names):
    return dict([(name, RATINGS[name]) for name in names])

@app.route("/team")
def route_team():
    return flask.jsonify(team(flask.request.args.getlist("poke")))

def modified_rating(team_dict, base_values=None):
    count = _vdex.TYPE_COUNT
    coverage = base_values[0][:] if base_values is not None else [0] * count
    or_totals = base_values[1][:] if base_values is not None else [0] * count
    ratings_total = base_values[2] if base_values is not None else 0
    for poke in team_dict.values():
        for typ in range(count):
            offense = poke["offense"][typ]
            if offense == 1:
                coverage[typ] = 1
            or_totals[typ] += (offense * 5) + poke["resistance"][typ]
        ratings_total += poke["rating"]
    modr = ratings_total
    negatives = 0
    for total in or_totals:
        if total < 0:
            negatives -= total
    if ratings_total > 0:
        modr += (sum(coverage) * ratings_total) // count
        modr //= negatives + 1
    return (modr, (sum(coverage), ratings_total, negatives),
            (coverage, or_totals, ratings_total))

def suggest(names, maxgen):
    team_dict = team(names)
    base_modr, base_extras, base_values = modified_rating(team_dict)
    team_dict["_RATING"] = (base_modr, base_extras)
    evolves = set(gen_evolves(maxgen))
    all_rated = []
    for species in range(_vdex.SPECIES_COUNT):
        species_details = _vdex.species_details(species)
        if species_details.generation > maxgen:
            continue
        if species in evolves:
            continue
        name = _vdex.species_name(species)
        modr, extras, _ = modified_rating({name: RATINGS[name]}, base_values)
        all_rated.append((modr, extras, name))
    all_rated.sort(reverse=True)
    team_dict["_SUGGEST"] = all_rated[:5]
    return team_dict

@app.route("/suggest")
def route_suggest():
    return flask.jsonify(suggest(flask.request.args.getlist("poke"),
        flask.request.args.get("maxgen", default=5, type=int) - 1))
