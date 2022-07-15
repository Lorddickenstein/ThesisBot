import discord
from dadjokes import Dadjoke
from jokeapi import Jokes
from mypackage.config import BOT_TOKEN, COMMANDS, SORRY_WORDS, CATEGORIES, BLACKLISTED

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

        # more like Bore Ragnarok!
        if msg.endswith('? more like') or  msg.endswith('more like'):
            response = 'Bore Ragnarok'
            await message.channel.send(response)

        # please don't apologize
        if any(words in msg for words in SORRY_WORDS):
            response = 'Stop apologizing so much!!! It\'s CRINGE!!!'
            await message.channel.send(response)

        # !list
        if msg == '!list':
            embed = discord.Embed(
                title='Commands Lists',
                description='These are some helpful commands.',
                color=0xf1c40f
            )

            for command in COMMANDS:
                embed.add_field(
                    name=command.get('command'),
                    value=command.get('response'),
                    inline=false
                )
            
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


client = MyClient()
client.run(BOT_TOKEN)