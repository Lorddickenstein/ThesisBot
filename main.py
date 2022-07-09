import discord
from mypackage.config import BOT_TOKEN

class MyClient(discord.Client):

    sorry_words = ['sorry', 'sorre', 'sorreh', 'sorrey', 'sori']
    commands = [
        {'command': '!list', 'response': 'lists all commands'},
        {'command': 'sorry', 'response': 'NEVER USE THIS COMMAND. THIS IS FORBIDDEN!!!'},
        {'command': 'more like', 'response': 'more like Bore Ragnarok!'},
        {'command': '*literally anything*? more like', 'response': 'more like Bore Ragnarok!'},
    ]

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

        if any(words in msg for words in self.sorry_words):
            response = 'Stop apologizing so much!!! It\'s CRINGE!!!'
            await message.channel.send(response)

        if msg == '!list':
            response = '```[Available commands]\n\n'
            for command in self.commands:
                print(command.get('command'))
                response += '\t' + command.get('command') + ' - *' + command.get('response') + '*' +'\n'
            response += '```'
            print(response)
            await message.channel.send(response)

        if msg == '!test':
            response = 'This text has some words *emphasized* in _different_ ways'
            await message.channel.send(response)


client = MyClient()
client.run(BOT_TOKEN)