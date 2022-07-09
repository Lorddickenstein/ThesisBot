import discord
from dadjokes import Dadjoke
from jokeapi import Jokes
from mypackage.config import BOT_TOKEN, COMMANDS, SORRY_WORDS, CATEGORIES, BLACKLISTED

class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        msg = message.content.lower()

        if message.author == self.user:
            return

        if msg.endswith('? more like') or  msg.endswith('more like'):
            response = 'Bore Ragnarok'
            await message.channel.send(response)

        if any(words in msg for words in SORRY_WORDS):
            response = 'Stop apologizing so much!!! It\'s CRINGE!!!'
            await message.channel.send(response)

        if msg == '!list':
            response = '```[Available commands]\n\n'
            for command in COMMANDS:
                response += '\t' + command.get('command') + ' - ' + command.get('response') + '\n'
            response += '```'
            await message.channel.send(response)

        if msg == '!dad-jokes':
            dadjoke = Dadjoke()
            response = dadjoke.joke
            await message.channel.send('*' + response + '*')

        if msg.startswith('!jokes'):
            j = await Jokes()
            params = msg.split('-')

            if len(params) > 1:
                if params[1] in BLACKLISTED:
                    while True:
                        flag = False
                        jokes = await j.get_joke(amount=10)
                        for jk in jokes['jokes']:
                            if jk['flags'][params[1]]:
                                joke = jk
                                flag = True
                                break

                        if flag:
                            break
                elif params[1] in CATEGORIES:
                    joke = await j.get_joke(category=[params[1]])
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