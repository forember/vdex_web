import flask
import _vdex

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

@app.route("/rate/<name>")
def route_rate(name):
    return flask.jsonify(rate(name))

def team(names):
    return dict([(name, rate(name)) for name in names])

@app.route("/team")
def route_team():
    return flask.jsonify(team(flask.request.args.getlist("poke")))
