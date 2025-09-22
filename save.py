#Not defined method yet -- Might go for SQL instead

from main import user_binder

import json

def save_binder():
    list_binder = {str(k): [list(card) for card in v] for k, v in user_binder.items()}
    path = "path to saves"

    with open(f"{path}/binder.json", "w", encoding='utf-8') as f:
        json.dump(list_binder, f) #convert keys to string, hopefully


def load_binder(): #call before bot startup, after defining user_binder = {}
    global user_binder
    path = "path to saves"
    
    try:
        with open(f"{path}/binder.json", "r", encoding="utf-8") as f: 
            data = json.load(f)
            #convert keys back to int
            user_binder = {int(k): [tuple(card) for card in v] for k, v in data.items()}
    except FileNotFoundError:
        user_binder = {}
