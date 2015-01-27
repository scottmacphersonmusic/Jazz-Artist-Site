"""
This module identifies personnel strings that have uncommon personnel within
them and parses them accordingly.
"""
# take initial_artist_arrays from personnelparser and return the artist arrays less any suspiciously odd personnel

common_oddities = ['unidentified orchestra',
                   'unidentified orchestra, including strings',
                   'unidentified orchestra and vocal group',
                   'unidentified big band, including strings',
                   'unidentified brass, reeds and vocals'
                   'unidentified strings and vocals',
                   'unidentified strings and chorus',
                   'unidentified strings',
                   'with unidentified vocal group and orchestra',
                   '+ overdubs: unidentified strings',
                   'unidentified large orchestra',
                   'unidentified chorus',
                   'unidentified vocal chorus',
                   'unidentified brass, reeds, rhythm and strings',
                   'unidentified large studio band',
                   'with unidentified woodwind quintet: unknown',
                   'unidentified brass and strings',
                   'unidentified horns and strings',
                   'unidentified large orchestra, strings and choir',
                   'unidentified brass, woodwinds, rhythm and strings',
                   'unidentified brass, woodwinds and strings',
                   'unidentified horns, reeds and strings',
                   'unidentified studio band',
                   'unidentified woodwinds',
                   'unidentified brass, percussion and choir',
                   'unidentified brass, strings and chorus',
                   'unidentified orchestra and choir',
                   'unidentified strings, and others',
                   'unidentified trombones, guitar, woodwinds, harp and strings',
                   'unidentified vocal group',
                   'unidentified large symphony orchestra',
                   'unidentified string quartet',
                   '+ overdubs: unidentified horns and strings',
                   'unidentified woodwinds and strings',
                   'unidentified brass and woodwinds',
                   'unidentified horn and brass',
                   'unidentified choir',
                   'unidentified orchestra, and others',
                   'unidentified band vocals (-1)',
                   'unidentified 5 strings',
                   'unidentified oboe and strings',
                   'unidentified Afro-Cuban band',
                   'unidentified big band',
                   'unidentified 22 voices',
                   'with unidentified brass, woodwinds, strings and vocal chorus',
                   'unidentified percussion',
                   'unidentified studio orchestra',
                   'unidentified voices',
                   'unidentified strings, harp, vocal choir',
                   'unidentified brass, L.A. Philharmonic Strings with Michael Gibbs (conductor)'

                   'New York Philharmonic',
                   'Cincinnati Symphony Orchestra',
                   'The Montreal International Jazz Festival Orchestra',
                   'Cathedral Choral Society Chorus, Duke Ellington School Of Arts Show Choir, Cathedral Choral Society Orchestra',
                   'Sydney Symphony Orchestra',
                   'Onzy Matthews Orchestra',
                   'percussion and choir',
                   'String Section Of The Sudfunk Symphony Orchestra, Stuttgart',
                   'Strings Of Sudfunk Symphony Orchestra, Stuttgart',
                   'Members Of Radio Symphony Orchestra, Stuttgart',
                   'London Orchestra, The Royal Ballet, The Cambodian Royal Palace',
                   'with a full orchestra:'
]    #maybe use this to list the full orchestras/philharmonics/ensembles that will be encountered?

odd_words = ['unidentified',
             'including',
             'and',
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
#             'unknown',
             'trombone',
             'guitar',
             'harp',
             'symphony',
             'quartet',
             'Afro-Cuban'
]

def odd_or_standard(artists):
    odd_personnel = None
    for a in artists:
        if 'unidentified' in a:   # or is one of the cap. O Orchestras or Sympyhonies or Philharmonics...
            odd_personnel = a
    standard_personnel = [a for a in artists if 'unidentified' not in a]
    return odd_personnel, standard_personnel

# will need to make sure the instruments I'm checking for aren't inside parens
# also can use the regex number checker from personnelparser to look for either track info or numbers inside p-strings

def isolate_odd_personnel(odd_personnel):
    isolate_odd = []
    for a in odd_personnel:  # will it ever be the case that there is more than one sub-personnel item with 'unidentified'?
        for w in odd_words:
            if w in a:
                isolate_odd.append(a)
    isolate_standard = odd_personnel[len(isolate_odd):]
    return isolate_odd, isolate_standard

def odd_personnel_to_dict(isolate_odd):
    if isolate_odd[-1].endswith(','):
        isolate_odd[-1] = isolate_odd[-1].rstrip(',')
    odd_dict = {}
    counter = 1
    for o in isolate_odd:
        key = "odd_" + str(counter)
        odd_dict[key] = o
        counter += 1
    return odd_dict
