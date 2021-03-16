import sqlite3
import time
import re
import zlib
from datetime import datetime, timedelta

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS Directors ''')
cur.execute('''DROP TABLE IF EXISTS Movies1 ''')
cur.execute('''DROP TABLE IF EXISTS Years ''')
cur.execute('''DROP TABLE IF EXISTS Genres ''')
cur.execute('''DROP TABLE IF EXISTS Countries ''')
cur.execute('''DROP TABLE IF EXISTS Cast ''')
cur.execute('''DROP TABLE IF EXISTS MovGen ''')
cur.execute('''DROP TABLE IF EXISTS MovCoun ''')
cur.execute('''DROP TABLE IF EXISTS MovCast ''')


cur.execute('''CREATE TABLE IF NOT EXISTS Directors
	(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Movies1
	(id INTEGER PRIMARY KEY, org_title TEXT NOT NULL, pl_title TEXT NOT NULL, year_id INTEGER, 
	length INTEGER, director_id INTEGER, story BLOB, rating INTEGER, 
	votes INTEGER)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Years
	(id INTEGER PRIMARY KEY, year INTEGER UNIQUE NOT NULL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Genres
	(id INTEGER PRIMARY KEY, genre TEXT UNIQUE NOT NULL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Countries
	(id INTEGER PRIMARY KEY, country TEXT UNIQUE NOT NULL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Cast
	(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS MovGen
	(movie_id INTEGER, genre_id INTEGER, PRIMARY KEY (movie_id, genre_id))''')
cur.execute('''CREATE TABLE IF NOT EXISTS MovCoun
	(movie_id INTEGER, country_id INTEGER, PRIMARY KEY (movie_id, country_id))''')
cur.execute('''CREATE TABLE IF NOT EXISTS MovCast
	(movie_id INTEGER, name_id INTEGER, PRIMARY KEY (movie_id, name_id))''')


# Open the main content (Read only)
conn_1 = sqlite3.connect('file:movies.sqlite?mode=ro', uri=True)
cur_1 = conn_1.cursor()

allmovies = list()
cur_1.execute('SELECT org_title FROM Movies')
for movie_raw in cur_1 :
	allmovies.append(movie_raw[0])

print('Loaded allmovies', len(allmovies))



cur_1.execute('''SELECT org_title, title, year, length, genre, director, country, people, short_info, rating, rates_number FROM Movies''')

mvs = dict()
yrs = dict()
genres = dict()
directors = dict()
countries = dict()
casts = dict()

count = 0

for movie_row in cur_1:
	movie = movie_row[0]
	pltitle = movie_row[1]
	yr = movie_row[2]
	lngth = movie_row[3]
	genrel = movie_row[4]
	drctr = movie_row[5]
	countryl = movie_row[6]
	cst = movie_row[7]
	info = movie_row[8]
	rtng = movie_row[9]
	votes = movie_row[10]
	allmovies.append(movie)

	count = count + 1
	if count % 100 == 1 :
		print(count, movie, drctr )

	year_id = yrs.get(yr, None)

	director_id = directors.get(drctr, None)


	if year_id is None :
		cur.execute('INSERT OR IGNORE INTO Years (year) VALUES (?)', (yr, ) )
		conn.commit()
		cur.execute('SELECT id FROM Years WHERE year=? LIMIT 1', (yr, ) )
		try:
			row = cur.fetchone()
			year_id = row[0]
			yrs[yr] = year_id
		except:
			print('Could not retrive year id', yr)


	if director_id is None :
		cur.execute('INSERT OR IGNORE INTO Directors (name) VALUES (?)', (drctr, ) )
		conn.commit()
		cur.execute('SELECT id FROM Directors WHERE name=? LIMIT 1', (drctr, ) )
		try:
			row = cur.fetchone()
			director_id = row[0]
			directors[drctr] = director_id
		except:
			print('Could not retrive director id', drctr)


	#if movie_id is None :
	cur.execute('INSERT INTO Movies1 (org_title, pl_title,year_id, length, director_id, story, rating, votes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
		(movie, pltitle,year_id, lngth, director_id, zlib.compress(info.encode()), rtng, votes ) )
	conn.commit()
	cur.execute('SELECT id FROM Movies1 WHERE org_title=? LIMIT 1', (movie, ) )
	try:
		row = cur.fetchone()
		movie_id = row[0]
		#mvs[movie] = movie_id
	except:
		print('Could not retrive movie id', movie)
	try:
		genrez = genrel.strip("[]").split(",")
	
		for gnr in genrez:
			gnr = gnr.strip().strip("''")
			genre_id = genres.get(gnr, None)

			if genre_id is None :
				cur.execute('INSERT OR IGNORE INTO Genres (genre) VALUES (?)',
					(gnr, ) )
				conn.commit()
				cur.execute('SELECT id FROM Genres WHERE genre=? LIMIT 1', (gnr, ) )
				try:
					row = cur.fetchone()
					genre_id = row[0]
					genres[gnr] = genre_id
				except:
					print('Could not retrive genre id', gnr)

			cur.execute('INSERT OR REPLACE INTO MovGen (movie_id, genre_id) VALUES (?, ?)', (movie_id, genre_id) )
	except:
		print('No genres', gnr)

	try:
		countriez = countryl.strip("[]").split(",")
	
		for cnt in countriez:
			cnt = cnt.strip().strip("''")
			country_id = countries.get(cnt, None)
			if country_id is None :
				cur.execute('INSERT OR IGNORE INTO Countries (country) VALUES (?)',
					(cnt.strip(), ) )
				conn.commit()
				cur.execute('SELECT id FROM Countries WHERE country=? LIMIT 1', (cnt.strip(), ) )
				try:
					row = cur.fetchone()
					country_id = row[0]
					countries[cnt] = country_id
				except:
					print('Could not retrive country id', countryl)

			cur.execute('INSERT OR REPLACE INTO MovCoun (movie_id, country_id) VALUES (?, ?)', (movie_id, country_id) )
	except:
		print('No countries', countryl)

	try:
		castz = cst.strip("[]").split(",")
	
		for person in castz:
			person = person.strip().strip("''")
			name_id = countries.get(person, None)
			if name_id is None :
				cur.execute('INSERT OR IGNORE INTO Cast (name) VALUES (?)',
					(person.strip(), ) )
				conn.commit()
				cur.execute('SELECT id FROM Cast WHERE name=? LIMIT 1', (person.strip(), ) )
				try:
					row = cur.fetchone()
					name_id = row[0]
					casts[person] = name_id
				except:
					print('Could not retrive name id', cst)

			cur.execute('INSERT OR REPLACE INTO MovCast (movie_id, name_id) VALUES (?, ?)', (movie_id, name_id) )
	except:
		print('No cast', cst)
cur.close()
cur_1.close()