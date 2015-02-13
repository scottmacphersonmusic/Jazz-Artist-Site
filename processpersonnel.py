"""
Recieve a list of personnel strings by session for a given album. Return a
dictionary of fully processed personnel.
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
             ('<span class="same">', ': </span>same personnel')
]

class ProcessPersonnel():
    def __init__(self, personnel):
        self.personnel = personnel
        self.extra_info = {}

    def assign_and_remove_alternate_issue_info(self, personnel):
        album_info = []
        for string in personnel:
            if "**" in string:
                clean_string = clean_extra_session_info(string)
                album_info.append(clean_string)
                personnel.remove(string)
        index = 1
        for string in album_info:
            key = "alt_album_info_" + str(index)
            self.extra_info[key] = string
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
        if len(personnel) > 1:
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

    def omit_artists(self, personnel): # make sure this can handle 2+ omissions in same personnel string
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
        assign_alt_issue_info = self.assign_and_remove_alternate_issue_info(
            self.personnel)
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
        processed_personnel = {}
        key_counter = 1
        for l in convert_strings:
            key = "personnel_" + str(key_counter)
            processed_personnel[key] = l
            key_counter += 1
        if len(self.extra_info) >= 1:
            for item in self.extra_info:
                processed_personnel[item] = self.extra_info[item]
        return processed_personnel

#    #    #    #    #    #    #    #    #    #    #    #    #    #    #    #    #

    def filter_keywords(self, session):
        if "same" in session \
        or "add" in session \
        or "omit" in session \
        or "plays" in session \
        or "replaces" in session:
            return False
        else:
            return True

    def convert_to_dicts(self, session):
        return personnelparser.album_artists(session)

    def clean_first_session(self, session):
        for item in span_tags:
            if item[0] in session and item[1] in session:
                bingo = copy.deepcopy(session)
                bingo = bingo.lstrip(item[0])
                print bingo.split(item[1])


    def new_attempt(self):
        for session in self.personnel:
            if self.filter_keywords(session):
                print self.convert_to_dicts(session), "\n"
            else:
                # print span_tags, type(span_tags), "\n"
                self.clean_first_session(session), "\n"

# make a list full of tuples with common markup that will be encountered
# make a function for the first session in case it has span tags
    # make a seperate function(/s) to deal with keywords that can be applied to the first session if need be

# Albums to test against:
    # 0 - 1, Kenny Clarke - Bohemia After Dark
        # generic album
    # 0 - 5, Julian "Cannonball" Adderley
        # 'same session' in initial personnel
        # 'replaces' in later personnel
    # 0 - 8, Sarah Vaughan In The Land Of Hi-Fi
        # 'same personnel' in initial and subsequent personnel
    # 0 - 22, The Complete Columbia Recordings Of Miles Davis With John Coltrane
        # 'add' in 3rd personnel
        # 'replaces' in 5th
    # 0 - 29, Various Artists - The Sound Of Big Band Jazz In Hi-Fi!
        # 'same' and 'replaces' in initial personnel
    # 0 - 78, Cannonball Adderley - Alabama/Africa
        # 'same' and 'add' in initial personnel
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
