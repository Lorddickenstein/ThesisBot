import discord
from dadjokes import Dadjoke
from jokeapi import Jokes
from datetime import datetime
from mypackage.database import Database
from mypackage.config import *

class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        def find_specific_joke(jokes, category):
            for joke in jokes['jokes']:
                if joke['flags'][category]:
                    return joke
            return

        msg = message.content.lower()

        if message.author == self.user:
            return

        # !list
        if msg == '!list':
            embed = discord.Embed(
                title='Commands Lists',
                description='''Hello, I\'m the product of your horrible thesis. Please refer to the commands below on how to use me.\n\u1CBC\u1CBC''',
                color=0xf1c40f)

            for command in COMMANDS:
                embed.add_field(
                    name=command.get('command'),
                    value=command.get('response'),)

            embed.set_footer(text='Bot created on July 8, 2022.')
            await message.channel.send(content=None, embed=embed)

        # !dad-jokes
        if msg == '!dad-jokes':
            dadjoke = Dadjoke()
            response = dadjoke.joke
            await message.channel.send('*' + response + '*')

        # !jokes
        if msg.startswith('!jokes'):
            j = await Jokes()
            params = msg.split('-')

            # !jokes with categories
            if len(params) > 1:
                _, category = params
                if category in BLACKLISTED:
                    while True:
                        jokes = await j.get_joke(amount=10)
                        joke = find_specific_joke(jokes, category)
                        if joke:
                            break
                        
                elif category in CATEGORIES:
                    joke = await j.get_joke(category=[category])

            # !jokes with no categories
            else:
                joke = await j.get_joke()

            if joke['type'] == 'single':
                response = joke['joke']
                await message.channel.send(response)
            else:
                response_setup = joke['setup']
                await message.channel.send('*' + response_setup + '*')
                response_delivery = joke['delivery']
                await message.channel.send('*||' + response_delivery + '||*')

        # !leaderboards
        if msg.startswith('!leaderboards'):
            db = Database(DB_FILE)
            embed = discord.Embed(
                title='Leaderboards',
                color=0x3498DB)

            params = msg.split('-')
            if len(params) > 1:
                _, word = params
                leaderboards = db.get_leaderboards(word=word)
            else:
                leaderboards = db.get_leaderboards()

            for word, results in leaderboards.items():
                value = ''
                for result in results:
                    member = await message.guild.fetch_member(int(result['author']))
                    value += f'{member.name}#{member.discriminator} : `{result["count"]}`\n'
                
                embed.add_field(
                    name=word.capitalize(),
                    value=value,
                    inline=True)


            embed.add_field(
                name='\u1CBC\u1CBC',
                value='Type `$leaderboards` to display all leaderboards.' if len(params) > 1 else 'Type `$leaderboards-[monitored_word]` to display word-specific leaderboard.',
                inline=False)
            db.close()
            await message.channel.send(content=None, embed=embed)

        # !monitored-words
        if msg == '!monitored-words':
            db = Database(DB_FILE)
            author_id = message.author.id
            embed = discord.Embed(
                title='List of Monitored Words',
                color=0x566573)

            for word in WORDS_COUNTED:
                total_mentions = db.count_mentions('word_counter',
                    word=word)
                embed.add_field(
                    name=word.capitalize(),
                    value=f'Total mentions: `{total_mentions}`',
                    inline=True)

            embed.add_field(
                name='\u1CBC\u1CBC',
                value='Type `!leaderboards` to display all leaderboards.',
                inline=False)
            db.close()
            await message.channel.send(content=None, embed=embed)

        # !stats
        if msg == '!stats':
            embed = discord.Embed(
                title='Thesis Bot Statistics',
                description='\u1CBC\u1CBC',
                url='https://discord.com/users/816934307780231178',
                color=0x5c64f4)
            embed.set_author(
                name='Thesis Bot',
                icon_url=client.user.avatar_url)

            for key, value in STATS.items():
                embed.add_field(
                    name=key,
                    value=value)

            await message.channel.send(content=None, embed=embed)

        # word counter
        if any(word in msg.split() for word in WORDS_COUNTED):
            db = Database(DB_FILE)
            author_id = message.author.id

            embed = discord.Embed(
                title='Word Counter (Global)',
                color=0x28b463)

            date_now = datetime.now()
            datetime_created = date_now.strftime('%Y-%m-%d %H:%M')

            words_list = []
            for word in msg.split():
                if word in WORDS_COUNTED:
                    db.insert_record('word_counter',
                        author=author_id,
                        word=word,
                        datetime_created=datetime_created)
                    words_list.append(word)
                    embed.add_field(
                        name=word.capitalize(),
                        value=f'Has been mentioned by <@{author_id}>',
                        inline=False)

            words_list = dict.fromkeys(words_list)
            for word, _ in words_list.items():
                total_mentions = db.count_mentions('word_counter',
                    author=author_id,
                    word=word)
                embed.add_field(
                    name=word.capitalize(),
                    value=f'Total mentions: `{total_mentions}`',
                    inline=False)

            embed.add_field(
                name='\u1CBC\u1CBC',
                value='Type `!leaderboards` to display leaderboards or `!monitored-words` to display a list of monitored words.',
                inline=False)
            db.close()
            await message.channel.send(content=None, embed=embed)

        # more like Bore Ragnarok!
        if msg.endswith('? more like') or  msg.endswith('more like'):
            response = 'Bore Ragnarok'
            await message.channel.send(response)

        # please don't apologize
        if any(words in msg for words in SORRY_WORDS):
            response = 'Stop apologizing so much!!! It\'s CRINGE!!!'
            await message.channel.send(response)


client = MyClient()
client.run(BOT_TOKEN)