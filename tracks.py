import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Genre;


CREATE TABLE Artist(
   id INTEGER PRIMARY KEY NOT NULL UNIQUE,
   name TEXT UNIQUE
);

CREATE TABLE Album(
   id INTEGER PRIMARY KEY NOT NULL UNIQUE,
   artist_id INTEGER,
   title TEXT UNIQUE
);

CREATE TABLE Genre(
   id INTEGER NOT NULL PRIMARY KEY UNIQUE,
   name TEXt UNIQUE
);

CREATE TABLE Track(
   id INTEGER PRIMARY KEY NOT NULL UNIQUE,
   album_id INTEGER,
   title TEXT UNIQUE,
   len INTEGER, rating INTEGER, count INTEGER,
   genre_id INTEGER
);
''')

fname = "Library.xml"

def lookup(d, value):
    found = False
    for child in d:
        if found: return child.text
        if child.tag == 'key' and child.text == value:
           found = True
    return None

stuff = ET.parse(fname)
all = stuff.findall("dict/dict/dict")
print "Dict count :",len(all)

for entry in all:
    if(lookup(entry, "Track ID") is None): continue

    name = lookup(entry, "Name")
    artist = lookup(entry, "Artist")
    album = lookup(entry, "Album")
    count = lookup(entry, "Play Count")
    rating = lookup(entry, "Rating")
    length = lookup(entry, "Total Time")
    genre = lookup(entry, "Genre")

    if name is None or artist is None or album is None or genre is None:
        continue

    cur.execute('''INSERT OR IGNORE INTO Artist(name)
        VALUES (?)''', (artist, ))
    cur.execute('''SELECT id FROM Artist where name = ?''', (artist, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
                VALUES (?,?)''', (album, artist_id))
    cur.execute('''SELECT id FROM Album WHERE title = ?''', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name) VALUES
    (?)''', (genre,))
    cur.execute('''SELECT id FROM Genre where name = ?''', (genre,))
    genre_id = cur.fetchone()[0]



    cur.execute('''INSERT OR REPLACE INTO Track (title, album_id, len,
    rating, count, genre_id) VALUES (?,?,?,?,?,?)''', (name, album_id, length, rating, count, genre_id))



conn.commit()
