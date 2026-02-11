import discord
from tinytag import TinyTag

execute = "DIRECTORY_TO_ffmpeg.exe"
directory = "data/"
crimes = []
mafia_players = []
mafia_game = []
mafia_vc = None
story = None
story_length = 0
mafia_sounds = []


#  Mute [True, False]
async def mute_manage_mafia_players(mute):

    for person in mafia_game[0].players:
        if person.alive:
            try:
                await person.info.edit(mute=mute)
            except:
                pass


async def change_music(index):
    global mafia_vc
    rewrite_sounds()
    mafia_vc.stop()
    if index == 100:
        mafia_vc.play(story)
    else:
        mafia_vc.play(mafia_sounds[index])


async def music_init_(channel):
    global mafia_vc
    mafia_vc = await channel.connect()


def update_story():
    global story
    global story_length

    story = discord.FFmpegPCMAudio(executable=execute,
                                   source=f"{directory}story.mp3")
    track = TinyTag.get(f"{directory}story.mp3")
    story_length = track.duration


def rewrite_sounds():
    global mafia_sounds
    mafia_sounds.clear()
    mafia_sounds = [discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}midsummer_theme.mp3"),
                    discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}wwtbam.mp3"),
                    discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}scream.mp3"),
                    discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}pink_panther.mp3"),
                    discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}victory.mp3"),
                    discord.FFmpegPCMAudio(executable=execute,
                                           source=f"{directory}defeat.mp3")]
