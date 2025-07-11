import discord 
from discord.ext import commands 
import logging 
from dotenv import load_dotenv
import os
from collections import Counter

from gacha.pull import *
from gacha.cards import cards_id

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')


#Variables to define

#Role for specific debug commands
secret_role = "God"

#Binder unique to each user
user_binder = {}


@bot.event
async def on_ready():
    print(f"{bot.user.name} online. Let's go.")

@bot.command()
async def help(ctx):
    """You're literally using it, but idk how to remove it from the list."""
    embed = discord.Embed(
        title="List of commands",
        color=discord.Colour.blue()
    )
    for cmd in bot.commands:
        if any(getattr(check, "__qualname__", "").startswith("has_role") for check in cmd.checks):
            continue
        embed.add_field(
            name=f"!{cmd}",
            value=cmd.help or "I forgor.",
            inline=False
        )
    await ctx.send(embed=embed)



@bot.command()
@commands.has_role(secret_role)
async def add(ctx, id_card:str, user:discord.Member, amount:int):
    """!add <id_card> <@username> <amount> -- adds a specific card to X user."""
#quand je trouve l'id (id_card), j'ai aussi besoin de récupérer les informations sur la carte
#(tier, name, info...). Donc besoin de trouver d'abord si la carte EXISTE, puis de récupérer data.

    found = False
    for tier, cards in cards_id.items():
        if id_card in cards:
            card_info = cards[id_card]
            found = True
            break
    
    if not found:
        await ctx.send(f"Card ID '{id_card}' couldn't be found, cock sucker.")
        return

    user_id = user.id
    if user_id not in user_binder:
        user_binder[user_id] = []

    for _ in range(amount):
        user_binder[user_id].append((id_card, card_info['name'], tier))

    await ctx.send(f"Successfully added {amount}x '{card_info['name']}' (ID {id_card}).")

    if id_card == '01':
        await ctx.send(f"@everyone {user.mention} RELEASED THE GOBLIN FROM ITS JAIL!!!!")

    

@bot.command()
@commands.has_role(secret_role)
async def delete(ctx, id_card:str, user:discord.Member, amount:int):
    """!delete <id_card> <@username> <amount> -- delete card from X user's binder."""
    
    user_id = user.id
    binder = user_binder.get(user_id,[])

    matching = [card for card in binder if card[0]==id_card]
    if not matching:
        await ctx.send(f"No card with ID '{id_card}' found in {user.mention}'s binder.")            
        return
    
    if amount > len(matching):
        await ctx.send(f"{user.mention} only has {len(matching)} cards. Please write a valid number.")
        return
    
    removed = 0
    new_binder = []
    for card in binder:
        if card[0] == id_card and removed < amount:
            removed += 1
            continue
        
        new_binder.append(card)
    user_binder[user_id] = new_binder

    await ctx.send(f"Successfully deleted {amount} card(s) with ID {id_card} from {user.mention}'s binder.")


@bot.command()
@commands.has_role(secret_role)
async def empty(ctx, user:discord.Member):
    """!empty <@username> -- deletes every card in X user's binder."""
    user_id = user.id
    binder = user_binder.get(user_id,[])

    if binder:
        user_binder[user_id] = []
        await ctx.send(f"Successfully cleared {user.mention}'s binder.")
    else:
        await ctx.send(f"The binder is already empty.")

@bot.command()
async def pull(ctx): #besoin d'ajouter la limite journalière plus tard.
    """Pull a card. Limited to 5 per day."""  

    tier, card_id, card = pull_card()
    user_id = ctx.author.id

    if user_id not in user_binder:
        user_binder[user_id] = []

    user_binder[user_id].append((card_id, card['name'], tier))
    pictures_path = card['image']

    if os.path.exists(pictures_path):
        file = discord.File(pictures_path, filename="image.png")

        if tier in ['E']:
            color=discord.Color.dark_blue()
        elif tier in ['D']:
            color=discord.Color.green()
        elif tier in ['C']:
            color=discord.Color.orange()
        elif tier in ['B']:
            color=discord.Color.blue()
        elif tier in ['A']:
            color=discord.Color.red()
        elif tier in ['S']:
            color=discord.Color.pink()
        elif tier in ['SS']:
            color=discord.Color.purple()
        elif tier in ['CURSED']:
            color=discord.Color.light_grey()
        else:
            color=discord.Color.gold()

        embed = discord.Embed(
            title=f"{card['name']} [{tier}]",
            description=card['info'],
            color=color
        )
        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)

        if tier in ['S','SS','CURSED']:
            await ctx.send(f"Congratulations ! You pulled a very rare card!")
        elif tier in ['GOBLIN']:
            await ctx.send(f"@everyone {ctx.author.mention} RELEASED THE GOBLIN FROM ITS JAIL!!!!")
        else:
            pass

    else:
        await ctx.send(f"Error : Image file not found for '{card['name']}'.")

@bot.command()
async def binder(ctx): #vérifier si c'est bien unique à chaque membre du serveur. N'est pas sauvegardé.
    """Check out your collection of cards."""
    user_id = ctx.author.id
    binder = user_binder.get(user_id, [])

    if not binder: #if binder is False / empty
        await ctx.send("Your binder is empty, stupid shit")
        return

    counter = Counter(binder) #counts occurences
    sorted_cards = sorted(counter.items(), key=lambda x: x[0][0])

    collection = ""
    for (id_card, card_name, card_tier), amount in sorted_cards:
        collection += f"{id_card}   {card_name}   {card_tier}   {amount}\n"

    embed = discord.Embed(
        title="BTU Cards Collection",
        description=collection
    )

    await ctx.send(embed=embed)



bot.run(token, log_handler=handler, log_level=logging.DEBUG) #debug et informations ajoutées à 'discord.log'