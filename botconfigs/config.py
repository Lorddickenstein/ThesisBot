import sys
from pathlib import Path

# set up base directory relative to main.py
BASE_DIR = Path(__file__).resolve().parent.parent

COMMANDS = [
        {'command': 'commands', 'response': 'Lists all commands'},
        {'command': 'dadjokes', 'response': 'Generate a random dad joke'},
        {'command': 'freegames now', 'response': 'Get the current free games from the Epic Games Store'},
        {'command': 'freegames later', 'response': 'Get next week\'s free games from the Epic Games Store'},
        {'command': 'jokes or !jokes any', 'response': 'Generate any random joke'},
        {'command': 'jokes christmas', 'response': 'Generate a random christmas joke'},
        {'command': 'jokes dark', 'response': 'Generate a random dark joke'},
        {'command': 'jokes explicit', 'response': 'Generate a random explicit joke'},
        {'command': 'jokes misc', 'response': 'Generate a random miscellaneous joke'},
        {'command': 'jokes nsfw', 'response': 'Generate a random nsfw joke'},
        {'command': 'jokes political', 'response': 'Generate a random political joke'},
        {'command': 'jokes programming', 'response': 'Generate a random programming joke'},
        {'command': 'jokes pun', 'response': 'Generate a random pun'},
        {'command': 'jokes racist', 'response': 'Generate a random racist joke'},
        {'command': 'jokes religious', 'response': 'Generate a random religious joke'},
        {'command': 'jokes sexist', 'response': 'Generate a random sexist joke'},
        {'command': 'jokes spooky', 'response': 'Generate a random spooky joke'},
        {'command': 'leaderboards', 'response': 'Display top mentions of watchlisted words'},
        {'command': 'leaderboards <monitored_words>', 'response': 'Display top mentions of a specific watchlisted word'},
        {'command': 'monitored words', 'response': 'List all monitored words'},
        {'command': 'sorry', 'response': 'I hate this command. Please never use it.'},
        {'command': 'stats', 'response': 'Display bot statistics'},
        ]

OTHER_COMMANDS = [
        {'command': 'more like', 'response': 'more like Bore Ragnarok!'},
        {'command': '<literally anything>? more like', 'response': 'more like Bore Ragnarok!'},
        ]

SORRY_WORDS = ['sorry', 'sorre', 'sorreh', 'sorrey', 'sori', '!sorry']

BLACKLISTED = ['nsfw', 'religious', 'political', 'racist', 'sexist', 'explicit']

CATEGORIES = ['any', 'misc', 'programming', 'dark', 'pun', 'spooky', 'christmas']

STATS = {
        'Bot Version': '0.2 beta',
        'Python version': '.'.join(map(str, sys.version_info[:3])),
        'Discord.py Version': '1.7.3',
        'Total Users': '*Not yet coded*',
        'Total Guilds': '*Not yet coded*',
        'Bot Created': 'July 8, 2022',
        'Bot Developers': [
                {'name': 'Jerson', 'discordId':'756084838154633237'},
                {'name': 'King', 'discordId': '645255797340766218'},
                {'name': 'Ramil', 'discordId': '460745694794481666'},
        ],
}

# Database
DB_FILE = str(BASE_DIR / 'botconfigs' / 'discord_db.db')

BOT_RESTRICTIONS = {
        'allowed-channels': ['bot-commands'],
}

if __name__ == '__main__':
        print('Directories: ')
        print('database:', DB_FILE)
        print('root application:', BASE_DIR)
