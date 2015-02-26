"""
This module identifies personnel strings that have uncommon personnel within
them and parses them accordingly.
"""

common_ensembles = ['Machito And His Orchestra',
                    'Oliver Nelson Orchestra',
                    'Orchestra Radio Baden-Baden',
                    'Orchestra Filarmonica Marchigiana',
                    'Radio Symphony Hannover',
                    "St. John's Assembly",
                    'Cincinnati Symphony Orchestra',
                    'Montreal International Jazz Festival Orchestra',
                    'Cathedral Choral Society Chorus',
                    'Duke Ellington School Of Arts Show Choir',
                    'Cathedral Choral Society Orchestra',
                    'New York Philharmonic',
                    'Westminster Choir',
                    'Cincinnati Brass Ensemble',
                    'London Symphony Orchestra',
                    'London Philharmonic Orchestra',
                    'Sydney Symphony Orchestra',
                    'Onzy Matthews Orchestra',
                    'Sudfunk-Tanzorchester (Southern Radio Dance Orchestra)',
                    'The University Of Illinois Brass Ensemble (-5)',   # this and the next one have track numbers... hmm
                    'The University Of Illinois Big Band (-6)',
                    'Mercer Ellington And His Orchestra',
                    'Frank Humphries And His Orchestra',
                    'Dizzy Gillespie And His Orchestra',
                    'Mary Lou Williams And Her Orchestra',
                    "Herman McCoy's Swing Choir (vocal group)",
                    'Almost Big Band',
                    'Frank DeVol Orchestra',
                    'Boston Pops Orchestra',
                    'Duke Ellington And His Orchestra',
                    'percussion and choir',
                    'and others'
]

odd_words = ['unidentified',
             'including',
             'with',
             '+',
             'overdub',
             'brass',
             'reed',
             'rhythm',
             'string',
             'chorus',
             'choir',
             'vocal',
             'voice',
             'orchestra',
             'horn',
             'oboe',
             'other',
             'band',
             'group',
             'big',
             'large',
             'studio',
             'woodwind',
             'percussion',
             'quintet',
             'unknown',
             'trombone',
             'guitar',
             'harp',
             'symphony',
             'quartet',
             'Afro-Cuban',
             'and'
]

class ProperEnsemble():
    def __init__(self, artists, len_odd):
        self.artists = artists
        self.len_odd = len_odd

    def has_common_ensemble(self, artist):
        """
        Recieve one artist substring from a given session's personnel and return
        the common ensemble name isolated from any standard-formatted artists
        that may have been included in the artist substring. Otherwise return
        None.
        """
        joined_artist = ""
        for i in artist:
            joined_artist += i + ' '
        for ensemble in common_ensembles:
            if ensemble in joined_artist:
                split_ensemble = ensemble.split()
                target = [artist.index(word) for word in artist
                          if split_ensemble[-1] in word][0] + 1
                proper_ensemble = ensemble
                standard_personnel = artist[target:]
                return proper_ensemble, standard_personnel

    def filter_common_ensembles(self):
        """
        If there are any common ensemble names present in an artist substring
        of a given session's personnel, return a tuple with the common ensemble
        isolated from the rest of the artists. Otherwise return the personnel
        as it was recieved.
        """
        for artist in self.artists:
            if self.has_common_ensemble(artist) != None:
                proper_ensemble, standard_personnel = self.has_common_ensemble(artist)
                index = self.artists.index(artist)
                self.artists[index] = standard_personnel
                return self.artists, proper_ensemble
        return self.artists, None

    def resolve_proper(self):
        standard, odd = self.filter_common_ensembles()
        if type(odd) == str:
            key = 'odd_' + str(self.len_odd + 1)
            odd_dict = {key: odd}
            return standard, odd_dict
            # for artist in filtered_artists:
            #     if len(artist) == 0:
            #         filtered_artists.remove(artist)
        else:
            return standard, odd

class OddPersonnel():
    def __init__(self, artists):
        self.artists = artists

    def odd_or_standard(self):
        """
        Isolate any artist substrings containing the word 'unidentified' and
        return a tuple of odd personnel and standard personnel. If no odd
        personnel are found return None in place of odd personnel in the tuple.
        """
        odd_personnel = None
        for artist in self.artists:
            if 'unidentified' in artist:
                odd_personnel = artist
                standard_personnel = [a for a in self.artists if 'unidentified' not in a]
                return odd_personnel, standard_personnel
        return None, self.artists

    def isolate_odd_personnel(self, odd_personnel):
        """
        Given a list of split words from a given artist substing which is known
        to contain 'unidentified', isolate any words associated with it from any
        standard-formatted personnel that may have been included. Return a tuple
        with of the odd and standard personnel.
        """
        isolate_odd = []
        for a in odd_personnel:  # will it ever be the case that there is more than one sub-personnel item with 'unidentified'?
            for w in odd_words:
                if w in a:
                    isolate_odd.append(a)
                # this is where I'll include an elif to check for digits
                elif a == isolate_odd[-1]:
                    break
        isolate_standard = odd_personnel[len(isolate_odd):]
        return isolate_odd, isolate_standard

    def odd_personnel_to_dict(self, isolate_odd):
        """
        Concatenate the substrings identified as odd and return a dictionary
        with the new odd string as a value.
        """
        if isolate_odd[-1].endswith(','):
            isolate_odd[-1] = isolate_odd[-1].rstrip(',')
        join_odd = ""
        for word in isolate_odd:
            join_odd += word + " "
        odd_dict = {"odd_1": join_odd.rstrip()}
        return odd_dict

    def resolve_odd(self):
        odd, standard = self.odd_or_standard()
        if odd == None:
            return standard, None
        else:
            isolate_odd, isolate_standard = self.isolate_odd_personnel(odd)
            odd_dict = self.odd_personnel_to_dict(isolate_odd)
            if len(isolate_standard) >= 1:
                standard.append(isolate_standard)
            return standard, odd_dict

# Bookmark: refactor seems to be alright but is printing strangely - let's check it out!

# To-Do:
    # refactor a little bit so personnelparser module doesn't have to do as much
    # will need to make sure the instruments I'm checking for aren't inside parens
    # also can use the regex number checker from personnelparser to look for either track info or numbers inside p-strings
    # what if an artist sub-string contains more than one common ensemble?
    # will it ever be the case there is more than one sub-personnel item with 'unidentified'?

# Example Albums:
    # Cannonball - 9, 10, Dinah Washington In The Land Of Hi-Fi
        # 'unidentified' in initial and second personnel (w/'replaces')
    # Cannonball - 21, Machito And His Orchestra - Kenya-Afro Cuban Jazz
        # proper ensemble name
    # Jarret - 16, Keith Jarrett - Restoration Ruin
        # 'unidentified' followed by tracks in parens
    # Jarret - 57, Keith Jarrett - In The Light
        # proper ensemble name in multiple sessions
    # Jarret - 68, Keith Jarrett - Arbour Zena
        # proper ensemble followed by instrument in parens
    # Brubeck - 86, Dave Brubeck - The Gates Of Justice
        # multiple proper ensembles in one personnel string
    # Brubeck - 124, Dave Brubeck - To Hope! - A Celebration
        # multiple proper ensembles in one personnel string
    # Dolphy - 91, Eric Dolphy - Illinois Concert
        # multiple proper ensembles having track numbers associated with them
