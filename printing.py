"""
This module contains functions responsible for printing album info to the
console.
"""
import copy

def print_personnel(personnel_dict):
    personnel = copy.deepcopy(personnel_dict)
    odd = None
    for artist_dict in personnel:
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

def print_tracks(track_dict):
    track_keys = track_dict.keys()
    for key in track_keys[::-1]:
        if type(track_dict[key]) is dict:
            track = track_dict[key]
            print "\t\t" + track['id'] + " --- " + track['title']
        else:
            print "\t\t", track_dict[key]

def print_alt_issue_info(album_dict):
    keys = album_dict.keys()
    alt_issue_info = [word for word in keys if "alt_album_info_" in word]
    for key in alt_issue_info:
        print album_dict[key]   # this isn't working correctly - fix it!
    print "\n"

def print_album_attributes(album_dict):
    """Print album_dict attributes to the console in human readable form"""
    # print album_dict
    t = "\t"
    keys = album_dict.keys()
    date_loc = [word for word in keys if "date" in word]
    personnel = [word for word in keys if "personnel" in word]
    tracks = [word for word in keys if "tracks" in word]
    session_counter = 1
    print "\n"
    print "Album Title:     ", album_dict['album_title/id'], "\n"
    print_alt_issue_info(album_dict)
    for item in date_loc:
        print "Session " + str(session_counter) + ": ",\
            album_dict['session_' + str(session_counter) + '_date/location']
        print "\n", t, "Personnel:"
        print_personnel(album_dict['personnel_'
                        + str(session_counter)]), "\n"
        print "\n", t, "Tracks:"
        print_tracks(album_dict['session_' + str(session_counter)
                     + '_tracks']), "\n"
        print "\n"
        session_counter += 1
