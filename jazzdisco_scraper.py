# build a webscraper for http://www.jazzdisco.org/
# identify the record lable links diffently to treat differently?
# there will be a move involved process for getting at the record lable info...

from bs4 import BeautifulSoup
import requests

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

# make record class 
# *(some record info uses "replace" format with personnel for multiple sessions...)
	
	# record title, 				ex: Kenny Clarke - Bohemia After Dark
	# record id, 					ex: Savoy MG 12017
	# recording date/location, 		ex: NYC, June 28, 1955
		# multiple sessions?
	# personnel
		# name
		# instrument/s - multiple instruments?
			# *(not always an instrument - 'arranger', 'announcer', 'conductor'...)
		# are they on specific tracks?
	# tracks
		# track names
		# track id's


# make artist class
	
	# artist name
	# albums they've been on