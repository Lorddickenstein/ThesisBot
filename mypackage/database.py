import sqlite3
from sqlite3 import Error

class Database:

	def __init__(self, db_name):
		self.db_name = db_name
		self.conn = self.create_connection()
		self.conn.row_factory = sqlite3.Row
		self.cur = self.conn.cursor()

		query = '''CREATE TABLE word_counter (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			author varchar(120) NOT NULL,
			word varchar(50),
			datetime_created datetime)'''
		self.create_table(query)


	def create_connection(self):
		""" create a database connection to a SQLite Database """

		conn = None
		try:
			print(f'   Connecting to {self.db_name} database v.{sqlite3.version}...')
			conn = sqlite3.connect(self.db_name)
			print('   Connection established.')
		except Error as err:
			print(err)
			return

		return conn


	def create_table(self, query):
		""" create a table in the database connection """

		try:
			print('   Creating Table...')
			self.conn.execute(query)
		except Error as err:
			print('   Table is already created.')


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

		print(f'   Inserting record to {table_name}...')
		self.cur.execute(query)
		self.conn.commit()
		print('   Inserting record successful.')


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

		# print(query)
		rows = self.cur.execute(query).fetchall()
		if len(rows) == 1:
			key = rows[0].keys()[0]
			return rows[0][key]
		else:
			return rows


	def close(self):
		""" close the connection """

		if self.conn:
			self.conn.close()
			return 1

		return -1
