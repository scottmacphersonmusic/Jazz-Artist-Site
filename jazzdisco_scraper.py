"""
A content webscraper for www.jazzdisco.org.

BeautifulSoup and requests are used to produce a list of links to traverse and
scrape artist recording catalog data.

The ArtistCatalog class will recieve a url for an artist catalog page as input
and construct an object that stores a BeautifulSoup object of the catalog's
content in the attribute content. Also will store a list of unicode strings
that each represent the markup for one album's content in the attribute
self.unicode_list.

The Album class will recieve a string containing a given album's content
markup and a BeautifulSoup object of the artist catalog as input (both from
an instantiation of the ArtistCatalog class) and produce a dictionary
containing all the album's data stored in the album_dict attribute.
"""

from bs4 import BeautifulSoup
import requests
import personnelparser

BASE_URL = "http://jazzdisco.org/"

def make_soup(url):
	"""
	Recieve a url as input, access the url with requests, and return a
	BeautifulSoup object.
	"""
	r = requests.get(url)
	data = r.text
	return BeautifulSoup(data)

def get_category_links(url):
	"""
	Recieve a url as input, call make_soup() with that url, and return a list
	of urls that each lead to an artist's recording catalog page.
	"""
	soup = make_soup(url)
	table = soup.find("table")
	category_links = [BASE_URL + a.get('href') + 'catalog/' for a in table.find_all('a')]
	return category_links


class ArtistCatalog():
	
	def __init__(self, artist_url):
		"""
		Recieve an artist catalog url as input and produce a BS object of
		catalog data as well as a list of unicode strings, each representing
		one album's markup.
		"""
		self.artist_url = artist_url
		self.soup = make_soup(self.artist_url)
		self.content = self.soup.find(id="catalog-data")
		self.unicode_list = []
		self.make_unicode_list()

	def make_unicode_list(self):
		"""
		Produce a list of unicode strings that each contain the markup
		for an album so as to gain access to personnel strings.
		"""
		c = self.content.prettify()
		s = c.split("<h3>")
		for i in s[1:]:
			if not i.startswith("<h2>"):
				self.unicode_list.append("<h3>" + i)
			else:
				self.unicode_list.append(i)

	
class Album():

	def __init__(self, album_info, catalog_data):
		"""
		Recieve a unicode string containing the album's content markup and a
		BeautifulSoup object containing the entire artist catalog as input and
		produce a dictionary containing all the album's data.

		album_info will be one of the items from the unicode_list attribute
		of an ArtistCatalog object. 

		catalog_data will be a BeautifulSoup object stored in the content
		attribute of an ArtistCatalog object.

		p_string_id and sibling_limit are attributes used to determine the
		starting point and bounds when navigating catalog_data to locate the
		same markup the personnel strings were scraped from in album_info.

		A dictionary containing all of an album's data will be stored in the
		album_dict attribute.
		"""
		self.album_info = album_info
		self.catalog_data = catalog_data
		self.p_strings = []
		self.extract_personnel_strings()
		self.album_dict = {}
		self.create_personnel_dicts()
		self.p_string_id = 0
		self.sibling_limit = 0
		self.set_sibling_limit()
		self.find_p_string_id()
		self.navigate_target_album()


	def extract_personnel_strings(self):
		"""
		Use the album_info attribute from __init__ to isolate and extract
		strings of text embedded in the markup describing recording personnel
		that are not accessible by using BeautifulSoup methods.  Assign the
		resulting personnel strings to the __init__ attribute p_strings.
		"""
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
		"""
		Use each item in the list stored in __init__ attribute p_strings to
		instantiate an AlbumPersonnel object from the personnelparser module.
		
		Iterate over each artist array in the AlbumPersonnel attribute 
		final_artist_arrays and instantiate an AlbumArtist object (also from
		the personnelparser module). 
	
		Produce a list of personnel dictionaries from
		the artist_dict attribute of each AlbumArtist object and assign that
		list to a key in the album_dict attribute of this Album object. 
		"""
		# first personnel string
		p_string_1 = (self.p_strings[0]).encode('ascii', 'ignore') # convert to ascii
		p_1 = personnelparser.AlbumPersonnel(p_string_1)
		p_1_Album_objects = []
		for a in p_1.final_artist_arrays:
			p_1_Album_objects.append(personnelparser.AlbumArtist(a))
		p_1_Album_dicts = [] # get just the artist_dict attrs
		for a in p_1_Album_objects:
			p_1_Album_dicts.append(a.artist_dict)
		self.album_dict['personnel_1'] = p_1_Album_dicts
		# second personnel string
		p_string_2 = (self.p_strings[1]).encode('ascii', 'ignore')
		p_2 = personnelparser.AlbumPersonnel(p_string_2)
		p_2_Album_objects = []
		for a in p_2.final_artist_arrays:
			p_2_Album_objects.append(personnelparser.AlbumArtist(a))
		p_2_album_dicts = []
		for a in p_2_Album_objects:
			p_2_album_dicts.append(a.artist_dict)
		self.album_dict['personnel_2'] = p_2_album_dicts

	def find_p_string_id(self):
		"""
		Use the album_info attribute to extract the text assigned to the 'name'
		property embedded within the <a> tag.  Assign the resulting string to
		the __init__ attribute p_string_id.

			Example:
				<a name="p_string_id">

		This string should be a unique identifier of a specfic album's content
		markup within the catalog and serve as a starting point for navigating
		the BeautifulSoup object of the same markup stored in the catalog_data
		attribute.
		"""
		split_info = self.album_info.split('name="')
		end = split_info[1].index('">')
		self.p_string_id = split_info[1][:end]

	def set_sibling_limit(self):
		"""
		Scan album_info to see how many div and table tags are present in the
		markup.  The result should indicate how many sibling tags past the 
		<h3> tag enclosing the p_string_id to account for.  Assign the result
		to the sibling_limit attribute.
		"""
		div = self.album_info.count('<div class="date">')
		table = self.album_info.count('<table')
		if div != table:
			print "divs don't match tables"
		else:
			self.sibling_limit = div

	def navigate_target_album(self):
		"""
		Assign album info to key:value dictionary entries stored in the
		album_dict attribute.

		Locate the starting point in catalog_data with p_string_id. Retrieve
		recording date/location and track information from as many <div> and
		<table> tags as delimited by the sibling_limit attribute.

		Track info takes the form of a dictionary where each key is a track
		identifier string and each value is the track name. That dict is then
		stored as the value to a dict entry in the album_dict attribute.
		"""
		first_link = self.catalog_data.find("a", {"name":self.p_string_id})
		parent = first_link.find_parent("h3")
		self.album_dict['album_title/id'] = parent.string
		# assign date/location to album_dict
		divs = parent.find_next_siblings("div", limit=self.sibling_limit)
		index = 1
		for d in divs:
			key = "session_" + str(index) + "_date/location"
			self.album_dict[key] = d.string
			index += 1
		# assign track info to album_dict
		tables = parent.find_next_siblings("table", limit=self.sibling_limit)
		index = 1
		for t in tables:
			strings = t.stripped_strings
			key = "session_" + str(index) + "_tracks"
			tracks = {}
			keys = []
			values = []
			count = 0
			for s in strings:
				if count % 2 == 0:
					keys.append(s.encode('ascii', 'ignore'))
					count += 1
				else:
					values.append(s.encode('ascii', 'ignore'))
					count += 1
			count = 0
			for k in keys:
				tracks[keys[count]] = values[count]
				count += 1
			self.album_dict[key] = tracks
			index += 1
		
	##### printing functions #####
	
	def print_personnel(self, personnel_dict):
		p = personnel_dict
		t = "\t"
		for d in p:
			print t*2, d
			# print d['name_1'], " ",
			# if 'name_2' in d:
			# 	print d['name_2'], " ",
			# if 'name_3' in d:
			# 	print d['name_3'], " ",
			# print ", ", d['inst_1'],
			# if 'inst_2' in d:
			# 	print ", ", d['inst_2'],
			# if 'inst_3' in d:
			# 	print ", ", d['inst_3'],
			# if 'inst_4' in d:
			# 	print", ", d['inst_4'],
			# if 'inst_5' in d:
			# 	print ", ", d['inst_5'],
			# if 'inst_6' in d:
			# 	print ", ", d['inst_6'],
			# if 'tracks' in d:
			# 	print ", ", d['tracks']
	# ['name_2', 'inst_2', 'tracks', 'name_1', 'inst_1'] 

	def print_tracks(self, track_list):
		t = "\t"
		for d in track_list:
			print t*2, d, ": ", track_list[d]
	
	def print_album_attrs(self):
		"""Print album_dict attributes to the console in human readable form"""
		t = "\t"
		print "\n"
		print "Album Title:	", self.album_dict['album_title/id'], "\n"
		print "Session 1: ", self.album_dict['session_1_date/location']
		print t, "Personnel:"
		print self.print_personnel(self.album_dict['personnel_1'])
		print t, "Tracks: "
		print self.print_tracks(self.album_dict['session_1_tracks']), "\n"
		print "Session 2: ", self.album_dict['session_2_date/location']
		print t, "Personnel: " 
		print self.print_personnel(self.album_dict['personnel_2'])
		print t, "Tracks: " 
		print self.print_tracks(self.album_dict['session_2_tracks']), "\n"

# ['personnel_2', 'personnel_1', 'session_1_date/location', 
#  'album_title/id', 'session_1_tracks', 'session_2_tracks', 
#  'session_2_date/location']

	# ("meta", {"name":"City"})

	# self.content.find("h3").find_next_sibling() <- this works	

# Temporary Instantiation Tests:
category_links = get_category_links(BASE_URL)
test_page = category_links[0] # Cannonball catalog
x = ArtistCatalog(test_page)
a_i = x.unicode_list[0] # first item (album markup) in unicode list
c_d = x.content
y = Album(a_i, c_d)
print y.print_album_attrs()


# Markup Patterns:	
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

# To Do:
	# another module to deal with record label catalog info?
		# should record label catalog info be cross-checked against artist catalog info?
		# identify the record lable links diffently to treat differently?
	# flesh out extract_personnel_strings() or make new functions to grab all of the 
	# 	personnel strings - there are often more than 2 and they are often very short
	#	and describe who replaces who by instrument in shorthand syntax

