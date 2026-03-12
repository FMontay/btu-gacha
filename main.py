#Import necessary libraries
import discord 
from discord.ext import commands 
import logging 
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

#Import db functions
from database.db import initialize
from database.binder import *
from database.pulls import *

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

DAILY_PULL_LIMIT = 3


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")

#Start the bot
@bot.event
async def on_ready():
    print(f"{bot.user.name} online. Let's go.")


#Check for EVERY available command (includes admin commands)
@bot.command()
@commands.has_role(secret_role)
async def devhelp(ctx):
    """Shows ALL the commands. For users with 'God' role.""" 

    embed = discord.Embed(
        title="List of every available command",
        color=discord.Colour.red()
    )
    for cmd in bot.commands:
        is_admin = any(getattr(check, "__qualname__", "").startswith("has_role") for check in cmd.checks)
        label = f"!{cmd} 👑" if is_admin else f"!{cmd}"
        embed.add_field(
            name=label,
            value=cmd.help or "You forgot to include a description stupid bitch",
            inline=False
        )
    await ctx.send(embed=embed)



#Check for available commands (no admin commands)
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
        await ctx.send(f"Successfully turned {user.mention}'s binder to dust.")


# Admin command to use the pull comand without being restrained by daily limit
@bot.command()
@commands.has_role(secret_role)
async def devpull(ctx): 
    """!devpull -- Pull a card. No limit. For test pulling and avoid being restrained by limited pull in case of glitch."""  

    #uses the functions and variable imported from gacha.pull & gacha.cards
    tier, card_id, card = pull_card()
    user_id = ctx.author.id

    add_card(user_id, card_id, card['name'], tier, card['info'])

    pictures_path = card['image']

    #The pictures are temporarily local. I need to upload them to the web once I want to permanently host the bot. This is just for testing
    if pictures_path.startswith("http"):

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
        embed.set_image(url=pictures_path)
        await ctx.send(embed=embed)

        if tier in ['S','SS','CURSED']:
            await ctx.send(f"Congratulations ! You pulled a very rare card!")
        elif tier in ['GOBLIN']:
            await ctx.send(f"@everyone {ctx.author.mention} RELEASED THE GOBLIN FROM ITS JAIL!!!!")
        else:
            pass
        

    else:
        await ctx.send(f"Error : Image file not found for '{card['name']}'.")



# Reset daily limit for X user
@bot.command()
@commands.has_role(secret_role)
async def reset(ctx, user:discord.Member): 
    """!reset <@username> -- Reset X user's daily limit (time limit and pull count)."""
    user_id = user.id
    row = get_pull_data(user_id)
    now = datetime.now(timezone.utc)

    if row:
        pull_count, last_reset_str = row
        last_reset = datetime.fromisoformat(last_reset_str).replace(tzinfo=timezone.utc)

        pull_count = 0
        last_reset = now - timedelta(hours=24) #reset time limit by going 24 hours into the past

    else:
        await ctx.send(f"{user.mention} hasn't pulled anything yet.")
        return

    update_pull_count(user_id, pull_count, last_reset.isoformat())

    await ctx.send(f"Daily limit successfully reset for {user.mention} !")


#Normal commands

#Get a random card based on its rarity. Limited to 3 pulls.
@bot.command()
async def pull(ctx):
    """!pull -- Pull a card. Limited to 3 per day in a 24h window."""  
    user_id = ctx.author.id

    #before pulling, check if limit is reached or not. If not, update it. If yes, show time until next available reset.
    now = datetime.now(timezone.utc) 

    row = get_pull_data(user_id)

    if row:
        pull_count, last_reset_str = row #decomposition of row from table
        last_reset = datetime.fromisoformat(last_reset_str).replace(tzinfo=timezone.utc)

        # If 24 hours have passed, reset the counter
        if now - last_reset >= timedelta(hours=24):
            pull_count = 0
            last_reset = now
        
    else:
        # First time this user pulls
        pull_count = 0
        last_reset = now
    
    if pull_count >= DAILY_PULL_LIMIT:
        time_remaining = (last_reset + timedelta(hours=24)) - now
        hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
        minutes = remainder // 60
        await ctx.send(f"Sorry sexy, you've reached your daily pull limit. Come back in {hours}h {minutes} minutes.")
        return
    
    # Increment and save before pulling
    update_pull_count(user_id, pull_count + 1, last_reset.isoformat())


    #uses the functions and variable imported from gacha.pull & gacha.cards
    tier, card_id, card = pull_card()
    
    add_card(user_id, card_id, card['name'], tier, card['info'])

    pictures_path = card['image']

    #The pictures are temporarily local. I need to upload them to the web once I want to permanently host the bot. This is just for testing
    if pictures_path.startswith("http"):

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
        embed.set_image(url=pictures_path)
        await ctx.send(embed=embed)

        if tier in ['S','SS','CURSED']:
            await ctx.send(f"Congratulations ! You pulled a very rare card!")
        elif tier in ['GOBLIN']:
            await ctx.send(f"@everyone {ctx.author.mention} RELEASED THE GOBLIN FROM ITS JAIL!!!!")
        else:
            pass


    else:
        await ctx.send(f"Error : Image file not found for '{card['name']}' :(")


#Check cards obtained in binder
@bot.command()
async def binder(ctx):
    """!binder -- Check out your collection of cards."""
    user_id = ctx.author.id
    rows = get_user_binder(user_id)

    if not rows: #if binder is False / empty
        await ctx.send("Your binder is empty, peasant.")
        return

    embed = discord.Embed(
        title="BTU Cards Collection",
        color=discord.Color.blue()
    )

    for (card_id, card_name, card_tier, amount) in rows:
        embed.add_field(
            name=f"{card_name} [{card_tier}]",
            value=f"ID: {card_id} | Copies: {amount}",
            inline=False
        )

    await ctx.send(embed=embed)



#Check specific card info
@bot.command()
async def info(ctx, id_card:str):
    """!info <card_id> -- Check a card's info : name, tier, description, id (01-70)"""
    user_id = ctx.author.id
    
    url = None
    for tier, cards in cards_id.items():
        if id_card in cards:
            url = cards[id_card]['image']
            break
    
    if not url:
        await ctx.send("Card data not found. Did you write the right ID (01-70) ?")
        return
    

    card = get_user_card(user_id, id_card)

    if not card:
        await ctx.send("You don't own that card.")
        return
    
    card_id, card_name, card_tier, card_description, quantity = card
    
    
    embed = discord.Embed(
            title=f"{card_name} [{card_tier}]",
            description=card_description,
            color=discord.Color.gold()
        )
    
    embed.set_footer(text=f"ID: {card_id}")
    embed.set_image(url=url)
    await ctx.send(embed=embed)
    

#Check remaining time until next available pulls
@bot.command()
async def check(ctx):
    """!check -- Check the remaining pulls you have, or time limit until daily limit reset."""
    user_id = ctx.author.id
    now = datetime.now(timezone.utc) 

    row = get_pull_data(user_id)

    if row is None:
        await ctx.send(f"Your pulls are fresh and ready! You have {DAILY_PULL_LIMIT} pulls remaining.")
        return

    else:
        pull_count, last_reset_str = row #decomposition of row from table
        last_reset = datetime.fromisoformat(last_reset_str).replace(tzinfo=timezone.utc)

        if now - last_reset >= timedelta(hours=24):
            await ctx.send(f"Your pulls are fresh and ready! You have {DAILY_PULL_LIMIT} pulls remaining.")
            return
        
        elif pull_count >= DAILY_PULL_LIMIT:
            time_remaining = (last_reset + timedelta(hours=24)) - now
            hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
            minutes = remainder // 60
            await ctx.send(f"Your pulls reset in {hours}h{minutes} minutes.")
            return

        else:
            await ctx.send(f"You still got a couple pulls ! You have {DAILY_PULL_LIMIT - pull_count} pulls remaining.")
            return


#Convert 10 duplicates of a card into a free guaranteed higher tier pull
@bot.command()
async def convert(ctx, card_id):
    """!convert <card_ID> -- Convert 10 duplicates into 1 free pull. Higher tier guaranteed."""
    user_id = ctx.author.id

    # Check if the card exists in cards_id
    found = False
    for tier, cards in cards_id.items():
        if card_id in cards:
            found = True
            break
    if not found:
        await ctx.send(f"Card ID '{card_id}' couldn't be found.")
        return

    
    # Check if the user owns that card and has enough duplicates
    card = get_user_card(user_id, card_id)
    if not card:
        await ctx.send("You don't own that card, sorry.")
        return
    
    card_id_db, card_name, card_tier, card_description, quantity = card
    max_convertible = (quantity // 10) * 10 #ground floor division

    if max_convertible < 10:
        await ctx.send(f"You only have {quantity} copies of that card. The minimum to convert should be 10, sorry sexy.")
        return
    
    elif max_convertible >= 20:
        await ctx.send(f"(Please write your answer) You have {quantity} copies of that card. How many free pulls do you want ? (10 duplicates = 1 free pull)")

        def check_author(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await bot.wait_for("message", check=check_author, timeout=30.0)
        except TimeoutError:
            await ctx.send(f"You took too long to answer, gotta cancel the conversion, sorry")
            return
        try:
            amount = int(msg.content)
        except ValueError:
            await ctx.send("You need to write a number dumbass. (conversion cancelled)")
            return
        
        
        if amount % 10 != 0 or amount < 10:
            await ctx.send("Your answer should be in a range of dozens (10, 20, 30...). Please retry. (conversion cancelled)")
            return

        if amount > max_convertible: #if number input is higher than owned duplicates ('30', but only 26 copies)
            await ctx.send(f"You only have {quantity} copies of the card '{card_name}'. Please retry. (conversion cancelled)")
            return
        
        if amount == 10:
            remove_card(user_id, card_id, 10)
            add_converted_pull(user_id, tier, 1)
            await ctx.send(f"Successfully converted 10 copies of {card_name} into 1 free pull of tier {card_tier} and higher !")
            return
        
        pulls_gained = amount//10
        
        #if no error and answer is 20 or more, proceed
        remove_card(user_id, card_id, amount)
        add_converted_pull(user_id, tier, pulls_gained)
        await ctx.send(f"Successfully converted {msg.content} copies of {card_name} into {pulls_gained}x free pulls of tier {card_tier} and higher !")

    
    else: #if max convertible = 10
        prompt = await ctx.send(f"You are about to convert 10 duplicates of the card '{card_name}' into a free pull. Do you wish to proceed ?")
        await prompt.add_reaction("✅")
        await prompt.add_reaction("❌")

        def check_author(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == prompt.id
        try:
            reaction, _ = await bot.wait_for("reaction_add", check=check_author, timeout=30.0)
        except TimeoutError:
            await ctx.send(f"You took too long to answer, gotta cancel the conversion, sorry")
            return
        
        if str(reaction.emoji) == "❌":
            await ctx.send("Ok fuck off")
            return

        #if no error, proceed
        remove_card(user_id, card_id, 10)
        add_converted_pull(user_id, tier, 1)
        await ctx.send(f"Successfully converted 10 copies of {card_name} into 1 free pull of tier {card_tier} and higher !")


#Check the amount of free pulls you have
@bot.command()
async def fpcheck(ctx):
    """!fpcheck -- Check the amount of free pulls you have."""
    user_id = ctx.author.id
    rows = check_free_pulls(user_id)

    if not rows:
        await ctx.send("You don't have any free pulls.")
        return 
    
    embed = discord.Embed(
        title="Collected free pulls",
        color=discord.Color.pink()
    )

    for (pull_tier, quantity) in rows:
        embed.add_field(
            name=f"Tier {pull_tier}+",
            value=f"Amount: {quantity}"
        )

    await ctx.send(embed=embed)


bot.run(token, log_handler=handler, log_level=logging.DEBUG) #debug and info added to 'discord.log'


# delete message prompt after validation (not answer)
# add error prevention before card removal
# need to order fpcheck by tiers