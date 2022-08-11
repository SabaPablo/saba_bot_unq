# main.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random
import requests
from fix import start_correction

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print("Starting bot...")

client = commands.Bot(command_prefix = '.')

#We delete default help command
client.remove_command('help')


#answers with the ms latency
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (client.latency * 1000)}ms ')


#Embeded help with list and details of commands
@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.green())
    embed.set_author(name='Help : list of commands available')
    embed.add_field(name='.ping', value='Returns bot respond time in milliseconds', inline=False)
    embed.add_field(name='.hello', value='??', inline=False)
    embed.add_field(name='.fix', value='Send corrections data', inline=False)
    await ctx.send(embed=embed)


@client.command()
async def fix(ctx):
    await ctx.send("mmmm.... dejame ver.")
    attachment_url = ctx.message.attachments[0].url
    if attachment_url[-3:] != 'gbs' :
        await ctx.send("dame un gbs, en otro formato ni me caliento")
        return
    file_request = requests.get(attachment_url)
    lines = file_request.content.decode("utf-8")
    errors = start_correction(lines)
    # write to file
    with open("result.txt", "w") as file:
        for line in errors:
            file.write(line)
            file.write('\n')

    # send file to Discord in message
    with open("result.txt", "rb") as file:
        await ctx.send("Listo, corregido:", file=discord.File(file, "result.txt"))
    await ctx.send("Tene en cuenta que solo se corregir algunas cosas, podrian faltar otras correcciones.")

        #Answers with a random quote
@client.command()
async def quote(ctx):
    responses = open('quotes.txt').read().splitlines()
    random.seed(a=None)
    response = random.choice(responses)
    await ctx.send(response)

#If there is an error, it will answer with an error
@client.event
async def on_command_error(ctx, error):
    await ctx.send(f'Error. Try .help ({error})')



print("Bot is ready!")
client.run(TOKEN)