import sqlite3
from botconfigs.utils import get_local_time_now, get_datetime
from sqlite3 import Error

class Database:

	def __init__(self, db_name):
		self.db_name = db_name


	def __enter__(self):
		print(f'    Connecting to {self.db_name} database v.{sqlite3.version}...')
		self.conn = sqlite3.connect(self.db_name, timeout=20)
		self.conn.row_factory = sqlite3.Row
		self.cur = self.conn.cursor()
		print('    Connection established.')
		return self


	def __exit__(self, type, value, tb):
		""" close the connection """

		if self.conn:
			self.conn.close()
			return



	def insert_record(self, table_name, **args):
		""" insert record into a specified table """

		query = f"""INSERT INTO {table_name} ("""

		for key, _ in args.items():
			query += key + ','

		query = query[:-1] + ') VALUES ('

		for _, value in args.items():
			if isinstance(value, str):
				query += '\'' + value + '\','
			else:
				query += str(value) + ','

		query = query[:-1] + ')'
		# print(query)
		
		try:
			self.cur.execute(query)
			self.conn.commit()
		except Error as err:
			self.conn.rollback()
			print('    Inserting unsuccessful.', err)


	def count_mentions(self, table_name, **args):
		""" count specific mentions of certain words """

		query = f'''SELECT count(*) as count FROM {table_name} WHERE '''

		for key, value in args.items():
			if isinstance(value, str):
				query += key + ' = \'' + str(value) + '\' AND '
			else:
				query += key + ' = ' + str(value) + ' AND '
		query = query[:-4] + 'GROUP BY ' 

		for key, _ in args.items():
			query += key + ','
		query = query[:-1]

		rows = self.cur.execute(query).fetchall()
		if len(rows) == 1:
			key = rows[0].keys()[0]
			return rows[0][key]
		else:
			return rows


	def get_all_words(self):
		""" return a list of all monitored words """

		query = f'SELECT DISTINCT word, guildId FROM monitored_words ORDER BY word, guildId'
		print('    Retrieving all monitored words...')
		rows = self.cur.execute(query).fetchall()

		words_dict = {}
		'''
			sample data:
				words_dict = {
					995472678225977384 : ['naol', 'nays', 'nice', 'noice', 'sad', 'sanaol']
					807284429524434965 : ['naol', 'nays', 'nice', 'noice', 'sad', 'sanaol']
				}
		'''
		# put all words in a dictionary with guildId as key
		# https://www.geeksforgeeks.org/python-convert-a-list-of-tuples-into-dictionary/
		for guild_id, word in [(row['guildId'], row['word']) for row in rows]:
			words_dict.setdefault(guild_id, []).append(word)
		return words_dict


	def get_leaderboards(self, guild_id, word=None, limit=5):
		""" display the leaderboards """
	
		def get_rows(word, limit):
			""" return results from query as rows """
			query = f''' SELECT count(*) as count, author, word
					FROM word_counter
					WHERE word = '{word}' AND guildId = {guild_id}
					GROUP BY author, word
					ORDER BY word, count DESC
					LIMIT {limit}'''
			rows = self.cur.execute(query).fetchall()
			return rows

		leaderboards = {}
		'''
		sample data:
		
			leaderboards = {
				'sanaol': [
					{'count': 15, 'author': '756084838154633237'},
					{'count': 12, 'author': '756084838154633238'},
					{'count': 1, 'author': '756084838154633239'},
					],
				'naol': [
					{'count': 14, 'author': '756084838154633237'},
					{'count': 22, 'author': '756084838154633238'},
					{'count': 10, 'author': '756084838154633239'},
					],
			}
		'''

		if word:
			print(f'    Retrieving {word} leaderboards...')
			rows = get_rows(word, limit)
			leaderboards[word] = [{'count': row[0], 'author': row[1]} for row in rows]
		else:
			print('    Retrieving leaderboards...')
			words_list = self.get_all_words()

			for word in words_list[guild_id]:
				rows = get_rows(word, limit)
				leaderboards[word] = [{'count': row[0], 'author': row[1]} for row in rows]
			print('    Learderboards loaded successfully...')
				
		return leaderboards


	def get_games(self):
		""" return a list of all current and upcoming free games from the database """

		query = ''' SELECT * FROM free_games WHERE status = 'active' or status = 'upcoming' GROUP BY status, startDate ORDER BY startDate'''
		rows = self.cur.execute(query).fetchall()

		free_games = {'active': [], 'upcoming': []}
		'''
			sample data:
				free_games = {
					'active': [{
						'title': 'title',
						'gameId': '7d849437da4547399baa3758cb7ec580',
						'description': 'some long texts',
						'icon': 'url of image icon',
						'startDate': '2022-07-28',
						'endDate': '2022-08-04 15:00:00',
						'url': 'url of game',
						'status': 'active',
						}],
					'upcoming': [{
						'title': 'title',
						'gameId': '7d849437da4547399baa3758cb7ec580',
						'description': 'some long texts',
						'icon': 'url of image icon',
						'startDate': '2022-07-28',
						'endDate': '2022-08-04 15:00:00',
						'url': 'url of game',
						'status': 'upcoming',
					}]
				}
		'''
		# append to the list of games
		for row in rows:
			if row['status'] == 'active':
				free_games['active'].append({
					'title': row['title'],
					'gameId': row['gameId'],
					'description': row['description'],
					'startDate': get_datetime(row['startDate'], '%Y-%m-%d %H:%M:%S'),
					'endDate': get_datetime(row['endDate'], '%Y-%m-%d %H:%M:%S'),
					'url': row['url'],
					'icon': row['icon'],
					'status': row['status'],
				})
			elif row['status'] == 'upcoming':
				free_games['upcoming'].append({
					'title': row['title'],
					'gameId': row['gameId'],
					'description': row['description'],
					'startDate': get_datetime(row['startDate'], '%Y-%m-%d %H:%M:%S'),
					'endDate': get_datetime(row['endDate'], '%Y-%m-%d %H:%M:%S'),
					'url': row['url'],
					'icon': row['icon'],
					'status': row['status'],
				})

		return free_games

	
	def update_game_status(self):
		""" update the status of the games in the database """

		now = get_local_time_now()
		games = self.get_games()

		for _, games_dict in games.items():
			for game in games_dict:
				# convert to datetime objects to allow operations
				end_date = game['endDate']
				start_date = game['endDate']

				status = ''

				# check and update status
				if game['status'] == 'active' and end_date < now:
					status = 'expired'

				if game['status'] == 'upcoming' and start_date < now:
					status = 'active'

				if status:	
					try:
						self.cur.execute(f'''UPDATE free_games
							SET status = '{status}'
							WHERE gameId = '{game["gameId"]}'
							''')
						self.conn.commit()
					except Error as err:
						self.conn.rollback()
						print('    Update unsuccessful.', err)

		print('    Games status updated successfully...')
