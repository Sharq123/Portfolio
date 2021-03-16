import sqlite3
import urllib.error
import ssl
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('movies.sqlite')
cur = conn.cursor()

print('This app allows to save to a database all movies from filmweb.pl that have at least one vote')

cur.execute('''CREATE TABLE IF NOT EXISTS Movies
(id INTEGER UNIQUE,
org_title TEXT,
title TEXT,
year INTEGER,
length INTEGER,
genre TEXT,
director TEXT,
country TEXT,
cast TEXT,
short_info TEXT,
rating REAL,
rates_number INTEGER )''')

# Pick up where we left off
page = None
cur.execute('SELECT * FROM Movies')

row = cur.fetchone()
if row is None :
    startyear = 1888
    page = 1
else :
	row = cur.execute('SELECT MAX(year) FROM Movies').fetchone()
	startyear = row[0]
	row = cur.execute('SELECT COUNT(year) FROM Movies WHERE year=?', (startyear, )).fetchone()
	YearCount = row[0]
	page = int(YearCount/10) + 1

error = 0
many = 0

while True :

    # get the number of movies to save, escape when it's done
    if ( many < 1 ):
	    conn.commit()
	    sval = input('How many movies?')
	    if (len(sval) < 1 ) : break
	    try:
	        many = int(sval)
	    except:
	    	print("insert number")
	    	continue
    url = 'https://www.filmweb.pl/films/search?endRate=10&endYear=2024&orderBy=year&descending=false&startCount=1&startRate=-1&startYear={}&page={}'.format(startyear, page)


    try:
	    document = urlopen(url, context=ctx)
	    html = document.read()
	    if document.getcode() != 200 :
		    print("Error on page: ",document.getcode())

	    if 'text/html' != document.info().get_content_type() :
		    print("Ignore non text/html page")
		    continue

	    print('('+str(len(html))+')', end=' ')

	    soup = BeautifulSoup(html, "html.parser")
    except KeyboardInterrupt:
    	print('')
    	print('Program interrupted by user...')
    	break
    except:
    	print("Unable to retrieve or parse page")
    	error = error + 1
    	if error > 5 :
    		break
    	continue

    movielist = soup.find_all('li', class_='hits__item')

    # find a number to be movie's id
    cur.execute('SELECT max(id) FROM Movies' )
    try:
	    row = cur.fetchone()
	    maxid = row[0]
	    if maxid is None:
		    number = 0
	    else:
		    number = maxid - (YearCount % 10)
    except:
	    number = 0


	

    for movie in movielist :

	    if ( many < 1 )  : break
	    many = many - 1
	    print(many)
		
	    number = number + 1
	    cur.execute('SELECT id FROM Movies WHERE id=?', (number, ))
		
	    try:
		    row = cur.fetchone()
		    if row is not None : 
			    many = int(sval)
			    continue
	    except:
		    row = None

	    try:
		    votes = int(movie.find('span', class_='rateBox__votes rateBox__votes--count')['content'])
	    except:
		    votes = None


	    try:
		    title = movie.find('h2').contents[0]
	    except:
		    title = None

	    try:
		    org = movie.find('div', class_='filmPreview__originalTitle').contents[0]
	    except:
		    org = title

	    try:
		    year = int(movie.find('div', class_='filmPreview__year').contents[0])
	    except:
		    year = None
		
	    try:
		    length = int(movie.find('div', class_='filmPreview__filmTime')['data-duration'])
	    except:
		    length = None
	    try:	
		    rating = movie.find('span', class_='rateBox__rate').contents[0]
		    rating = rating.replace(",",".")
		    rating = float(rating)
	    except:
		    rating = None	
	    try:
		    description = str(movie.find('p').contents[0])
		    if len(description)<1:
			    description = ""
	    except:
		    description = ""

	    try:
		    genrediv = movie.find('div', class_='filmPreview__info filmPreview__info--genres')
		    genrelist = genrediv.find_all('a')
		    glist = list()
		    for item in genrelist :
			    glist.append(item.contents[0])
		    genre = str(glist)
	    except:
		    genre = None

	    try:
		    countriesdiv = movie.find('div', class_='filmPreview__info filmPreview__info--countries')
		    countrieslist = countriesdiv.find_all('a')
		    clist = list()
		    for item in countrieslist :
			    clist.append(item.contents[0])
		    countries = str(clist)
	    except:
		    countries = None

	    try:
		    directorsdiv = movie.find('div', class_='filmPreview__info filmPreview__info--directors')
		    director = directorsdiv.find('a')['title']
	    except:
		    director = None

	    castdiv = movie.find('div', class_='filmPreview__info filmPreview__info--cast')
	    try:
		    castlist = castdiv.find_all('a')
		    calist = list()
		    for item in castlist :
			    calist.append(item.contents[0])
		    cast = str(calist)
	    except:
		    cast = None

	    cur.execute('''INSERT OR IGNORE INTO Movies (id,org_title, title, year, length, genre, director, country, cast, short_info, rating, rates_number)
		    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''', (number,org, title, year, length, genre, director, countries, cast, description, rating, votes))

	    conn.commit()

	    print(title, year, director, votes)

    conn.commit()
    YearCount = 10
    if (many < 1) :
        break
    page = page + 1
    # switch year when we get to page nr 1000
    if page > 1000 :
	    startyear = year
	    row = cur.execute('SELECT COUNT(year) FROM Movies WHERE year=?', (startyear, )).fetchone()
	    YearCount = row[0]
	    page = int(YearCount/10) + 1
	    sval = many

