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
a single instance of the ArtistCatalog class) and produce a dictionary
containing all the album's data stored in the album_dict attribute.
"""

from bs4 import BeautifulSoup
import requests
import personnelparser
import replaces
import copy

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
                self.album_dict = {}

#       #       #       #       #       Process Personnel Strings       #       #       #       #       #       #       #

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

        def clean_extra_session_info(self, info):
                """Remove markup from extra session info strings"""
                if '<i>' in info:
                        split_i = info.split('<i>')
                        info = split_i[0] + split_i[1]
                if '</i>' in info:
                        split_ic = info.split('</i>')
                        info = split_ic[0] + split_ic[1]
                if '<br/>' in info:
                        info = info.rstrip('<br/>')
                if "\n" in info:
                        info = info.lstrip("\n")
                        info = info.rstrip("\n")
                return info

        def assign_and_remove_alternate_issue_info(self, personnel):
                album_info = []
                for string in personnel:
                        if "**" in string:
                                clean_string = self.clean_extra_session_info(string)
                                album_info.append(clean_string)
                                personnel.remove(string)
                index = 1
                for string in album_info:
                        key = "alt_album_info_" + str(index)
                        self.album_dict[key] = string
                        index += 1
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
                # use replaces module
                elif '<span class="same">' and 'replaces' in first_string:
                        split = first_string.split(': </span>')
                        original = split[0].lstrip('<span class="same">')
                        original_dict = personnelparser.album_artists(original)
                        rep_instance = replaces.ReplacePersonnel(original_dict, split[1])
                        personnel[0] = rep_instance.build_replacement_personnel()
                elif '<span class="same">' and 'add' in first_string:
                        split = first_string.split(': </span>')
                        original = split[0].lstrip('<span class="same">')
                        original_dict = personnelparser.album_artists(original)
                        add =  personnelparser.album_artists(split[1].lstrip('add '))
                        for d in add:
                                original_dict.append(d)
                        personnel[0] = original_dict
                elif 'same' in first_string:
                        print "ERROR: unrecognized version of 'same' shorthand"
                return personnel

        def original_personnel_to_dict(self, personnel):
                """
                Use the personnelparser module to convert the first/original personnel
                string into an artist dictionary.
                """
                if type(personnel[0]) == str:
                        personnel[0] = personnelparser.album_artists(personnel[0])
                return personnel

        def standard_personnel_to_dict(self, personnel):
                """
                Use the personnelparser module to convert any standard personnel
                strings (i.e. they don't have trigger words like 'add', 'same'
                or 'replaces') into dicts.
                """
                for p in personnel[1:]:
                        i = personnel.index(p)
                        if 'add' not in p \
                        and 'same' not in p \
                        and 'replaces' not in p \
                        and 'omit' not in p \
                        and 'plays' not in p:
                                personnel[i] = personnelparser.album_artists(p)
                return personnel

        def expand_plays(self, personnel):
                """
                Identify and modify any personnel strings using the keyword
                'plays'.
                """
                for p in personnel[1:]:
                        if "plays" in p:
                                index = personnel.index(p)
                                previous_personnel = copy.deepcopy(personnel[index - 1])
                                split = p.split("plays")
                                l_name, inst = split[0].rstrip(), split[1].lstrip()
                                for d in previous_personnel:
                                        if l_name in d.values():
                                                target = d
                                                previous_personnel.remove(d)
                                name = [(n, target[n]) for n in target if 'name' in n]
                                sorted_name = sorted(name)
                                temp = ""
                                for name in sorted_name:
                                        temp += name[1] + " "
                                temp += inst
                                temp_dict = personnelparser.album_artists(temp)[0]
                                revised_personnel = previous_personnel
                                revised_personnel.append(temp_dict)
                                personnel[index] = revised_personnel
                                return personnel
                return personnel

        def expand_same_personnel(self, personnel):
                """
                Substitue the original personnel for 'same personnel' shorthand and
                return the resulting array.
                """
                if len(personnel) > 1:
                        for p in personnel[1:]:
                                index = personnel.index(p)
                                if "same personnel" in p:
                                        personnel[index] = personnel[index - 1]
                return personnel

        def expand_add(self, personnel):
                for p in personnel[1:]:
                        i = personnel.index(p)
                        if type(p) == str and 'add' in p:
                                clean_string = p.lstrip("add ")
                                artist_dicts = personnelparser.album_artists(clean_string)
                                base_personnel = copy.deepcopy(personnel[i - 1])
                                #add_personnel = map(lambda x: base_personnel.append(x), artist_dicts)
                                add_personnel = []
                                for d in base_personnel:
                                        add_personnel.append(d)
                                for d in artist_dicts:
                                        add_personnel.append(d)
                                personnel[i] = add_personnel
                return personnel

        def expand_replaces(self, personnel):
                """
                If necessary, substitute the indicated artist/s into the original
                personnel dict and return an array of dicts. Otherwise return the
                original personnel.
                """
                for p in personnel[1:]:
                        if "replaces" in p:
                                i = personnel.index(p)
                                original_personnel = copy.deepcopy(personnel[i - 1])
                                rep_instance = replaces.ReplacePersonnel(original_personnel, p)
                                build_personnel = rep_instance.build_replacement_personnel()
                                rep_personnel = [item for item in build_personnel]
                                personnel[i] = rep_personnel
                return personnel

        def omit_artists(self, personnel):
                for item in personnel:
                        if 'omit' in item:
                                target = item.lstrip('omit ')
                                index = personnel.index(item)
                                original = copy.deepcopy(personnel[index - 1])
                                for d in original:
                                        if target in d.values():
                                                original.remove(d)
                                personnel[index] = original
                return personnel

        def remaining_strings_to_dict(self, personnel):
                for item in personnel:
                        if type(item) == str:
                                index = personnel.index(item)
                                personnel[index] = personnelparser.album_artists(personnel[index])
                return personnel

        def process_personnel_strings(self):
                """
                Call the functions involved in extracting and ammending personnel
                strings and assign the resulting lists of artist dicts as values to
                self.album_dict.
                """
                original_strings = self.extract_personnel_strings()
                assign_alt_issue_info = self.assign_and_remove_alternate_issue_info(
                                                                                original_strings)
                remove_markup = self.remove_markup_from_first_string(
                                                                                assign_alt_issue_info)
                original_to_dict = self.original_personnel_to_dict(remove_markup)
                standard_personnel = self.standard_personnel_to_dict(original_to_dict)
                expand_plays = self.expand_plays(standard_personnel)
                expand_same_personnel = self.expand_same_personnel(expand_plays)
                expand_add = self.expand_add(expand_same_personnel)
                expand_replaces = self.expand_replaces(expand_add)
                omit_artists = self.omit_artists(expand_replaces)
                convert_strings = self.remaining_strings_to_dict(omit_artists)
                #       #       #       #       #       #       #       #
                key_counter = 1
                for l in convert_strings:
                        key = "personnel_" + str(key_counter)
                        self.album_dict[key] = l
                        key_counter += 1

#       #       #       #       #       #       #       #       #       #       #       #       #       #       #       #       #       #       #       #

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
                        self.album_dict[key] = self.clean_extra_session_info(extra_session_info)

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
                self.find_parent_tag()
                self.find_extra_session_info()
                self.set_sibling_limit()
                self.assign_album_title_to_dict()
                self.assign_date_location_to_dict()
                self.assign_track_info_to_dict()

        ##### Printing Functions #####

        def print_personnel(self, personnel_dict):
                personnel = copy.deepcopy(personnel_dict)
                odd = None
                for artist_dict in personnel:
                        # print artist_dict
                        # print type(artist_dict)
                        for key in artist_dict.keys():
                                if 'odd' in key:
                                        odd = artist_dict
                                        personnel.remove(artist_dict)
                                        break
                for artist_dict in personnel:
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
                # print odd personnel
                if odd != None:
                        keys = [word for word in odd.keys()]
                        counter = 1
                        print "\t\t",
                        while counter <= len(keys):
                                key = "odd_" + str(counter)
                                print odd[key],
                                counter += 1

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
                for key in alt_issue_info:
                        print self.album_dict[key]
                print "\n"

        def print_album_attributes(self):
                """Print album_dict attributes to the console in human readable form"""
                t = "\t"
                keys = self.album_dict.keys()
                date_loc = [word for word in keys if "date" in word]
                personnel = [word for word in keys if "personnel" in word]
                tracks = [word for word in keys if "tracks" in word]
                session_counter = 1
                print "\n"
                print "Album Title:     ", self.album_dict['album_title/id'], "\n"
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
test_page = category_links[33] # Cannonball catalog is 0 (33, Jarret)
catalog = ArtistCatalog(test_page)

#find album:
# print catalog.find_album_number("Keith Jarrett - The Impulse Years, 1973-1974")

string_markup = catalog.string_markup[54] # first album markup
catalog_soup = catalog.catalog_soup
cannonball_album = Album(string_markup, catalog_soup)

# Problem Albums:
        # cannonball 16, 24
                # 'cannonball adderley as ronnie peters'
                # apparentely cannonball went by a couple pseudonyms:
                        # Spider Johnson
                        # Buckshot La Funque
                        # Ronnie Peters
                        # Jud Brotherly
                        # Blockbuster
                # after string has been split but before it has been assigned to dict:
                #       make a dict key for 'pseudonym'
        # Keith Jarret - some albums use 'plays' shorthand in personnel strings
                # 5, 33, 34, 54
#  BOOKMARK: figure out how to order personnel string processing so the following is solved:
                # on 34 a 'same' personnel string comes after a 'plays', but 33 and 54 are the other way...


# cannonball_album.process_personnel_strings()

# p = cannonball_album.extract_personnel_strings()

# a = cannonball_album.assign_and_remove_alternate_issue_info(p)

# r = cannonball_album.remove_markup_from_first_string(p)

# o_p = cannonball_album.original_personnel_to_dict(r)

# s_d = cannonball_album.standard_personnel_to_dict(o_p)

# e_s = cannonball_album.expand_same_personnel(s_d)

# e_a = cannonball_album.expand_add(e_s)

# e_r = cannonball_album.expand_replaces(e_s)

# e_p = cannonball_album.expand_plays(e_r)

# o_a = cannonball_album.omit_artists(e_p)

# c_s = cannonball_album.remaining_strings_to_dict(e_r)

# for item in c_s:
#         for d in item:
#                 print d, "\n"

# for thing in e_p:
#         print thing, "\n"


#for thing in e_a:
#        print "\n", thing

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

cannonball_album.build_album_dict()

# for d in cannonball_album.album_dict:
#         print d, ': ',  cannonball_album.album_dict[d], "\n"

cannonball_album.print_album_attributes()

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# t = cannonball_album.album_dict

# print t.keys()

        # ("meta", {"name":"City"}) to locate text in soup objects

# possible classes (/modules?!):
        # make a distinct personnel class to deal with the strings once they are extracted from the
        #       site using the personnelparser.py module


# To Do:
        #  remove tags: <i></i>, <b></b>
        # some extra album info can be located after the rest of the album info behind a <br> tag...
        # non-critical: rewrite print functions using dict-based string formatting
