import flask
import _vdex

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/enums/")
def enums():
    return flask.render_template("enums.html")

@app.route("/enums/<name>")
def enum(name):
    sname = _vdex.to_snake_case(name)
    if not hasattr(_vdex, sname + "_list"):
        flask.abort(404)
    _list = getattr(_vdex, sname + "_list")
    _name = getattr(_vdex, sname + "_name")
    names = [_name(i) for i in _list()]
    return flask.render_template("enum.html", name=name, names=names)

@app.route("/efficacy")
def efficacy():
    types = _vdex.type_list()
    names = [_vdex.type_name(t) for t in types]
    efficacy = [[_vdex.efficacy(a, d) for d in types] for a in types]
    return flask.render_template("efficacy.html", names=names, efficacy=efficacy)

@app.route("/items/")
def items():
    pockets = {}
    for item in _vdex.item_iter():
        item_name = _vdex.item_name(item)
        details = _vdex.item_details(item)
        category = (details.category, _vdex.item_category_name(details.category))
        pocket = (details.pocket, _vdex.pocket_name(details.pocket))
        pockets.setdefault(pocket, {}).setdefault(category, []).append((item, item_name))
    return flask.render_template("items.html", pockets=pockets)

VALID_ITEMS = list(_vdex.item_iter())

@app.route("/items/<int:item>")
def item(item):
    if item not in VALID_ITEMS:
        flask.abort(404)
    name = _vdex.item_name(item)
    details = _vdex.item_details(item)
    category = _vdex.item_category_name(details.category)
    pocket = _vdex.pocket_name(details.pocket)
    fling_effect = _vdex.fling_effect_name(details.fling_effect)
    flags = []
    for flag_name in _vdex.ITEM_FLAG:
        if details.flags & getattr(_vdex, "ITEM_FLAG_" + flag_name):
            flags.append(flag_name)
    natural_gift_type = _vdex.type_name(details.natural_gift_type)
    if details.flavor == _vdex.NO_DOMINANT_FLAVOR:
        flavor = "no dominant flavor"
    else:
        flavor = "primarily " + _vdex.flavor_name(details.flavor)
    return flask.render_template("item.html", **locals())

class Move:
    def __init__(self, move):
        self.move = move
        self.name = _vdex.move_name(move)
        self.details = details = _vdex.move_details(move)
        self.generation = _vdex.generation_name(details.generation)
        self.typ = _vdex.type_name(details.typ)
        self.power = details.power
        if self.power == 0:
            self.power = "--"
        elif self.power == 1:
            self.power = "*"
        self.accuracy = details.accuracy
        if self.accuracy == _vdex.NEVER_MISSES:
            self.accuracy = "--"
        self.target = _vdex.move_target_name(details.target)
        self.damage_class = _vdex.damage_class_name(details.damage_class)
        if self.damage_class == "NonDamaging":
            self.damage_class = "Status"
        self.effect = _vdex.move_effect_name(details.effect)
        self.effect_spaced = _vdex.to_snake_case(self.effect).replace("_", " ")
        self.category = _vdex.move_category_name(details.category)
        self.ailment = _vdex.ailment_name(details.ailment)
        self.stat_changes = []
        for index, name in enumerate(_vdex.STAT_CHANGE):
            change = details.stat_changes[index]
            if change != 0:
                self.stat_changes.append((change, name))
        self.flags = []
        for name in _vdex.MOVE_FLAG:
            if details.flags & getattr(_vdex, "MOVE_FLAG_" + name):
                self.flags.append(name)
        # Generate Summary
        self.extra = []
        def _c(chance):
            return 100 if chance == 0 else chance
        def _a(fmt, *args):
            self.extra.append(fmt.format(*args) + ".")
        if self.ailment != "None":
            _a("{}% {} chance", _c(details.ailment_chance), self.ailment)
        if details.min_hits != 1 or details.max_hits != 1:
            if details.min_hits == details.max_hits:
                _a("{} hits", details.max_hits)
            else:
                _a("{}-{} hits", details.min_hits, details.max_hits)
        if details.min_turns != 1 or details.max_turns != 1:
            if details.min_turns == details.max_turns:
                _a("{} turns", details.max_turns)
            else:
                _a("{}-{} turns", details.min_turns, details.max_turns)
        if details.recoil < 0:
            _a("{}% recoil", abs(details.recoil))
        elif details.recoil > 0:
            _a("{}% drain", details.recoil)
        if details.healing != 0:
            _a("{}% healing", details.healing)
        if details.critical_rate > 0:
            _a("Increased critical rate")
        if details.flinch_chance > 0:
            _a("{}% flinch chance", details.flinch_chance)
        if self.stat_changes == [(1, name) for name in _vdex.STAT_CHANGE[:5]]:
            _a("{}% chance to +1 all stats", _c(details.stat_chance))
        elif self.stat_changes:
            changes = " and ".join(["{:+d} {}".format(change, name.lower()
                .replace("_", " ")) for change, name in self.stat_changes])
            if _c(details.stat_chance) == 100:
                _a("{}", changes)
            else:
                _a("{}% chance for {}", _c(details.stat_chance), changes)

@app.route("/moves/")
def moves():
    moves = [Move(move) for move in range(_vdex.MOVE_COUNT)]
    return flask.render_template("moves.html", moves=moves)

@app.route("/moves/<int:move>")
def move(move):
    return flask.render_template("move.html", move=Move(move))

@app.route("/palace")
def palace():
    rows = zip([_vdex.nature_name(nature) for nature in _vdex.nature_list()],
            _vdex.palace_low_attack(), _vdex.palace_low_defense(),
            _vdex.palace_high_attack(), _vdex.palace_high_defense())
    return flask.render_template("palace.html", rows=rows)
