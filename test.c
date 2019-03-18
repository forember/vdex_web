#include <stdint.h>
#include <stdio.h>

void* vdex_pokemon(uint16_t species, size_t pokemon_index);

enum {
    VDEX_PERMANENT_STATS = 6,
};

struct VDexPokemonDetails {
    uint16_t id;
    uint8_t ability1;
    uint8_t has_ability2;
    uint8_t ability2;
    uint8_t has_hidden_ability;
    uint8_t hidden_ability;
    uint8_t stats[VDEX_PERMANENT_STATS];
    uint8_t type1;
    uint8_t has_type2;
    uint8_t type2;
};

struct VDexPokemonDetails vdex_pokemon_details(void* pokemon);

int main(int argc, char** argv)
{
    void* pokemon = vdex_pokemon(0, 0);
    fprintf(stderr, "pointer (C): %p\n", pokemon);
    struct VDexPokemonDetails details = vdex_pokemon_details(pokemon);
    fprintf(stderr, "ability: %d\n", details.ability1);
}
