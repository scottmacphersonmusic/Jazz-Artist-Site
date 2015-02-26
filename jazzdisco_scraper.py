"""
A content webscraper for www.jazzdisco.org.

BeautifulSoup is used to traverse html files scraped from the site that exist
in a local directory.

The ArtistCatalog class will recieve an artist catalog html file as input and
construct an object that stores a BeautifulSoup object of the catalog's content
in the attribute catalog_soup. Also will store a list of strings that each
represent the markup for one album's content in the attribute string_markup.

The Album class will recieve a string containing a given album's content
markup and a BeautifulSoup object of the artist catalog as input (both from
a single instance of the ArtistCatalog class) and produce a dictionary
containing all the album's data stored in the album_dict attribute.
"""

from bs4 import BeautifulSoup
import os
import processpersonnel
import copy
import printing

def make_soup(artist_catalog):
    """Return a BeautifulSoup object of a given html file."""
    base_path = "/Users/scottmacpherson/Desktop/Code/" +  \
                "Jazz Artist Site/site_archive/album_archive"
    file = os.path.join(base_path, artist_catalog)
    with open(file) as f:
        data = f.read()
        return BeautifulSoup(data)


class ArtistCatalog():
    def __init__(self, artist_catalog):
        """
        Store a BeautifulSoup object of a given artist catalog as well as a
        list of the markup as strings by album.
        """
        self.soup = make_soup(artist_catalog)
        self.catalog_soup = self.soup.find(id="catalog-data")
        self.string_markup = str(self.catalog_soup).split("<h3>")

    def find_album_number(self, title):
        """Given the title of an album, return the index."""
        index = 0
        for album in self.string_markup:
            if title in album:
                index = self.string_markup.index(album)
        if index != 0:
            return index
        else:
            return 'Title Not Found  :('


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

        parent_tag and sibling_limit are attributes used to determine
        the starting point and bounds when navigating catalog_soup to locate
        the same markup the personnel strings were scraped from in
        string_markup.

        A dictionary containing all of an album's data will be stored in the
        album_dict attribute.
        """
        self.string_markup = string_markup
        self.catalog_soup = catalog_soup
        self.parent_tag = 0
        self.sibling_limit = 0
        self.album_dict = None

    def extract_personnel_strings(self):
        """
        Parse string_markup to isolate and extract all personnel strings.
        """
        target_string = string_markup.split("</h3>")[1]
        split_strings = target_string.split("</table>")
        personnel = [string_list.splitlines()[1]
                     for string_list in split_strings
                     if len(string_list) > 1]
        for item in personnel:
            if '<h2>' in item:
                personnel.remove(item)
        return personnel

    def process_personnel(self, personnel):
        """
        Use the processpersonnel module to create a fully processed dict of
        the album's personnel and any extra album info if present.
        """
        process_instance = processpersonnel.ProcessPersonnel(personnel)
        album_personnel = process_instance.album_personnel()
        self.album_dict =  album_personnel

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

    def find_extra_session_info(self):
        """
        Look for a <br> tag in the markup to indicate whether there is
        extra session info or not. If so, parse and assign the info to
        self.album_dict.
        """
        markup =  self.string_markup
        if "<br/>" in markup:
            extra_session_info = markup.split("<br/>")[1]
            if "<h2>" in extra_session_info:
                extra_session_info = extra_session_info.split("<h2>")[0]
                index = len([key for key in self.album_dict.keys()
                             if "alt_album_info_" in key]) + 1
                key = "alt_album_info_" + str(index)
                self.album_dict[key] = processpersonnel.clean_extra_session_info(extra_session_info)

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
        personnel = self.extract_personnel_strings()
        self.process_personnel(personnel)
        self.find_parent_tag()
        self.find_extra_session_info()
        self.set_sibling_limit()
        self.assign_album_title_to_dict()
        self.assign_date_location_to_dict()
        self.assign_track_info_to_dict()


# Find Album Index:
# print catalog.find_album_number("Eric Dolphy - Illinois Concert")

# Temporary Instantiation Tests:
catalog = ArtistCatalog("john-coltrane.html")
string_markup = catalog.string_markup[7]
catalog_soup = catalog.catalog_soup
cannonball_album = Album(string_markup, catalog_soup)


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

cannonball_album.build_album_dict()

printing.print_album_attributes(cannonball_album.album_dict)

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# To Do:
    # make sure oddpersonnel module can deal with integers in name or track
    # write a function that searches each html file recursively for text and returns information about where it was found
    # non-critical: rewrite print functions using dict-based string formatting
    # may eventually need to deal with track-info shorthand
        # ex: "1, 4/7" - the backslash implies "1, 4,5,6,7"
    # deal with albums containing pseudonyms - Cannonball 16, 24
