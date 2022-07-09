import discord
from mypackage.config import BOT_TOKEN, COMMANDS, SORRY_WORDS

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

        if any(words in msg for words in self.SORRY_WORDS):
            response = 'Stop apologizing so much!!! It\'s CRINGE!!!'
            await message.channel.send(response)

        if msg == '!list':
            response = '```[Available commands]\n\n'
            for command in self.COMMANDS:
                response += '\t' + command.get('command') + ' - ' + command.get('response') + '\n'
            response += '```'
            await message.channel.send(response)


client = MyClient()
client.run(BOT_TOKEN)