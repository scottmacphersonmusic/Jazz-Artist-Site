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
        """
        Use the personnelparser module to convert a given session's personnel
        string into a dictionary.
        """
        return personnelparser.album_artists(session)

    def add(self, previous_personnel, modifier):
        """
        Expand a session's personnel string containing the 'add' keyword into
        a complete personnel dict.
        """
        added_artists = modifier.lstrip("add ")
        added_artist_dicts = self.convert_to_dicts(added_artists)
        modified_personnel = previous_personnel
        for artist in added_artist_dicts:
            modified_personnel.append(artist)
        return modified_personnel

    def omit(self, previous_personnel, modifier):
        """
        Return a complete session personnel dict less the artist indicated by
        the 'omit' keyword.
        """
        targets = modifier.lstrip("omit ")
        targets = targets.split(", ")
        modified_personnel = previous_personnel
        for name in targets:
            for artist_dict in modified_personnel:
                if name in artist_dict.values():
                    modified_personnel.remove(artist_dict)
        return modified_personnel

    def replaces(self, previous_personnel, modifier):
        """
        Return a complete session personnel dict modified according to the
        'replaces' keyword.
        """
        rep_instance = replaces.ReplacePersonnel(previous_personnel, modifier)
        modified_personnel = rep_instance.build_replacement_personnel()
        return modified_personnel

    def plays(self, previous_personnel, modifier):
        """
        Return a complete session personnel dict with modified instrumentation
        for the artist indicated by the 'plays' keyword.
        """
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
        """
        Determine which keyword is being used in a given session's personnel
        string and call the corresponding method. Return a complete, modified
        personnel dict.
        """
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

    def extract_alternate_album_info(self, personnel):
        """
        Extract any extra album info that may have been scraped along with the
        personnel strings and return the personnel and extra info isolated from
        one another.
        """
        album_info = []
        for string in personnel:
            if "**" in string:
                clean_string = clean_extra_session_info(string)
                album_info.append(clean_string)
                personnel.remove(string)
        return personnel, album_info

    def clean_first_session(self, session):
        """
        Remove any markup if present and return a complete personnel dict for
        the first session.
        """
        for item in span_tags:
            if item[0] in session \
            and item[1] in session:
                personnel = session.lstrip(item[0])
                personnel = personnel.split(": </span>")
                personnel = self.convert_to_dicts(personnel[0])
                return personnel
        return self.convert_to_dicts(session)

    def album_personnel_to_dict(self, album_personnel):
        """
        Recieve a list of session personnel dicts and return a dict where each
        of those is a value.
        """
        session_count = 1
        album_personnel_dict = {}
        for session in album_personnel:
            key = "personnel_" + str(session_count)
            album_personnel_dict[key] = session
            session_count += 1
        return album_personnel_dict

    def album_personnel(self):
        """
        Use the above methods (where necessary) to produce a dict for each
        session's complete personnel. Also produce a dict for alternate album
        info if present.  Return a dict where each of the session dicts is a
        value.
        """
        personnel, album_info = self.extract_alternate_album_info(self.personnel)
        album_personnel = [self.clean_first_session(personnel[0])]
        for session in personnel[1:]:
            if self.filter_keywords(session):
                previous_personnel = copy.deepcopy(album_personnel[-1])
                album_personnel.append(self.apply_modifier(previous_personnel, session))
            else:
                album_personnel.append(self.convert_to_dicts(session))
        album_personnel = self.album_personnel_to_dict(album_personnel)
        if len(album_info) == 1:
            album_personnel["alt_album_info_1"] = album_info[0]
        # for item in album_personnel:
        #     print item, album_personnel[item]
        return album_personnel

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
    # 25 - 59, The Metronome All-Star Bands
        # multiple artist 'omit' keyword in second personnel string
    # 25 - 60, Various Artists - Great Jazz Reeds
        # 'add' in first personnel
    # 26 - 6, Fletcher Henderson And His Orchestra
        # 'omit' in first personnel
    # 26 - 165, Dexter Gordon Quartet - The Apartment
        # multiple artist 'add' keyword in second personnel string
    # 33 - 5, 33, 34, 54
        # all use 'plays' shorthand after first personnel

# To-Do:
    # can this module handle a personnel string with TWO keywords?:
        # ex: "Brookmeyer plays (valve trombone). Cutty Cutshall (trombone) replaces McGarity"
