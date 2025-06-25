import discord 
from discord.ext import commands 
import logging 
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

secret_role = "test"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event #A SUPPRIMER, C'EST JUSTE POUR LE TUTO
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event #A SUPPRIMER, C'EST JUSTE POUR LE TUTO
async def on_message(message):
    #ignore les messages du bot. Evite les loops.
    if message.author == bot.user:
        return 
    
    #Mise en place d'un autocensor. 'lower()' afin d'éviter pbs de capitalisation.
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} don't use that word!!!!")

    await bot.process_commands(message) #allows to process other messages. NECESSAIRE!

@bot.command() #A SUPPRIMER
async def hello(ctx): #!hello
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command() #A SUPPRIMER
async def assign(ctx): #assigner un rôle PREEXISTANT
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}.")
    else:
        await ctx.send("Role doesn't exist")

@bot.command() #A SUPPRIMER
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} role removed.")
    else:
        await ctx.send("Role doesn't exist")


@bot.command() #SUPPRIMER
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said '{msg}'") #!dm hello world

@bot.command() #SUPPRIMER
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")


@bot.command() #SUPPRIMER
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club.")

@secret.error #SUPPRIMER
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("you do not have permission to do that.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG) #debug et informations ajoutées à 'discord.log'