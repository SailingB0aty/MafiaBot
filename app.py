import discord
from discord.ext import commands
import datetime
from shared_lists import crimes, mafia_players, mafia_game
import shared_lists
from mafia import Mafia

TOKEN = "Njk4NjYwMzI5MjAyMzg1MDM5.XpJMAA.A7bOzdmdrsKjZQ5f8yppW-6bcxY"
client = commands.Bot(command_prefix=">")
mafia_initialized = False

@client.event
async def on_ready():
    print(f"[{datetime.datetime.now()}]  At your service, master!")

@client.command()
async def mafia(ctx):
    global mafia_initialized

    try:
        if len(mafia_game) > 0:
            await ctx.send("A game is already in progress")
        else:
            channel = ctx.author.voice.channel
            await shared_lists.music_init_(channel)
            await shared_lists.change_music(0)
            mafia_initialized = True
            await ctx.send(
                "If you would like to be involved in the game of mafia, please say **Join**. Once all have joined, say **Start**")
    except:
        await ctx.send("You must be in a voice chat to play mafia")

@client.event
async def on_message(message):
    global mafia_initialized
    text = message.content.lower()

    if not message.author.name == "Mafia":
        if mafia_initialized:
            if message.author not in mafia_players and "join" in text:
                mafia_players.append(message.author)
                await message.channel.send(f"{message.author.mention} added to the game")
            elif message.author in mafia_players and "start" in text:
                #  Initialize game here
                if len(mafia_players) > 4:
                    await shared_lists.change_music(1)
                    mafia_game.append(Mafia(message.channel, mafia_players))
                    await shared_lists.mute_manage_mafia_players(True)
                    await Mafia.acknowledge_players(mafia_game[0])
                    mafia_initialized = False
                else:
                    await message.channel.send(f"At least 5 people must play: {len(mafia_players)}/5")
        #  Update mafia game
        for game in mafia_game:
            if message.author in game.raw_players:
                if game.stage == 1:
                    await mafia_game[0].stage_1_messages(message)
                elif game.stage == 2 and text.startswith("<@"):
                    await mafia_game[0].stage_2_messages(message)

        await client.process_commands(message)

client.run(TOKEN)
