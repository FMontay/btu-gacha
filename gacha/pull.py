import random
from .cards import cards_id

TIER_ORDER = ["E", "D", "C", "B", "A", "S", "SS", "CURSED", "GOBLIN"]

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

def tier_selector(): #convertion to list because 'random' needs lists
    tiers = list(pull_rates.keys())
    weights = list(pull_rates.values())
    return random.choices(tiers, weights=weights, k=1)[0]


def pull_card():
    tier = tier_selector() #chooses a random tier based on probabilities
    cards = cards_id[tier] #in the obtained tier, looks through the tier's cards
    card_id = random.choice(list(cards.keys())) #randomly chooses a card id
    card = cards[card_id] #gathers the card id's data
    return tier, card_id, card #returns the tier and the card id


def new_rates(tier):
    # Find the index of the converted tier
    tier_index = TIER_ORDER.index(str)

    # Keep only tiers strictly above the converted tier
    eligible_tiers = TIER_ORDER[tier_index + 1:]

    # Get their original rates
    eligible_rates = {t: pull_rates[t] for t in eligible_tiers}

    # Normalize so the rates add up to 1.0
    total = sum(eligible_rates.values())
    normalized = {t: round(rate/total, 4) for t, rate in eligible_rates.items()}

    return normalized

