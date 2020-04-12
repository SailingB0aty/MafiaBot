import random
import asyncio
import discord
import shared_lists
from gtts import gTTS

got_story = False

class Round:
    def __init__(self, killed, breaded, saved, accused):
        self.killed = killed
        self.breaded = breaded
        self.saved = saved
        self.accused = accused
        self.votes = []
        self.voted = []
        self.to_die = None


class Player:
    def __init__(self, info, role):
        self.info = info
        self.role = role
        self.alive = True
        self.dm_channel = None


class Mafia:
    def __init__(self, channel, players):
        self.raw_players = players
        self.killer = self.get_killer(players)
        self.doctor = self.get_doctor(players)
        self.sheriff = self.get_sheriff(players)
        self.breadman = self.get_breadman(players)
        self.civilians = self.get_civilians(players)

        self.channel = channel
        self.players = self.get_all_players(players)

        #  0 ==> choose players
        #  1 ==> ask players for choices
        #  2 ==> tell story and get users to vote
        #  3 ==> reveal who was killer
        self.stage = 0
        self.round = Round(None, None, None, None)
        self.dead_id = []

    def get_killer(self, players):
        killer = Player(players[random.randint(0, len(players) - 1)], "killer")
        return killer

    def get_doctor(self, players):
        selected = False
        person = players[random.randint(0, len(players) - 1)]
        while not selected:
            if person != self.killer.info:
                return Player(person, "doctor")
                selected = True
            else:
                person = players[random.randint(0, len(players) - 1)]

    def get_sheriff(self, players):
        selected = False
        person = players[random.randint(0, len(players) - 1)]
        while not selected:
            if person != self.killer.info and person != self.doctor.info:
                return Player(person, "sheriff")
                selected = True
            else:
                person = players[random.randint(0, len(players) - 1)]

    def get_breadman(self, players):
        selected = False
        person = players[random.randint(0, len(players) - 1)]
        while not selected:
            if person != self.killer.info and person != self.doctor.info and person != self.sheriff.info:
                return Player(person, "bread man")
                selected = True
            else:
                person = players[random.randint(0, len(players) - 1)]

    def get_civilians(self, players):
        civilians = []
        for person in players:
            if person != self.killer.info and person != self.doctor.info and person != self.sheriff.info and person != self.breadman.info:
                civilians.append(Player(person, "civilian"))
        return civilians

    def get_all_players(self, players):
        players = [self.killer, self.doctor, self.sheriff, self.breadman]
        for person in self.civilians:
            players.append(person)
        return players

    #  Sets the civilians, and roles to match the players list
    def update_players(self):
        new_players = []
        for player in self.players:
            if player.role == "civilian":
                new_players.append(player)
            elif player.role == "bread man":
                self.breadman = player
            elif player.role == "killer":
                self.killer = player
            elif player.role == "doctor":
                self.doctor = player
            elif player.role == "sheriff":
                self.sheriff = player
        self.civilians = new_players

    #  Updates player list to include dm_channels
    def update_player_list(self):
        for x in range(len(self.players)):
            if self.players[x].role == "bread man":
                self.players[x] = self.breadman
            elif self.players[x].role == "killer":
                self.players[x] = self.killer
            elif self.players[x].role == "doctor":
                self.players[x] = self.doctor
            elif self.players[x].role == "sheriff":
                self.players[x] = self.sheriff

    #  Returns the list of players and their status
    def embed_player_status(self):
        embed = discord.Embed(title="---Population Report---", colour=discord.Colour.blue())
        for player in self.players:
            if player.alive:
                embed.add_field(name=f"{player.info.display_name}", value="😊", inline=False)
            else:
                embed.add_field(name=f"{player.info.display_name}", value=f"☠️   ------------->   {player.role}", inline=False)
        return embed

    #  Creates text to speech file
    @staticmethod
    def story_to_speech(story):
        global got_story
        language = 'en'

        output = gTTS(text=story, lang=language, slow=False)
        output.save("data/story.mp3")
        got_story = True

        shared_lists.update_story()



    #  STAGE 1 FUNCTIONS
    async def acknowledge_players(self):
        try:
            await self.killer.info.send("...Initializing Mafia...")
            self.killer.dm_channel = self.killer.info.dm_channel
        except:
            self.killer.dm_channel = self.channel.guild.channels[4]
        try:
            await self.doctor.info.send("...Initializing Doctor...")
            self.doctor.dm_channel = self.doctor.info.dm_channel
        except:
            self.doctor.dm_channel = self.channel.guild.channels[5]
        try:
            await self.sheriff.info.send("...Initializing Sheriff...")
            self.sheriff.dm_channel = self.sheriff.info.dm_channel
        except:
            self.sheriff.dm_channel = self.channel.guild.channels[6]
        try:
            await self.breadman.info.send("...Initializing Bread Man...")
            self.breadman.dm_channel = self.breadman.info.dm_channel
        except:
            self.breadman.dm_channel = self.channel.guild.channels[7]

        self.update_player_list()
        self.stage = 1
        await self.killer.dm_channel.send(
            f"{self.killer.info.mention}, You are the **Mafia**! The Jeff city cartel have hired you to eliminate all of the townsfolk. You must do so without raising suspicion...")
        await self.doctor.dm_channel.send(
            f"{self.doctor.info.mention}, You are the **Doctor**! After graduating Jeff city medical school in the year 2004, you have spent many years as a successful trauma doctor. Will you be able to save the towns people from the evil cartel? or will you be selfish and save yourself...?")
        await self.sheriff.dm_channel.send(
            f"{self.sheriff.info.mention}, You are the **Sheriff**! The Jeff city Cartel are on a mission to wipe out the town... Can you deduce who is responsible, and bring them to justice...?")
        await self.breadman.dm_channel.send(
            f"{self.breadman.info.mention}, You are the **Bread man**! It's your duty to keep the Jeff city people stocked up with bread")
        await self.stage_1_init_()

    #  Returns True is Sheriff guesses correctly
    def sheriff_correct(self, display_name):
        for person in self.players:
            if person.role == "killer" and person.info.display_name == display_name:
                return True
        return False

    async def stage_1_init_(self):

        await self.killer.dm_channel.send("Who would you like to kill? (Enter their display name as it appears in the group)")
        if self.sheriff.alive:
            await self.sheriff.dm_channel.send("Who would you like to accuse? (Enter their display name as it appears in the group)")
        else:
            self.round.accused = 1
        if self.doctor.alive:
            await self.doctor.dm_channel.send("Who would you like to save? (Enter their display name as it appears in the group)")
        else:
            self.round.saved = 1
        if self.breadman.alive:
            await self.breadman.dm_channel.send("Who would you like to bestow bread upon? (Enter their display name as it appears in the group)")
        else:
            self.round.breaded = 1

    async def stage_1_messages(self, message):
        if message.author == self.killer.info and message.channel == self.killer.dm_channel and self.round.killed is None:
            chosen = None
            if message.content != self.killer.info.display_name:
                for player in self.players:
                    if player.info.display_name == message.content:
                        if player.alive:
                            if player.info.display_name == message.content:
                                chosen = player
                                await self.killer.dm_channel.send(f"You have killed **'{player.info.display_name}'**")
                                print("Mafia Done")
                        else:
                            await self.killer.dm_channel.send("They are already dead! Try again.")
                if chosen is not None:
                    self.round.killed = chosen
                else:
                    await self.killer.dm_channel.send(f"'{message.content}' is not a valid player, try again")
            else:
                await self.killer.dm_channel.send("No suicides! Try again")

        elif message.author == self.doctor.info and message.channel == self.doctor.dm_channel and self.round.saved is None and self.doctor.alive:
            chosen = None
            for player in self.players:
                if player.info.display_name == message.content:
                    if player.alive:
                        if player.info.display_name == message.content:
                            chosen = player
                            await self.doctor.dm_channel.send(f"You have saved **'{player.info.display_name}'**")
                            print("Doctor Done")
                    else:
                        await self.doctor.dm_channel.send("The dead are beyond saving... Try again.")
            if chosen is not None:
                self.round.saved = chosen
            else:
                await self.doctor.dm_channel.send(f"'{message.content}' is not a valid player, try again")

        elif message.author == self.sheriff.info and message.channel == self.sheriff.dm_channel and self.round.accused is None and self.sheriff.alive:
            chosen = None
            if message.content != self.sheriff.info.display_name:
                for player in self.players:
                    if player.info.display_name == message.content:
                        if player.alive:
                            if player.info.display_name == message.content:
                                chosen = player
                                await self.sheriff.dm_channel.send(f"You have accused **'{player.info.display_name}**'")
                                print("Sheriff Done")
                                if self.sheriff_correct(player.info.display_name):
                                    await self.sheriff.dm_channel.send("You are **CORRECT**!")
                                else:
                                    await self.sheriff.dm_channel.send("You are **INCORRECT**")
                        else:
                            await self.sheriff.dm_channel.send("Its clearly not a dead guy! Try again...")
                #and chosen != 1
                if chosen is not None:
                    self.round.accused = chosen
                else:
                    await self.sheriff.dm_channel.send(f"'{message.content}' is not a valid player, try again")
            else:
                await self.sheriff.dm_channel.send("I don't think it was you... Try again")

        elif message.author == self.breadman.info and message.channel == self.breadman.dm_channel and self.round.breaded is None and self.breadman.alive:
            chosen = None
            for player in self.players:
                if player.info.display_name == message.content:
                    if player.alive:
                        if player.info.display_name == message.content:
                            chosen = player
                            await self.breadman.dm_channel.send(f"You have gifted bread to **'{player.info.display_name}'**")
                            print("Bread Man Done")
                    else:
                        await self.killer.dm_channel.send("The dead have no use for bread... Try again.")
            if chosen is not None:
                self.round.breaded = chosen
            else:
                await self.breadman.dm_channel.send(f"'{message.content}' is not a valid player, try again")

        #  Checks if all have chosen
        if self.round.killed != None and self.round.breaded != None and self.round.accused != None and self.round.saved != None:
            self.stage = 2
            await self.stage_2_init_()



    #  STAGE 2 FUNCTIONs
    async def get_story(self):
        global got_story

        await shared_lists.mute_manage_mafia_players(False)
        got_story = False


        what_they_doing = ["sat in the garden", "picking ripe apples from a large tree", "cooking a fresh lasagne",
                           "bullying small children", "sunbathing on the beach", "laying in bed",
                           "grinding on RuneScape", "coding another shitty discord bot",
                           "listening to their favorite tunes", "just waking up form a deep slumber",
                           "snorting crack", "cutting his toenails on his bed", "looking at furry porn",
                           "eating marmite on toast", "playing JackBox with their friends", "sat on a porta-loo"]
        where_maf_came = ["snuck up from behind", "dug a hole up through the floor", "was waiting in a nearby tree",
                          "air dropped down", "ran towards them"]
        what_maf_did = ["smacked them", "destroyed them", "crushed them", "chopped them up"]
        what_with = ["blunt object", "machete", "bomb", "large dildo", "shovel", "hammer",
                     "refreshing glass of cool aid", "rather sharp pencil"]
        surgical_procedure = ["colonoscopy", "breast biopsy", "cholecystectomy", "skin graft", "mastectomy",
                              "partial colectomy"]
        bread_did = ["bestowed the gift of bread upon", "bread slapped", "gave a whole baguette to", "threw a crusty white bloomer at",
                     "made a bread sandwich for", "threw a bag of strong white bread flour"]
        doctor_doing = ["'self medicating'", "on a five day meth binge", "popping their own pimples",
                        "cutting their toenails", "extracting a lightbulb from their anus"]


        one = what_they_doing[random.randint(0, len(what_they_doing) - 1)]
        two = where_maf_came[random.randint(0, len(where_maf_came) - 1)]
        three = what_maf_did[random.randint(0, len(what_maf_did) - 1)]
        four = what_with[random.randint(0, len(what_with) - 1)]
        five = surgical_procedure[random.randint(0, len(surgical_procedure) - 1)]
        six = doctor_doing[random.randint(0, len(doctor_doing) - 1)]
        seven = bread_did[random.randint(0, len(bread_did) - 1)]

        story = f"{self.round.killed.info.mention} was {one}, when the mafia {two} and {three} with a {four}!"
        story_speech = f"{self.round.killed.info.display_name} was {one}, when the mafia {two} and {three} with a {four}!"

        #  If doctor saves victim
        if self.round.killed == self.round.saved:
            story += f" Luckily for them, the doctor was in the area. He rushed over, performed a quick {five}, and saved the life of {self.round.killed.info.mention}!"
            story_speech += f" Luckily for them, the doctor was in the area. He rushed over, performed a quick {five}, and saved the life of {self.round.killed.info.display_name}!"
        #  Kills chosen player
        else:
            for i in range(len(self.players)):
                if self.players[i].info == self.round.killed.info:
                    self.players[i].alive = False
                    try:
                        await self.players[i].info.edit(mute=True)
                    except:
                        pass
                    self.dead_id.append(self.players[i].info.id)
                    await shared_lists.change_music(2)
                    try:
                        await self.players[i].dm_channel.send("**You have died!**")
                        await self.channel.send(f"Oh no! the **{self.players[i].role}** has been killed!")
                    except:
                        pass

        #  If doctor saves himself
        if self.doctor.alive:
            if self.round.saved.role == "doctor" and self.round.killed.role != "doctor":
                story += f" The doctor could have saved them, but they were {six} at the time."
                story_speech += f" The doctor could have saved them, but they were {six} at the time."

        #  Bread man
        if self.breadman.alive:
            story += f" In other news, the bread man {seven} {self.round.breaded.info.mention}!"
            story_speech += f" In other news, the bread man {seven} {self.round.breaded.info.display_name}!"

        Mafia.story_to_speech(story_speech)

        return story

    @staticmethod
    def get_id_from_mention(mention):
        player_id = mention.replace("<", "")
        player_id = player_id.replace(">", "")
        player_id = player_id.replace("!", "")
        player_id = player_id.replace("&", "")
        return int(player_id.replace("@", ""))

    def get_person(self, mention):
        player_id = Mafia.get_id_from_mention(mention)

        for person in self.players:
            if person.info.id == player_id:
                if person.alive:
                    if person.info.id == player_id:
                        return person
                else:
                    return "dead"
        return None

    def get_people_alive(self):
        alive = 0
        for person in self.players:
            if person.alive:
                alive += 1
        return alive

    def get_to_die(self):
        counter = 0
        prisoner = None

        for vote in self.round.votes:
            current_freq = self.round.votes.count(vote)
            if current_freq > counter:
                counter = current_freq
                prisoner = vote

        return [prisoner, counter]

    #  Tells story and Population report
    async def stage_2_init_(self):
        story = await self.get_story()
        self.update_players()
        while not got_story:
            pass
        await self.channel.send(story)
        await shared_lists.change_music(100)
        await asyncio.sleep(shared_lists.story_length + 1)
        await self.channel.send(embed=self.embed_player_status())
        if self.get_people_alive() > 2:
            await shared_lists.change_music(3)
            await self.channel.send("Discuss who you think is responsible! Cast your vote with a **mention**.")
        else:
            await self.channel.send("The townsfolk no long outnumber the mafia! The mafia wins!")
            await self.channel.send(f"{self.killer.info.mention} was the mafia!")
            await shared_lists.change_music(5)
            await Mafia.game_over()

    #  Vote for mafia
    async def stage_2_messages(self, message):
        if message.channel == self.channel and message.author.id not in self.round.voted and message.author.id not in self.dead_id:
            if message.author.id != Mafia.get_id_from_mention(message.content):
                person = self.get_person(message.content)
                if person != "dead":
                    if person is not None:
                        self.round.votes.append(person)
                        self.round.voted.append(message.author.id)
                        await self.channel.send(f"Vote for {person.info.mention}")
                        if len(self.round.votes) == self.get_people_alive():
                            self.round.to_die = self.get_to_die()
                            await shared_lists.change_music(2)
                            await self.kill_prisoner()
                    else:
                        await self.channel.send("This person is not playing, try again.")
                else:
                    await self.channel.send("You can't vote for the dead, try again.")
            else:
                await self.channel.send("You cannot vote for yourself! Try again.")

    async def kill_prisoner(self):

        await self.channel.send(
            f"The towns people have spoken! You have voted for **{self.round.to_die[0].info.mention}** with **{self.round.to_die[1]} vote/s** ")

        for x in range(len(self.players)):
            if self.players[x] == self.round.to_die[0]:
                self.players[x].alive = False
                try:
                    await self.players[x].info.edit(mute=True)
                except:
                    pass
                self.dead_id.append(self.players[x].info.id)
                self.update_players()
                try:
                    await self.players[x].dm_channel.send("**You have been executed!**")
                    if self.players[x].role == "killer":
                        await self.channel.send(f"Congratulations! **{self.players[x].info.mention}** was the mafia!")
                        await shared_lists.change_music(4)
                        await Mafia.game_over()
                    else:
                        await self.channel.send(f"Oh no! the **{self.players[x].role}** has been executed!")
                        await self.channel.send(embed=self.embed_player_status())
                        if self.get_people_alive() > 2:
                            await asyncio.sleep(5)
                            await self.channel.send("Players! Make your choices now!")
                            self.stage = 1
                            await shared_lists.mute_manage_mafia_players(True)
                            self.round = Round(None, None, None, None)
                            await shared_lists.change_music(1)
                            await self.stage_1_init_()
                        else:
                            await self.channel.send("The townsfolk no long outnumber the mafia! The mafia wins!")
                            await self.channel.send(f"{self.killer.info.mention} was the mafia!")
                            await shared_lists.change_music(5)
                            await Mafia.game_over()
                except:
                    await self.channel("Oh no! You have executed a civilian!")
                    await self.channel.send(embed=self.embed_player_status())
                    if self.get_people_alive() > 2:
                        await asyncio.sleep(5)
                        await self.channel.send("Players! Make your choices now!")
                        self.stage = 1
                        await shared_lists.mute_manage_mafia_players(True)
                        self.round = Round(None, None, None, None)
                        await shared_lists.change_music(1)
                        await self.stage_1_init_()
                    else:
                        await self.channel.send("The townsfolk no long outnumber the mafia! The mafia wins!")
                        await self.channel.send(f"{self.killer.info.mention} was the mafia!")
                        await shared_lists.change_music(5)
                        await Mafia.game_over()



    #  Resets game variables
    @staticmethod
    async def game_over():
        for person in shared_lists.mafia_game[0].players:
            try:
                await person.info.edit(mute=False)
            except:
                pass
        shared_lists.mafia_game.clear()
        shared_lists.mafia_vc = None
        shared_lists.story_length = 0
        shared_lists.story = None
        shared_lists.mafia_players.clear()

