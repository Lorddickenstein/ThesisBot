import discord
from mypackage.config import BOT_TOKEN

class MyClient(discord.Client):

    sorry_words = ['sorry', 'sorre', 'sorreh', 'sorrey', 'sori']
    commands = [
        {'command': '#list', 'response': 'lists all commands'},
        {'command': '#more like', 'response': 'more like Bore Ragnarok!'},
        {'command': 'more like', 'response': 'more like Bore Ragnarok!'},
        {'command': '<literally anything>? more like', 'response': 'more like Bore Ragnarok!'},
        {'command': 'sorry', 'response': 'THIS IS FORBIDDEN!!!'}
    ]

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        msg = message.content.lower()

        if message.author == self.user:
            return

        if msg.endswith('? more like') or  msg.endswith('more like'):
            await message.channel.send('Bore Ragnarok!')

        if any(words in msg for words in self.sorry_words):
            await message.channel.send('Stop apologizing so much!!! It\'s CRINGE!!!')

        if msg == '#list':
            cmd = '```[Available commands]\n\n'
            for command in self.commands:
                cmd += '\t' + command.get('command') + ' - ' + command.get('response') +'\n'
            await message.channel.send(cmd + '```')


client = MyClient()
client.run(BOT_TOKEN)