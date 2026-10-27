import json
import os

POKEMON_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "pokemon_list.json")

RESTRICTED_LEGENDARIES = {
    'koraidon', 'miraidon', 'calyrex', 'calyrex-ice', 'calyrex ice rider', 'calyrex-shadow', 'calyrex shadow rider',
    'zacian', 'zacian-crowned', 'zacian crowned', 'zamazenta', 'zamazenta-crowned', 'zamazenta crowned',
    'kyogre', 'groudon', 'rayquaza', 'mewtwo', 'lugia', 'ho-oh', 'ho oh', 'dialga', 'dialga origin',
    'palkia', 'palkia origin', 'giratina', 'giratina origin', 'giratina altered', 'reshiram', 'zekrom',
    'kyurem', 'kyurem black', 'kyurem white', 'xerneas', 'yveltal', 'zygarde', 'zygarde 50', 'zygarde complete',
    'solgaleo', 'lunala', 'necrozma', 'necrozma dusk mane', 'necrozma dawn wings', 'necrozma ultra',
    'eternatus', 'terapagos', 'terapagos terastal', 'terapagos-terastal', 'terapagos stellar', 'terapagos-stellar',
    'cosmog', 'cosmoem'
}

SUB_LEGENDARIES = {
    # Ruin Quartet
    'chien-pao', 'chien pao', 'ting-lu', 'ting lu', 'chi-yu', 'chi yu', 'wo-chien', 'wo chien',
    # Forces of Nature
    'landorus', 'landorus-therian', 'landorus therian', 'landorus-incarnate', 'landorus incarnate',
    'tornadus', 'tornadus-therian', 'tornadus therian', 'tornadus-incarnate', 'tornadus incarnate',
    'thundurus', 'thundurus-therian', 'thundurus therian', 'thundurus-incarnate', 'thundurus incarnate',
    'enamorus', 'enamorus-therian', 'enamorus therian', 'enamorus-incarnate', 'enamorus incarnate',
    # Urshifu
    'urshifu', 'urshifu-rapid-strike', 'urshifu rapid strike', 'urshifu-single-strike', 'urshifu single strike',
    'urshifu-r', 'urshifu-s', 'kubfu',
    # Loyal Three & Ogerpon
    'okidogi', 'munkidori', 'fezandipiti',
    'ogerpon', 'ogerpon teal', 'ogerpon-teal', 'ogerpon wellspring', 'ogerpon-wellspring',
    'ogerpon hearthflame', 'ogerpon-hearthflame', 'ogerpon cornerstone', 'ogerpon-cornerstone',
    # Birds
    'articuno', 'zapdos', 'moltres', 'galarian articuno', 'articuno-galar', 'galarian zapdos', 'zapdos-galar', 'galarian moltres', 'moltres-galar',
    # Beasts
    'raikou', 'entei', 'suicune',
    # Swords of Justice
    'cobalion', 'terrakion', 'virizion',
    # Lake Guardians
    'uxie', 'mesprit', 'azelf',
    # Heatran, Cresselia, Regis, Eons
    'heatran', 'cresselia', 'regirock', 'regice', 'registeel', 'regieleki', 'regidrago', 'latios', 'latias',
    # Tapus & Ultra Beasts
    'tapu koko', 'tapu lele', 'tapu bulu', 'tapu fini', 'nihilego', 'buzzwole', 'pheromosa', 'xurkitree', 'celesteela', 'kartana', 'guzzlord', 'poipole', 'naganadel', 'stakataka', 'blacephalon',
    'silvally', 'type: null', 'type null'
}

PARADOX_POKEMON = {
    'great tusk', 'scream tail', 'brute bonnet', 'flutter mane', 'slither wing', 'sandy shocks',
    'iron treads', 'iron bundle', 'iron hands', 'iron jugulis', 'iron moth', 'iron thorns',
    'roaring moon', 'iron valiant', 'walking wake', 'iron leaves', 'gouging fire', 'raging bolt',
    'iron boulder', 'iron crown'
}

MYTHICAL_POKEMON = {
    'mew', 'celebi', 'jirachi', 'deoxys', 'deoxys attack', 'deoxys defense', 'deoxys speed', 'deoxys normal',
    'phione', 'manaphy', 'darkrai', 'shaymin', 'shaymin land', 'shaymin sky', 'arceus', 'victini',
    'keldeo', 'keldeo ordinary', 'keldeo resolute', 'meloetta', 'meloetta aria', 'meloetta pirouette',
    'genesect', 'diancie', 'hoopa', 'hoopa unbound', 'volcanion', 'magearna', 'magearna original',
    'marshadow', 'zeraora', 'meltan', 'melmetal', 'zarude', 'pecharunt'
}

def is_mega_pokemon(name):
    low = name.lower()
    if 'meganium' in low or 'yanmega' in low:
        return False
    return 'mega' in low

REGULATION_CONFIGS = {
    "Regulation M-C": {
        "id": "Regulation M-C",
        "name": "Regulation M-C (Pokémon Champions Season 3)",
        "badge": "Reg M-C",
        "description": "Official Pokémon Champions Regulation Set M-C: Features Z-Megas (Mega Garchomp Z, Mega Lucario Z, Mega Absol Z), new Megas (Mega Baxcalibur, Mega Golisopod, Mega Salamence), Rillaboom, and Indeedee. Standard double battle rules.",
        "allow_restricted": False,
        "allow_sub_legends": False,
        "allow_paradox": False,
        "allow_mythicals": False,
        "allow_megas": True,
        "ai_prompt": "CRITICAL POKÉMON CHAMPIONS REGULATION M-C RULES: This battle is under Regulation M-C. Mega Evolutions are active and prominent! Watch out especially for Z-Megas (Mega Garchomp Z, Mega Lucario Z, Mega Absol Z), format Megas (Mega Salamence, Mega Golisopod, Mega Baxcalibur, Mega Charizard Y, Mega Kangaskhan, Mega Gengar, Mega Dragonite, Mega Raichu X/Y, Mega Metagross, Mega Aerodactyl, Mega Tyranitar, Mega Venusaur, Mega Blastoise), and staple M-C partners (Rillaboom, Indeedee-Female, Indeedee-Male, Archaludon, Sneasler, Basculegion, Incineroar, Gholdengo, Farigiraf, Pelipper, Swampert, Sinistcha, Annihilape, Volcarona, Dondozo, Tatsugiri). No box legendaries or paradoxes."
    },
    "Regulation M-B": {
        "id": "Regulation M-B",
        "name": "Regulation M-B (Pokémon Champions Season 2)",
        "badge": "Reg M-B",
        "description": "Pokémon Champions Regulation M-B: Features Mega Metagross, Mega Raichu X/Y, Mega Aerodactyl, and Farigiraf.",
        "allow_restricted": False,
        "allow_sub_legends": False,
        "allow_paradox": False,
        "allow_mythicals": False,
        "allow_megas": True,
        "ai_prompt": "Pokémon Champions Regulation M-B rules: Mega Evolutions enabled (Mega Metagross, Mega Raichu X, Mega Aerodactyl, Mega Charizard Y, Farigiraf, Gholdengo, Annihilape, Incineroar)."
    },
    "Regulation M-A": {
        "id": "Regulation M-A",
        "name": "Regulation M-A (Pokémon Champions Launch)",
        "badge": "Reg M-A",
        "description": "Initial Pokémon Champions launch format with foundational Megas (Mega Charizard Y, Mega Venusaur, Garchomp, Incineroar).",
        "allow_restricted": False,
        "allow_sub_legends": False,
        "allow_paradox": False,
        "allow_mythicals": False,
        "allow_megas": True,
        "ai_prompt": "Pokémon Champions Regulation M-A rules: Early Champions meta featuring foundational Megas (Mega Charizard Y, Mega Venusaur, Garchomp, Incineroar)."
    },
    "Regulation H": {
        "id": "Regulation H",
        "name": "Regulation H (Standard Dex, No Legends, No Paradox)",
        "badge": "Reg H",
        "description": "Official VGC Regulation H: Standard regional Pokémon only. All Legendaries (Restricted & Sub-Legendary), Paradox Pokémon, and Megas are BANNED. (Ursaluna-Bloodmoon is legal).",
        "allow_restricted": False,
        "allow_sub_legends": False,
        "allow_paradox": False,
        "allow_mythicals": False,
        "allow_megas": False,
        "ai_prompt": "CRITICAL REGULATION H RULES: NO Legendaries (no Calyrex, Koraidon, Miraidon, Urshifu, Landorus, Tornadus, Ogerpon, etc.), NO Paradox Pokémon (no Flutter Mane, Iron Hands, Iron Bundle, etc.), and NO Megas. ONLY standard regional Pokémon are legal (e.g., Sneasler, Basculegion, Incineroar, Archaludon, Gholdengo, Rillaboom, Ursaluna-Bloodmoon, Dondozo, Dragonite, Kingambit). Do NOT detect banned Pokémon."
    },
    "Regulation G": {
        "id": "Regulation G",
        "name": "Regulation G (1 Restricted Legendary + Paradox)",
        "badge": "Reg G",
        "description": "Official VGC Regulation G: Exactly 1 Restricted Legendary permitted per team. Paradox and Sub-Legendaries permitted. Megas and Mythicals banned.",
        "allow_restricted": True,
        "allow_sub_legends": True,
        "allow_paradox": True,
        "allow_mythicals": False,
        "allow_megas": False,
        "ai_prompt": "Regulation G rules: Exactly one Restricted Legendary (e.g. Calyrex-Shadow, Calyrex-Ice, Koraidon, Miraidon, Zacian, Kyogre, Groudon, Terapagos) per team. Sub-Legendaries (Urshifu, Landorus, Ogerpon) and Paradox Pokémon (Flutter Mane, Iron Hands) are legal. NO Megas."
    },
    "Champions / Mega": {
        "id": "Champions / Mega",
        "name": "Champions / Mega League (Open Megas)",
        "badge": "⚡ Mega",
        "description": "Open competitive battle format featuring all Mega Evolutions and competitive Pokémon.",
        "allow_restricted": True,
        "allow_sub_legends": True,
        "allow_paradox": True,
        "allow_mythicals": False,
        "allow_megas": True,
        "ai_prompt": "Champions League format: Mega Evolutions are enabled! Pay close attention to Mega-Evolved Pokémon."
    },
    "All / Open": {
        "id": "All / Open",
        "name": "All / Open (Unrestricted)",
        "badge": "Open",
        "description": "Full National Dex, no restrictions.",
        "allow_restricted": True,
        "allow_sub_legends": True,
        "allow_paradox": True,
        "allow_mythicals": True,
        "allow_megas": True,
        "ai_prompt": "Open regulation: All standard, Legendary, Paradox, and Mega Pokémon are legal."
    }
}

DEFAULT_REGULATION = "Regulation M-C"

def get_available_regulations():
    return [
        {
            "id": k,
            "name": v["name"],
            "badge": v["badge"],
            "description": v["description"]
        }
        for k, v in REGULATION_CONFIGS.items()
    ]

def is_pokemon_legal_in_regulation(pokemon_name, regulation_name):
    cfg = REGULATION_CONFIGS.get(regulation_name, REGULATION_CONFIGS["Regulation M-C"])
    low = pokemon_name.lower().strip()

    # Megas check
    if not cfg["allow_megas"] and is_mega_pokemon(low):
        return False

    # Mythicals check
    if not cfg["allow_mythicals"] and low in MYTHICAL_POKEMON:
        return False

    # Restricted check
    if not cfg["allow_restricted"] and low in RESTRICTED_LEGENDARIES:
        return False

    # Paradox check
    if not cfg["allow_paradox"] and low in PARADOX_POKEMON:
        return False

    # Sub-Legendaries check (Note: Bloodmoon Ursaluna is NOT a sub-legendary and is legal in Reg H & Reg M-C)
    if not cfg["allow_sub_legends"]:
        if low in SUB_LEGENDARIES:
            return False

    return True

def get_legal_pokemon_for_regulation(regulation_name):
    if not os.path.exists(POKEMON_LIST_PATH):
        return []
    try:
        with open(POKEMON_LIST_PATH, "r", encoding="utf-8") as f:
            all_pokemon = json.load(f)
    except Exception:
        return []

    cfg = REGULATION_CONFIGS.get(regulation_name, REGULATION_CONFIGS["Regulation M-C"])
    if regulation_name in ["All / Open", "Champions / Mega"]:
        if cfg["allow_mythicals"]:
            return all_pokemon
        return [p for p in all_pokemon if p.lower() not in MYTHICAL_POKEMON]

    return [p for p in all_pokemon if is_pokemon_legal_in_regulation(p, regulation_name)]

def get_regulation_ai_prompt(regulation_name):
    cfg = REGULATION_CONFIGS.get(regulation_name, REGULATION_CONFIGS["Regulation M-C"])
    return cfg.get("ai_prompt", "")
