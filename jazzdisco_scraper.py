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
		catalog data as well as a list of strings, each representing
		one album's markup.
		"""
		self.soup = make_soup(artist_url)
		self.catalog_soup = self.soup.find(id="catalog-data")
		self.string_markup = str(self.catalog_soup).split("<h3>")
		 
	
class Album():

	def __init__(self, string_markup, catalog_soup):
		"""
		Recieve a unicode string containing the album's content markup and a
		BeautifulSoup object containing the entire artist catalog as input and
		produce a dictionary containing all the album's data.

		string_markup will be ONE of the items from the string_markup
		attribute of an ArtistCatalog object. 

		catalog_soup will be a BeautifulSoup object stored in the catalog_soup
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
		self.parent_tag = 0
		self.sibling_limit = 0
		self.album_dict = {}

	def extract_personnel_strings(self):
		"""
		Parse string_markup to isolate and extract all personnel strings.
		"""
		target_string = string_markup.split("</h3>")[1]
		split_strings = target_string.split("</table>")
		self.personnel_strings = [string_list.splitlines()[1] 
								  for string_list in split_strings
								  if len(string_list) > 1]
		
	def create_personnel_dicts(self):
		"""
		Use the album_artists() function from the personnelparser module to
		create a list of artist dictionaries for each personnel string.
		Assign each list to its own key in the self.album_dict attribute. 
		"""
		string_num = 1
		for personnel_string in self.personnel_strings:
			album_artist = personnelparser.album_artists(personnel_string)
			key = "personnel_" + str(string_num)
			self.album_dict[key] = album_artist 
			string_num += 1

	def find_parent_tag(self):
		"""
		Use the string_markup attribute to extract the text assigned to the
		'name' property embedded within the <a> tag. Assign a BS tag object of
		the <h3> tag enclosing that to self.parent_tag to provide a starting place for assigning
		album info.
		"""
		split_markup = self.string_markup.split('name="')
		end = split_markup[1].index('">')
		personnel_string_id = split_markup[1][:end]
		start_tag = self.catalog_soup.find(
					 "a", {"name":personnel_string_id})
		self.parent_tag = start_tag.find_parent("h3")
		
	def set_sibling_limit(self):
		"""
		Scan string_markup to see how many div and table tags are present in
		the markup.  The result should indicate how many sibling tags past the 
		<h3> parent tag to account for.  Assign the result to the
		sibling_limit attribute.
		"""
		div_count = self.string_markup.count('<div class="date">')
		table_count = self.string_markup.count('<table')
		if div_count != table_count:
			print "divs don't match tables"
		else:
			self.sibling_limit = div_count

	def assign_album_title_to_dict(self):
		"""Assign album title to album_dict."""
		parent_tag = self.parent_tag
		self.album_dict['album_title/id'] = parent_tag.string
		
	def assign_date_location_to_dict(self):
		"""
		Determine how many <div> tags containing recording location and date
		info are in the markup for this album and assign each one to the 
		album_dict attribute.
		"""
		div_tags = self.parent_tag.find_next_siblings(
					"div", limit=self.sibling_limit)
		session_count = 1
		for div in div_tags:
			key = "session_" + str(session_count) + "_date/location"
			self.album_dict[key] = div.string
			session_count += 1
		
	def assign_track_info_to_dict(self):
		"""
		Determine how many <table> tags containing track info are in the
		markup for this album and create a dictionary for each one which is
		then assigned to self.album_dict. The value of each dictionary will be
		another dictionary containing ID and title info for each track.
		"""
		table_tags = self.parent_tag.find_next_siblings(
					  "table", limit=self.sibling_limit)
		session_count = 1
		for table in table_tags:
			session_key = "session_" + str(session_count) + "_tracks"
			track_data = {}
			table_data = [tr.find_all("td") for tr in table.find_all("tr")]
			track_count = 1
			for td_list in table_data:
				track_key = "track_" + str(track_count)
				track_dict = {"id": td_list[0].string, "title": td_list[1].string.rstrip("\n")}
				track_data[track_key] = track_dict
				track_count += 1
			self.album_dict[session_key] = track_data
			session_count += 1

	def build_album_dict(self):
		"""
		Call all of the functions necessary to complete the album_dict
		attribute.
		"""
		self.extract_personnel_strings()
		self.create_personnel_dicts()
		self.find_parent_tag()
		self.set_sibling_limit()
		self.assign_album_title_to_dict()
		self.assign_date_location_to_dict()
		self.assign_track_info_to_dict()

	##### Printing Functions #####
	
	def print_personnel(self, personnel_dict):
		for d in personnel_dict:
			print "\t"*2, d

	def print_tracks(self, track_dict):
		track_keys = track_dict.keys()
		for key in track_keys[::-1]:
			track = track_dict[key]
			print "\t\t" + "ID: " + track['id'] + "\t\tTitle: " + track['title']
	
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
string_markup = cannonball_catalog.string_markup[1] # first album markup
catalog_soup = cannonball_catalog.catalog_soup
cannonball_album = Album(string_markup, catalog_soup)

cannonball_album.build_album_dict()

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

