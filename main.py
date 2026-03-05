#Import necessary libraries
import discord 
from discord.ext import commands 
import logging 
from dotenv import load_dotenv
import os
from collections import Counter

#Import db functions
from database.db import initialize
from database.binder import get_user_binder, add_card, remove_card, clear_binder

#Import the functions and cards for the main discord commands
from gacha.pull import *
from gacha.cards import cards_id

initialize()


#Starting up Discord Bot
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

#Create log folder if it doesn't already exist and set up log file name
os.makedirs('logs', exist_ok=True)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')

#choice of intents for the bot -- its authorisations. Should sync with Discord Dev choices
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#choice of bot prefix to use commands
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help') #removed 'help' for my own customised "help" command


#Variables to define
#Role for specific debug commands
secret_role = "God"


#Start the bot
@bot.event
async def on_ready():
    print(f"{bot.user.name} online. Let's go.")



#Check for available commands
@bot.command()
async def help(ctx):
    """You're literally using it dumbass, but idk how to remove it from the list.""" 
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




#If Admin role (God), can do the following commands

# Add card.s to X user's binder
@bot.command()
@commands.has_role(secret_role)
async def add(ctx, id_card:str, user:discord.Member, amount:int):
    """!add <id_card> <@username> <amount> -- adds a specific card to X user."""
#When I find the card id, I also need to get the card's data
#(tier, name, info...). Need to check if the card exists first, then get the data.

    found = False
    for tier, cards in cards_id.items():
        if id_card in cards:
            card_info = cards[id_card]
            found = True
            break
    
    if not found:
        await ctx.send(f"Card ID '{id_card}' couldn't be found.")
        return

    user_id = user.id

    add_card(user_id, id_card, card_info['name'], tier, card_info['info'], amount)
    await ctx.send(f"Successfully added {amount}x '{card_info['name']}' (ID {id_card}).")

    #FOR TESTING PURPOSES
    if id_card == '01':
        await ctx.send(f"@everyone {user.mention} RELEASED THE GOBLIN FROM ITS JAIL!!!!")

    
# Delete X user's card.s
@bot.command()
@commands.has_role(secret_role)
async def delete(ctx, id_card:str, user:discord.Member, amount:int):
    """!delete <id_card> <@username> <amount> -- delete card from X user's binder."""
    
    #get user id & binder
    user_id = user.id
    rows = get_user_binder(user_id)

    #check if card exists in the binder
    matching = [r for r in rows if r[0]==id_card]
    if not matching:
        await ctx.send(f"No card with ID '{id_card}' found in {user.mention}'s binder.")            
        return
    
    #check if the amount you want to delete is superior to the maximum amount the user has
    if amount > matching[0][3]:
        await ctx.send(f"{user.mention} only has {matching[0][3]} cards. Please write a valid number.")
        return
    
    remove_card(user_id, id_card, amount)
    await ctx.send(f"Successfully deleted {amount} card(s) with ID {id_card} from {user.mention}'s binder.")


#Empty X user's binder
@bot.command()
@commands.has_role(secret_role)
async def empty(ctx, user:discord.Member):
    """!empty <@username> -- deletes every card in X user's binder."""
    user_id = user.id
    rows = get_user_binder(user_id)

    if not rows:
        await ctx.send(f"The binder is already empty.")  
    else:
        clear_binder(user_id)
        await ctx.send(f"Successfully cleared {user.mention}'s binder.")





#Normal commands

#Get a random card based on its rarity. The limit isn't added yet.
@bot.command()
async def pull(ctx): #Need to add daily limit
    """Pull a card. Limited to 5 per day."""  

    #uses the functions and variable imported from gacha.pull & gacha.cards
    tier, card_id, card = pull_card()
    user_id = ctx.author.id

    add_card(user_id, card_id, card['name'], tier, card['info'])

    pictures_path = card['image']

    #The pictures are temporarily local. I need to upload them to the web once I want to permanently host the bot. This is just for testing
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

    #only happens if internal error within my local files
    else:
        await ctx.send(f"Error : Image file not found for '{card['name']}'.")


#Check cards obtained in binder
@bot.command()
async def binder(ctx): #Check if unique to each user. Need to add a saving system when the bot disconnects.
    """Check out your collection of cards."""
    user_id = ctx.author.id
    rows = get_user_binder(user_id)

    if not rows: #if binder is False / empty
        await ctx.send("Your binder is empty, peasant.")
        return
    
    for (card_id, card_name, card_tier, amount) in rows:
        collection += f"{card_id}   {card_name}   {card_tier}   {amount}\n"

    embed = discord.Embed(
        title="BTU Cards Collection",
        description=collection #displays only card id, card name, card tier and amount for ergonomic purposes
    )

    await ctx.send(embed=embed)



bot.run(token, log_handler=handler, log_level=logging.DEBUG) #debug and info added to 'discord.log'