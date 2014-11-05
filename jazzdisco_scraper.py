# build a webscraper for http://www.jazzdisco.org/
# identify the record lable links diffently to treat differently?
# there will be a more involved process for getting at the record lable info...

from bs4 import BeautifulSoup
import requests
import personnel-parser

BASE_URL = "http://jazzdisco.org/"

def make_soup(url):
	r = requests.get(url)
	data = r.text
	return BeautifulSoup(data)

def get_category_links(url):
	soup = make_soup(url)
	table = soup.find("table")
	category_links = [BASE_URL + a.get('href') + 'catalog/' for a in table.find_all('a')]
	return category_links

category_links = get_category_links(BASE_URL)
test_page = category_links[0] # Cannonball catalog
# test_soup = make_soup(test_page)

class ArtistCatalog():
	
	def __init__(self, artist_url):
		self.artist_url = artist_url
		self.soup = make_soup(self.artist_url)
		self.content = self.soup.find(id="catalog-data")
		self.make_unicode_list() # call function when object is instantiated
		self.album_dict = {} # final dict to put all info in

	def make_unicode_list(self):
		c = self.content.prettify()
		s = c.split("<h3>")
		unicode_list = []
		for i in s[1:]:
			if not i.startswith("<h2>"):
				unicode_list.append("<h3>" + i)
			else:
				unicode_list.append(i)
		return unicode_list


class Album():

	def __init__(self, album_info):
		self.album_info = album_info

	def extract_personnel_strings(self): #
		# find first personnel string
		start_1 = self.album_info.index("</h3>") + 5 # tag is 5 characters long
		end_1 = self.album_info.index('<div class="date">')
		p_string_1 = self.album_info[start_1:end_1]
		# find second personnel string
		copy = self.album_info
		target_string = copy.split("</table>")[1]
		end_2 = target_string.index("<div")
		p_string_2 = target_string[:end_2]
		return p_string_1, p_string_2

	def create_personnel_dicts(self):
		pass # use stuff from personnel-parser to put personnel info in dicts



x = ArtistCatalog(test_page)
a_i = x.make_unicode_list()[0] # first item (album markup) in unicode list
y = Album(a_i)
print y.extract_personnel_strings()




		
# content: <div id="catalog-data">
# ( year of recording/age of artist: <h2> )
# personnel string: indicated by newline character in dom - "data"
# recording location/date: <div class="date">
# track titles/catalog num: <table>
	# additional personnel: text data following <table>
	# additional tracks: <table>
	# additional loc/date: <div class="date">

# make album class 
# *(some record info uses "replace" format with personnel for multiple sessions)
# may wish to address age of artist info in catalog tables
	
	# album title, 				ex: Kenny Clarke - Bohemia After Dark
	# album id, 					ex: Savoy MG 12017
	# recording date/location, 		ex: NYC, June 28, 1955
		# multiple sessions?
	# personnel
		# see 'personnel-parser.py'
	# tracks
		# track names
		# track id's
	# additional personnel
	# additional tracks


# make artist class
	
	# artist name
	# albums they've been on