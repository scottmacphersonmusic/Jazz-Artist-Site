"""
This module identifies personnel strings that have uncommon personnel within
them and parses them accordingly.
"""
# take initial_artist_arrays from personnelparser and return the artist arrays less any suspiciously odd personnel

common_ensembles = ['Machito And His Orchestra',
                    'Oliver Nelson Orchestra',
                    'Orchestra Radio Baden-Baden',
                    'Orchestra Filarmonica Marchigiana',
                    'Radio Symphony Hannover',
                    'Cincinnati Symphony Orchestra',
                    'Montreal International Jazz Festival Orchestra',
                    'Cathedral Choral Society Chorus, Duke Ellington School Of Arts Show Choir, Cathedral Choral Society Orchestra',
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

    def __init__(self, artists):
        self.artists = artists

    def has_common_ensemble(self, artist):
        joined_artist = ""
        for i in artist:
            joined_artist += i + ' '
        for e in common_ensembles:
            if e in joined_artist:
                split_ensemble = e.split()
                # print 'artist: ', artist
                # print 'split_ensemble: ', split_ensemble
                target = [artist.index(word) for word in artist
                          if split_ensemble[-1] in word][0] + 1
                proper_ensemble = e
                standard_personnel = artist[target:]
                return proper_ensemble, standard_personnel

    def filter_common_ensembles(self):
        for a in self.artists:
            # print 'running has_common_ensemble(): ', a
            if self.has_common_ensemble(a) != None:
                # print 'branch a'
                proper_ensemble, standard_personnel = self.has_common_ensemble(a)
                index = self.artists.index(a)
                self.artists[index] = standard_personnel
                return proper_ensemble, self.artists
        return self.artists


class OddPersonnel():

    def __init__(self, artists):
        self.artists = artists

    def odd_or_standard(self):
        odd_personnel = None
        for a in self.artists:
            if 'unidentified' in a:
                odd_personnel = a
                standard_personnel = [a for a in self.artists if 'unidentified' not in a]
                return odd_personnel, standard_personnel
        return None, self.artists

# will need to make sure the instruments I'm checking for aren't inside parens
# also can use the regex number checker from personnelparser to look for either track info or numbers inside p-strings

    def isolate_odd_personnel(self, odd_personnel):
        isolate_odd = []
        for a in odd_personnel:  # will it ever be the case that there is more than one sub-personnel item with 'unidentified'?
            for w in odd_words:
                if w in a:
                    isolate_odd.append(a)
                elif a == isolate_odd[-1]:
                    break
        isolate_standard = odd_personnel[len(isolate_odd):]
        return isolate_odd, isolate_standard

    def odd_personnel_to_dict(self, isolate_odd):
        if isolate_odd[-1].endswith(','):
            isolate_odd[-1] = isolate_odd[-1].rstrip(',')
        odd_dict = {}
        counter = 1
        for o in isolate_odd:
            key = "odd_" + str(counter)
            odd_dict[key] = o
            counter += 1
        return odd_dict
