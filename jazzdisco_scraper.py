"""
A content webscraper for www.jazzdisco.org.

BeautifulSoup and requests are used to produce a list of links to traverse and
scrape artist recording catalog data.

The ArtistCatalog class will recieve a url for an artist catalog page as input
and construct an object that stores a BeautifulSoup object of the catalog's
content in the attribute catalog_soup. Also will store a list of strings that
each represent the markup for one album's content in the attribute
string_markup.

The Album class will recieve a string containing a given album's content
markup and a BeautifulSoup object of the artist catalog as input (both from
an instance of the ArtistCatalog class) and produce a dictionary
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
		Recieve a string containing the album's content markup and a
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

#	#	#	#	#	Process Personnel Strings 	#	#	#	#	#	#	#

	def extract_personnel_strings(self):
		"""
		Parse string_markup to isolate and extract all personnel strings.
		"""
		target_string = string_markup.split("</h3>")[1]
		split_strings = target_string.split("</table>")
		personnel = [string_list.splitlines()[1] 
								  for string_list in split_strings
								  if len(string_list) > 1]
		return personnel

	def assign_and_remove_alternate_issue_info(self, personnel):
		counter = 1
		for string in personnel:
			key = "alt_album_info_" + str(counter)
			if "**" in string:
				self.album_dict[key] = string
				personnel.remove(string)
			counter += 1
		return personnel

	def remove_markup_from_first_string(self, personnel):
		first_string = personnel[0]
		if '<span class="same">' \
		and ': </span>same session' \
		in first_string:
			remove_left = first_string.lstrip('<span class="same">')
			remove_right = remove_left.rstrip(': </span>same session')
			personnel[0] = remove_right
		elif '<span class="same">' \
		and ': </span>same personnel' \
		in first_string: 
			remove_left = first_string.lstrip('<span class="same">')
			remove_right = remove_left.rstrip(': </span>same personnel')
			personnel[0] = remove_right
		elif 'same' in personnel[0]:
			print "ERROR: unrecognized version of 'same' shorthand"
		return personnel

	def expand_same_personnel(self, personnel):
		"""
		Substitue the original personnel for 'same personnel' shorthand and
		return the resulting array.
		"""
		if len(personnel) > 1:
			for string in personnel[1:]:
				index = personnel.index(string)
				if "same personnel" in string:
					personnel[index] = personnel[0]
		return personnel
			
	def expand_replaces(self, personnel):
		"""
		Substitute the original personnel with a new artist where identified
		by 'replaces' shorthand and return the resulting array.
		"""
		if len(personnel) > 1:
			for string in personnel[1:]:	
				index = personnel.index(string)
				first_string = personnel[0]
				if string.count("replaces") > 1:
					print "ERROR: more than one new artist?"
				elif "replaces" in string:
					replacement = string.split("replaces ")
					new_artist = replacement[0].rstrip()
					old_artist = replacement[1]
					split_strings = first_string.split(old_artist)
					left_string = split_strings[0].rsplit(")", 1)[0]
					right_string = split_strings[1].split(") ", 1)[1]
					personnel[index] = left_string + ") " \
									   + new_artist + " " \
									   + right_string
		return personnel

	def process_personnel_strings(self):
		"""
		Call the functions involved in extracting and ammending personnel
		strings and assign the results to self.personnel_strings.
		"""
		original_strings = self.extract_personnel_strings()
		assign_alt_issu_info = self.assign_and_remove_alternate_issue_info(original_strings)
		remove_markup = self.remove_markup_from_first_string(assign_alt_issu_info)
		expand_same_personnel = self.expand_same_personnel(remove_markup)
		expand_replaces = self.expand_replaces(expand_same_personnel)
		self.personnel_strings = expand_replaces

#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#

	def create_personnel_dicts(self):
		"""
		Use the album_artists() function from the personnelparser module to
		create a list of artist dictionaries for each personnel string.
		Assign each list its own key in the self.album_dict attribute. 
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
		the <h3> tag enclosing that to parent_tag to provide a starting place
		for assigning album info.
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
				if td_list[0].string is not None:  # first td is empty
					track_dict = {"id": td_list[0].string,
								  "title": td_list[1].string.rstrip("\n")}
					track_data[track_key] = track_dict
					track_count += 1
				else:
					track_data[track_key] = td_list[1].string.rstrip("\n")
					track_count += 1
			self.album_dict[session_key] = track_data
			session_count += 1

	def build_album_dict(self):
		"""
		Call all of the functions necessary to complete the album_dict
		attribute.
		"""
		self.process_personnel_strings()
		self.create_personnel_dicts()
		self.find_parent_tag()
		self.set_sibling_limit()
		self.assign_album_title_to_dict()
		self.assign_date_location_to_dict()
		self.assign_track_info_to_dict()

	##### Printing Functions #####
	
	def print_personnel(self, personnel_dict):
		for artist_dict in personnel_dict:
			keys = artist_dict.keys()
			name = [word for word in keys if "name" in word]
			inst = [word for word in keys if "inst" in word]
			tracks = [word for word in keys if "tracks" in word]
			print "\t\t",
			for word in name[::-1]:
				print artist_dict[word] + " ",
			if len(tracks) > 0:
				print " --- ",
				for word in inst[:(len(inst) - 1)]:
					print artist_dict[word] + ", ",
				print artist_dict[inst[-1]],
				for word in tracks:
					print " --- (tracks " + artist_dict[word] + ")"
			else:
				print " --- ",
				for word in inst[:(len(inst) - 1)]:
					print artist_dict[word] + ", ",
				print artist_dict[inst[-1]]


	def print_tracks(self, track_dict):
		track_keys = track_dict.keys()
		for key in track_keys[::-1]:
			if type(track_dict[key]) is dict:
				track = track_dict[key]
				print "\t\t" + track['id'] + " --- " + track['title']
			else:
				print "\t\t", track_dict[key]
				
	
	def print_alt_issue_info(self):
		keys = self.album_dict.keys()
		alt_issue_info = [word for word in keys if "alt_album_info_" in word]
		counter = 1
		for string in alt_issue_info:
			print "\t\t", self.album_dict[string], "\n"

	def print_album_attributes(self):
		"""Print album_dict attributes to the console in human readable form"""
		t = "\t"
		keys = self.album_dict.keys()
		date_loc = [word for word in keys if "date" in word]
		personnel = [word for word in keys if "personnel" in word]
		tracks = [word for word in keys if "tracks" in word]
		# if len(date_loc) != len(personnel) != len(tracks):
		# 	print "\nERROR: some session info or alternate issue ID info may be missing"
		session_counter = 1
		print "\n"
		print "Album Title:	", self.album_dict['album_title/id'], "\n"
		self.print_alt_issue_info()
		for item in date_loc:
			print "Session " + str(session_counter) + ": ", self.album_dict[
						'session_' + str(session_counter) + '_date/location']
			print "\n", t, "Personnel:"
			self.print_personnel(self.album_dict['personnel_'
				+ str(session_counter)]), "\n"
			print "\n", t, "Tracks:"
			self.print_tracks(self.album_dict['session_' + str(session_counter)
				+ '_tracks']), "\n"
			print "\n"
			session_counter += 1
	

# Temporary Instantiation Tests:
category_links = get_category_links(BASE_URL)
test_page = category_links[0] # Cannonball catalog
cannonball_catalog = ArtistCatalog(test_page)

string_markup = cannonball_catalog.string_markup[21] # first album markup
catalog_soup = cannonball_catalog.catalog_soup
cannonball_album = Album(string_markup, catalog_soup)

# Problem Albums:
	# cannonball 10
		# orchestra and undefined orchestra in personnel string
	# cannonball 16
		# 'cannonball adderley as ronnie peters' WTF???
		# apparentely cannonball went by a couple pseudonyms:
			# Spider Johnson
			# Buckshot La Funque
			# Ronnie Peters
			# Jud Brotherly
			# Blockbuster
	# cannonball 17
		# deal with 'add some musician' in personnel strings
	# cannonball 22
		# 'add Nat Adderley' - deal with add in personnel strings
	# cannonball 28
		# gnarly personnel string with 'replaces' shorthand
	# cannonball 29
		# no idea... wtf

# cannonball_album.process_personnel_strings()

# p = cannonball_album.extract_personnel_strings()

# a = cannonball_album.assign_and_remove_alternate_issue_info(p)

# r = cannonball_album.remove_markup_from_first_string(p)

# e_s = cannonball_album.expand_same_personnel(r)

# e_r = cannonball_album.expand_replaces(e_s)

# for string in e_s:
# 	print string

# for string in a:
# 	print "\n", string

# print "\nPersonnel Strings: \n"
# for string in cannonball_album.personnel_strings:
# 	print string, "\n"
	
cannonball_album.build_album_dict()


cannonball_album.print_album_attributes()

# Available Album Dictionary Attributes:
# ['personnel_2', 'personnel_1', 'session_1_date/location', 
# 'album_title/id', 'session_1_tracks', 'session_2_tracks', 
# 'session_2_date/location']

	# ("meta", {"name":"City"}) to locate text in soup objects

# make artist class
	
	# artist name
	# albums they've been on

# To Do:
	# another module to deal with record label catalog info?
		# should record label catalog info be cross-checked against artist catalog info?
		# identify the record lable links diffently to treat differently?
		# do I need to store data about the final meta string that gives info about alternate
		# issuances? 
		# ex: '** also issued on EmArcy MG 36091; Verve 314 543 828-2'
		# may need to remove tags: <i></i>, <b></b>
	# improve expand_replaces() to be able to deal with multi-person 'replace' shorthand
		# ex: "Bill Barber (tuba) Phil Bodner (reeds) Philly Joe Jones (drums) replaces Phillips, Sanfino, Blakey"


