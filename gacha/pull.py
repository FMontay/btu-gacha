import random
from .cards import cards_id

#Pull rates for the tiers of the cards
pull_rates = {
    "GOBLIN":0.0001,
    "CURSED":0.001,
    "SS":0.01,
    "S":0.03,
    "A":0.06,
    "B":0.1,
    "C":0.15,
    "D":0.25,
    "E":0.3989
}

def tier_selector(): #conversion en liste car 'random' a besoin de listes
    tiers = list(pull_rates.keys())
    weights = list(pull_rates.values())
    return random.choices(tiers, weights=weights, k=1)[0]


def pull_card():
    tier = tier_selector() #choisit un tier au hasard selon les probabilités
    cards = cards_id[tier] #dans le tier obtenu, regarde toutes les cartes
    card_id = random.choice(list(cards.keys())) #choisit au hasard l'ID d'une carte
    card = cards[card_id] #récupère les données de l'ID de la carte choisit
    return tier, card_id, card #redonne le tier & la carte