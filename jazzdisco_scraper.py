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
	category_links = [BASE_URL + a.get('href') + 'catalog/' \
					 for a in table.find_all('a')]
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
		pretty_content = self.content.prettify()
		split_pretty_content = pretty_content.split("<h3>")
		for item in split_pretty_content[1:]:
			if not item.startswith("<h2>"):
				self.unicode_list.append("<h3>" + item)
			else:
				self.unicode_list.append(item)

	
class Album(): #catalog_soup

	def __init__(self, string_markup, catalog_soup):
		"""
		Recieve a unicode string containing the album's content markup and a
		BeautifulSoup object containing the entire artist catalog as input and
		produce a dictionary containing all the album's data.

		string_markup will be one of the items from the unicode_list attribute
		of an ArtistCatalog object. 

		catalog_soup will be a BeautifulSoup object stored in the content
		attribute of an ArtistCatalog object.

		personnel_string_id and sibling_limit are attributes used to determine
		the starting point and bounds when navigating catalog_soup to locate
		the same markup the personnel strings were scraped from in
		string_markup.

		A dictionary containing all of an album's data will be stored in the
		album_dict attribute.
		"""
		self.string_markup = string_markup
		self.catalog_soup = catalog_soup
		self.personnel_strings = []
		self.extract_personnel_strings()
		self.album_dict = {}
		self.create_personnel_dicts()
		self.personnel_string_id = 0
		self.sibling_limit = 0
		self.set_sibling_limit()
		self.find_personnel_string_id()
		self.assign_album_data_to_album_dict()


	def extract_personnel_strings(self):
		"""
		Use the string_markup attribute from __init__ to isolate and extract
		strings of text embedded in the markup describing recording personnel
		that are not accessible by using BeautifulSoup methods.  Assign the
		resulting personnel strings to the __init__ attribute
		personnel_strings.
		"""
		# find first personnel string
		start_1 = string_markup.index("</h3>") + 5 # tag is 5 characters long
		end_1 = string_markup.index('<div class="date">')
		personnel_string_1 = string_markup[start_1:end_1]
		self.personnel_strings.append(personnel_string_1)
		# find second personnel string
		markup_copy = string_markup
		start_2 = markup_copy.split("</table>")[1]
		end_2 = start_2.index("<div")
		personnel_string_2 = start_2[:end_2]
		self.personnel_strings.append(personnel_string_2)

	def create_personnel_dicts(self):
		"""
		Use the album_artists() function from the personnelparser module to
		create a list of artist dictionaries for each personnel string.
		Assign each list to its own key in the self.album_dict attribute. 
		"""
		string_num = 1
		for string in self.personnel_strings:
			album_artist = personnelparser.album_artists(
						   string.encode('ascii', 'ignore'))
			key = "personnel_" + str(string_num)
			self.album_dict[key] = album_artist 
			string_num += 1

	def find_personnel_string_id(self):
		"""
		Use the string_markup attribute to extract the text assigned to the
		'name' property embedded within the <a> tag.  Assign the resulting
		string to the __init__ attribute personnel_string_id.

			Example:
				<a name="personnel_string_id">

		This string should be a unique identifier of a specfic album's content
		markup within the catalog and serve as a starting point for navigating
		the BeautifulSoup object of the same markup stored in the catalog_soup
		attribute.
		"""
		split_markup = self.string_markup.split('name="')
		end = split_markup[1].index('">')
		self.personnel_string_id = split_markup[1][:end]

	def set_sibling_limit(self):
		"""
		Scan string_markup to see how many div and table tags are present in
		the markup.  The result should indicate how many sibling tags past the 
		<h3> tag enclosing the personnel_string_id to account for.  Assign the
		result to the sibling_limit attribute.
		"""
		div_count = self.string_markup.count('<div class="date">')
		table_count = self.string_markup.count('<table')
		if div_count != table_count:
			print "divs don't match tables"
		else:
			self.sibling_limit = div_count

	def assign_album_data_to_album_dict(self):
		"""
		Assign album info to key:value dictionary entries stored in the
		album_dict attribute.

		Locate the starting point in catalog_soup with personnel_string_id.
		Retrieve recording date/location and track information from as many
		<div> and <table> tags as delimited by the sibling_limit attribute.

		Track info takes the form of a dictionary where each key is a track
		identifier string and each value is the track name. That dict is then
		stored as the value to a dict entry in the album_dict attribute.
		"""
		start_tag = self.catalog_soup.find(
					 "a", {"name":self.personnel_string_id})
		parent_tag = start_tag.find_parent("h3")
		self.album_dict['album_title/id'] = parent_tag.string
		# assign date/location to album_dict
		div_count = parent_tag.find_next_siblings(
					"div", limit=self.sibling_limit)
		session_count = 1
		for div in div_count:
			key = "session_" + str(session_count) + "_date/location"
			self.album_dict[key] = div.string
			session_count += 1
		# assign track info to album_dict
		table_count = parent_tag.find_next_siblings(
					  "table", limit=self.sibling_limit)
		session_count = 1
		for table in table_count:
			stripped_strings = table.stripped_strings
			key = "session_" + str(session_count) + "_tracks"
			track_data = {}
			keys = []
			values = []
			count = 0
			for string in stripped_strings:
				if count % 2 == 0:
					keys.append(string.encode('ascii', 'ignore'))
					count += 1
				else:
					values.append(string.encode('ascii', 'ignore'))
					count += 1
			count = 0
			for k in keys:
				track_data[keys[count]] = values[count]
				count += 1
			self.album_dict[key] = track_data
			session_count += 1
		
	##### Printing Functions #####
	
	def print_personnel(self, personnel_dict):
		for d in personnel_dict:
			print "\t"*2, d

	def print_tracks(self, track_list):
		for d in track_list:
			print "\t"*2, d, ": ", track_list[d]
	
	def print_album_attributes(self):
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
	

# Temporary Instantiation Tests:
category_links = get_category_links(BASE_URL)
test_page = category_links[0] # Cannonball catalog
cannonball_catalog = ArtistCatalog(test_page)
string_markup = cannonball_catalog.unicode_list[0] # first item in unicode list
catalog_soup = cannonball_catalog.content
cannonball_album = Album(string_markup, catalog_soup)
cannonball_album.create_personnel_dicts()
cannonball_album.print_album_attributes()

# Available Album Dictionary Attributes:
# ['personnel_2', 'personnel_1', 'session_1_date/location', 
# 'album_title/id', 'session_1_tracks', 'session_2_tracks', 
# 'session_2_date/location']

	# ("meta", {"name":"City"}) to locate text in soup objects


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
		# the whole module really needs to be redesigned to deal with these meta-strings

