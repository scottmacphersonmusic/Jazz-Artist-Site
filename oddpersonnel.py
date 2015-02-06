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
                    'percussion and choir',
                    'Duke Ellington And His Orchestra',
                    'NDR Big Band',
                    'New York Chamber Symphony',
                    'Kurt Edelhagen Big Band',
                    'String Section Of The Sudfunk Symphony Orchestra, Stuttgart',
                    'Strings Of Sudfunk Symphony Orchestra, Stuttgart',
                    'Members Of Radio Symphony Orchestra, Stuttgart (string orchestra)',
                    'Syracuse Symphony',
                    'New Japan Philharmonic',
                    "American Composer's Orchestra",
                    'Fairfield Orchestra',
                    'Stuttgarter Kammerorchester',
                    'Brooklyn Philharmonic',
                    'Myrna Summers And The Interdenominational Singers',
                    'American Brass Quintet',
                    'Piece For Four Celli And Two Trombones',
                    'Roland Kirk Spirit Choir (backing vocals)',
                    'National Philharmonic Orchestra (-6/9)',
                    'Ambrosian Choir (-9)',
                    'London Orchestra, The Royal Ballet, The Cambodian Royal Palace',
                    'Toshiyuki Miyama And His New Herd Orchestra',
                    'overdubbed 14 piece strings',
                    "New York Group Singer's Big Band",
                    'Hand Made Band',
                    '5 horns, 5 flutes, 10 celli, harp, percussion',
                    'probably 4 trumpet, 3-4 trombone, 5 reeds and strings',
                    'New Orchestra Of Boston',
                    '90 voice Sound Awareness Ensemble',
                    "10 members of The West Los Angeles Christian Academy Children's Choir",
                    'Chuck Niles And The Los Angeles Modern Strings Orchestra (-5)',
                    '

]    #maybe use this to list the full orchestras/philharmonics/ensembles that will be encountered?

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
#             'unknown',
             'trombone',
             'guitar',
             'harp',
             'symphony',
             'quartet',
             'Afro-Cuban',
             'and'
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
            elif a == isolate_odd[-1]:
                break

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
