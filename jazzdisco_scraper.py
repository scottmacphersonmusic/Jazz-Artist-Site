# build a webscraper for http://www.jazzdisco.org/
# identify the record lable links diffently to treat differently?
# there will be a more involved process for getting at the record lable info...

from bs4 import BeautifulSoup
import requests
import personnelparser

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

class ArtistCatalog():
	
	def __init__(self, artist_url):
		self.artist_url = artist_url
		self.soup = make_soup(self.artist_url)
		self.content = self.soup.find(id="catalog-data")
		self.unicode_list = []
		self.make_unicode_list()

	def make_unicode_list(self):
		c = self.content.prettify()
		s = c.split("<h3>")
		for i in s[1:]:
			if not i.startswith("<h2>"):
				self.unicode_list.append("<h3>" + i)
			else:
				self.unicode_list.append(i)

	def find_target_album(self):
		print self.content.find("a", {"name":"savoy-mg-12017"}) # boo-fuckin-ya!

		# ("meta", {"name":"City"})

		# self.content.find("h3").find_next_sibling() <- this works

		 # text='savoy-mg-12017'
		 # text='name="savoy-mg-12017"'
		


class Album():

	def __init__(self, album_info, catalog_data):
		self.album_info = album_info
		self.catalog_data = catalog_data
		self.p_strings = []
		self.extract_personnel_strings()
		self.album_dict = {}
		self.create_personnel_dicts()
		self.p_string_id = 0
		self.find_p_string_id()
		# self.find_target_album()


	def extract_personnel_strings(self):
		# find first personnel string
		start_1 = self.album_info.index("</h3>") + 5 # tag is 5 characters long
		end_1 = self.album_info.index('<div class="date">')
		p_string_1 = self.album_info[start_1:end_1]
		self.p_strings.append(p_string_1)
		# find second personnel string - will probly be more p_strings for other albums
		copy = self.album_info
		target_string = copy.split("</table>")[1]
		end_2 = target_string.index("<div")
		p_string_2 = target_string[:end_2]
		self.p_strings.append(p_string_2)

	def create_personnel_dicts(self):
		# first personnel string
		p_string_1 = (self.p_strings[0]).encode('ascii', 'ignore') # convert to ascii
		p_1 = personnelparser.AlbumPersonnel(p_string_1)
		p_1_Album_objects = []
		for a in p_1.final_arrays:
			p_1_Album_objects.append(personnelparser.AlbumArtist(a))
		p_1_Album_dicts = [] # get just the artist_dict attrs
		for a in p_1_Album_objects:
			p_1_Album_dicts.append(a.artist_dict)
		self.album_dict['personnel_1'] = p_1_Album_dicts
		# second personnel string
		p_string_2 = (self.p_strings[1]).encode('ascii', 'ignore')
		p_2 = personnelparser.AlbumPersonnel(p_string_2)
		p_2_Album_objects = []
		for a in p_2.final_arrays:
			p_2_Album_objects.append(personnelparser.AlbumArtist(a))
		p_2_album_dicts = []
		for a in p_2_Album_objects:
			p_2_album_dicts.append(a.artist_dict)
		self.album_dict['personnel_2'] = p_2_album_dicts

	def find_p_string_id(self):
		# helps to pair p_strings with the rest of album info
		# id should be compared to <a name="p_string_id"> in <h3> tag
		split_info = self.album_info.split('name="')
		end = split_info[1].index('">')
		# self.album_dict['p_string_id'] = split_info[1][:end]
		self.p_string_id = split_info[1][:end]

	def find_target_album(self):
		# which <h3> heading has the desired p_string_id?
		# print self.catalog_data.find(text=self.p_string_id).find_next_sibling()
		pass


x = ArtistCatalog(test_page)
a_i = x.unicode_list[0] # first item (album markup) in unicode list
print x.find_target_album()
c_d = x.content
y = Album(a_i, c_d)
z = y.album_dict
# print z['p_string_id']
# a = z['personnel_1']
# print "Personnel String ID: ", z['p_string_id']
# print "Personnel String 1: "
# for d in a:
# 	print d
# b = z['personnel_2']
# print "Personnel String 2: "
# for d in b:
# 	print d

# !!! Use p_string_id to id the album id to start from using next_sibling iterator from there

		
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