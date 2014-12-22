# deal with personnel strings that use 'replaces' with multiple artists
	# create a tuple that has a dict for the sub and the name of the target?
	# eventually plug in to main module?
	# will need to figure out how to deal with artists subbing in a section with multiple instrumentalists
		# ex: subbing in a trumpet player in a personnel string that has multiple tpt players
	# use personnelparser.py to parse the first chunk before 'replaces'
	# maybe easier to replace artists using parsed artist dict rather than with string manipulation

import personnelparser

p_s = "Johnny Coles, Louis Mucci, Ernie Royal (trumpet) Joe Bennett, Tom Mitchell, Frank Rehak (trombone) Julius Watkins (French horn) Harvey Phillips (tuba) Cannonball Adderley (alto saxophone) Jerry Sanfino (reeds) Gil Evans (piano, arranger, conductor) Chuck Wayne (guitar) Paul Chambers (bass) Art Blakey (drums)"

ex = "Bill Barber (tuba) Phil Bodner (reeds) Philly Joe Jones (drums) \
replaces Phillips, Sanfino, Blakey"

def split_replaces(personnel):
	subs_targets = personnel.split('replaces')
	subs, targets = subs_targets[0], subs_targets[1]
	return subs, targets

def split_subs(subs):
	split_subs = subs.split(')')
	full_subs = [word + ")" for word in split_subs[:(len(split_subs) - 1)]]
	return full_subs

def split_targets(targets):
	split_targets = targets.split(',')
	clean_targets = [word.strip() for word in split_targets]
	return clean_targets

def create_sub_target_tuples(subs, targets):
	sub_dicts = [personnelparser.album_artists(sub)[0] for sub in subs]
	tuples = []
	index = 0
	for sub in sub_dicts:
		tuples.append((sub, targets[index]))
		index += 1
	return tuples


# album_artists = personnelparser.album_artists(ex)
# for d in album_artists:
# 	print d

subs, targets = split_replaces(ex)
split_subs = split_subs(subs)
split_targets = split_targets(targets)
# print split_subs
# print split_targets

print create_sub_target_tuples(split_subs, split_targets)
