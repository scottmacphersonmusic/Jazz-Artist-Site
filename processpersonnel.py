"""
Recieve a list of personnel strings by session for a given album. Return a
dictionary of fully processed personnel as well as any additional album
information.
"""
import personnelparser
import replaces
import copy

def clean_extra_session_info(info):
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

span_tags = [('<span class="same">', ': </span>same session'),
             ('<span class="same">', ': </span>same personnel'),
             ('<span class="same">', ': </span>add'),
             ('<span class="same">', ': </span>omit'),
             ('<span class="same">', 'plays'),
             ('<span class="same">', 'replaces')
]

class ProcessPersonnel():
    def __init__(self, personnel):
        self.personnel = personnel
        self.extra_info = {}

    def filter_keywords(self, session):
        if "same" in session \
        or "add" in session \
        or "omit" in session \
        or "plays" in session \
        or "replaces" in session:
            return True
        else:
            return False

    def convert_to_dicts(self, session):
        return personnelparser.album_artists(session)

    def add(self, previous_personnel, modifier):
        added_artist = modifier.lstrip("add ") # will this need to deal with more than one artist?
        added_artist_dict = self.convert_to_dicts(added_artist)
        modified_personnel = previous_personnel
        modified_personnel.append(added_artist_dict)
        return modified_personnel

    def omit(self, previous_personnel, modifier):
        target = modifier.lstrip("omit ") # will this need to deal with more than one artist?
        modified_personnel = [artist for artist
                              in previous_personnel
                              if target not in artist.values()]
        return modified_personnel

    def replaces(self, previous_personnel, modifier):
        rep_instance = replaces.ReplacePersonnel(previous_personnel, modifier)
        modified_personnel = rep_instance.build_replacement_personnel()
        return modified_personnel

    def plays(self, previous_personnel, modifier):
        split = modifier.split("plays")
        l_name, inst = split[0].rstrip(), split[1].lstrip()
        for artist in previous_personnel:
            if l_name in artist.values():
                target = artist
                previous_personnel.remove(artist)
        name = [(n, target[n]) for n in target if 'name' in n]
        sorted_name = sorted(name)
        temp = ""
        for name in sorted_name:
            temp += name[1] + " "
        temp += inst
        temp_dict = self.convert_to_dicts(temp)
        modified_personnel = previous_personnel
        modified_personnel.append(temp_dict)
        return modified_personnel
        
    def apply_modifier(self, previous_personnel, modifier):
        if "add" in modifier:
            return self.add(previous_personnel, modifier)
        elif "omit" in modifier:
            return self.omit(previous_personnel, modifier)
        elif "replaces" in modifier:
            return self.replaces(previous_personnel, modifier)
        elif "plays" in modifier:
            return self.plays(previous_personnel, modifier)
        elif "same" in modifier:
            return previous_personnel

    def assign_and_remove_alternate_issue_info(self, personnel):
        album_info = []
        for string in personnel:
            if "**" in string:
                clean_string = clean_extra_session_info(string)
                album_info.append(clean_string)
                personnel.remove(string)
        index = 1
        extra_info = {}
        for string in album_info:
            key = "alt_album_info_" + str(index)
            extra_info[key] = string
            index += 1
        return personnel, extra_info
        
    def clean_first_session(self, session):
        # print session, "\n"*2
        for item in span_tags:
            if item[0] in session \
            and item[1] in session \
            and "span" in item[1]:
                personnel = session.lstrip(item[0])
                personnel = personnel.split(item[1])
                personnel = self.convert_to_dicts(personnel[0])
                return personnel
            if item[0] in session \
            and item[1] in session:   # the following block looks redundant - may be a better way?
                print "We're looking at either 'plays' or 'replaces'!"
                personnel = session.lstrip(item[0])
                personnel = personnel.split(": </span>")
                personnel = self.convert_to_dicts(personnel[0])
                return personnel
        return self.convert_to_dicts(session)

    def album_personnel(self):
        # will want to treat extra album info (beginning w/**)
        print "original personnel strings:"
        for item in self.personnel:
            print item, "\n"
        personnel, extra_info = self.assign_and_remove_alternate_issue_info(self.personnel)
        album_personnel = [self.clean_first_session(personnel[0])]
        #probably need to make sure there are more than one personnel string
        for session in personnel[1:]:
            if self.filter_keywords(session):
                previous_personnel = copy.deepcopy(album_personnel[-1])
                album_personnel.append(self.apply_modifier(previous_personnel, session))
            else:
                album_personnel.append(self.convert_to_dicts(session))
        print "\nalbum_personnel:"
        for item in album_personnel:
            print type(item)
            for artist in item:
                print artist
            print
        print extra_info
        
                
                

# make a list full of tuples with common markup that will be encountered
# make a function for the first session in case it has span tags
    # make a seperate function(/s) to deal with keywords that can be applied to the first session if need be
# figure out how to use local copy of artist catalog page html instead of internet

# Albums to test against:
    # 0 - 1, Kenny Clarke - Bohemia After Dark
        # generic album
    # 0 - 5, Julian "Cannonball" Adderley
        # 'same session' in first personnel
        # 'replaces' in later personnel
    # 0 - 8, Sarah Vaughan In The Land Of Hi-Fi
        # 'same personnel' in first and subsequent personnel
    # 0 - 22, The Complete Columbia Recordings Of Miles Davis With John Coltrane
        # 'add' in 3rd personnel
        # 'replaces' in 5th
    # 0 - 29, Various Artists - The Sound Of Big Band Jazz In Hi-Fi!
        # 'same' and 'replaces' in first personnel
    # 0 - 78, Cannonball Adderley - Alabama/Africa
        # 'same' and 'add' in first personnel
    # 0 - 84, Nancy Wilson/Cannonball Adderley
        # 'omit' in 2nd
    # 25 - 2, Teddy Hill - I'm Happy, Darling, Dancing With You / Blue Rhythm Fantasy
        # 'plays' in first personnel
    # 25 - 60, Various Artists - Great Jazz Reeds
        # 'add' in first personnel
    # 26 - 6, Fletcher Henderson And His Orchestra
        # 'omit' in first personnel
    # 33 - 5, 33, 34, 54
        # all use 'plays' shorthand after first personnel


# BOOKMARK check to see if there are cases where 'add' or 'omit' have multiple artists to deal with
    # for that matter - 'replaces' or 'plays'?
