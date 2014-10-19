# a script to parse the artist-info string and create navigable dicts out of them
import re

artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'

word_list = artists.split()

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

def has_multiple_artists(l):
	commas = False
	for word in l:
		if word.endswith(','):
			commas = True
	if commas == True:
		return True

def clean_word(w):
	if w.startswith('(') and w.endswith(')'):
		x = w.lstrip('(')
		return x.rstrip(')')
	elif w.startswith('-') and w.endswith(')'):
		x = w.lstrip('-')
		return x.rstrip(')')
	elif w.startswith('('):
		return w.lstrip('(')
	elif w.endswith(')'):
		return w.rstrip(')')
	elif w.endswith(','): # for mult. artists on same instrument
		return w.rstrip(',')
	else:
		return w

def make_artist_list():
	artist_list = []
	for word in word_list:
		if not word.endswith(')'):
			artist_list.append(word)
		else:
			artist_list.append(word)
			break
	for word in word_list[:len(artist_list)]:
		word_list.remove(word)
	return artist_list


# deal with multiple artists on same instrument
# does not yet adress dealing with track info!!!
ex_list = ["Bobby", "Byrne,", "Jimmy", "Cleveland", "(trombone)"]
def multiple_artists_same_instrument(l):
	# returns a list of new lists per each artist
	names = []
	instrument = []
	new_lists = []
	for word in l:
		if not word.startswith('('):
			names.append(word)
		else:
			break
	for word in l[len(names):]:
		if not contains_digits(word):
			instrument.append(word)
	num_artists = 1
	for name in names:
		if name.endswith(','):
			num_artists += 1
	# make a new list for each artist, put it in new_lists
	temp_list = []
	while num_artists > 0:
		if num_artists > 1:
			for name in names:
				if not name.endswith(','):
					temp_list.append(clean_word(name))	
				else:
					temp_list.append(clean_word(name))
					temp_list.append(instrument[0])
					break
		else: # last extra artist
			for name in names:
				temp_list.append(name)
			temp_list.append(instrument[0])
		# get rid of processed names
		for n in names[:(len(temp_list) - 1)]:
			names.remove(n)

		new_lists.append(temp_list)
		temp_list = []
		num_artists -= 1	
	return new_lists


def list_of_artist_lists():
	list_of_artist_lists = []
	while len(word_list) > 0:
		a_l = make_artist_list()
		if not has_multiple_artists(a_l):
			list_of_artist_lists.append(a_l)
		else:
			mult_art = multiple_artists_same_instrument(a_l)
			for i in mult_art:
				list_of_artist_lists.append(i)
	return list_of_artist_lists


# takes one artist list and converts into useful dictionary
def make_artist_dict(l):
	artist_dict = {}
	artist_list = l
	# create sub-lists for name, instrument, track
	names = [] 
	instrument = []
	for i in artist_list:
		if not i.startswith('('):
			names.append(i)
		else:
			break
	for i in artist_list[len(names):]:
		if contains_digits(i):
			artist_dict['tracks'] = clean_word(i)
		else:
			instrument.append(clean_word(i))
	
	# create dict name attrs 
	if len(names) == 3: 
		artist_dict['first_name'] = clean_word(names[0])
		artist_dict['middle_name'] = names[1]
		artist_dict['last_name'] = names[2]
	elif len(names) == 2:
		artist_dict['first_name'] = clean_word(names[0])
		artist_dict['last_name'] = names[1]
	elif len(names) == 1:
		artist_dict['first_name'] = clean_word(names[0])
	else:
		print "does not fit the name system"
	
	# create dict instrument attrs
	if len(instrument) >= 2:
		for i in instrument:
			i = clean_word(i)
		artist_dict['instrument'] = instrument
	elif len(instrument) == 1:
		artist_dict['instrument'] = clean_word(instrument[0])	
	elif len(instrument) == 0:
		artist_dict['instrument'] = 'none'
	else:
		print "does not fit instrument system"
	return artist_dict

def make_list_of_artist_dicts():
	artist_dicts = []
	a_l = list_of_artist_lists()
	for l in a_l:
		artist_dicts.append(make_artist_dict(l))
	return artist_dicts

list_of_artist_dicts = make_list_of_artist_dicts()

for d in list_of_artist_dicts:
	print d, "\n"

# print make_artist_dict()
# print make_artist_dict()
#print make_artist_dict()
#print make_artist_dict()


# {
# 'f_name': 'x', 
# 'm_name': 'y', #? more than 2 names?
# 'l_name': 'x', 
# 'instrument/s': 'i', 
# 'tracks'; 't'} 
	
# To-Do:
	# adress multiple-word instrument names, ex: 'alto, saxophone'
	# use comma to identify multiple artists on same instrument
	# sometimes double-quote marks are in string - " "

# ['Nat', 'Adderley', '(cornet', '-1,2,4/6)', 
# 'Donald', 'Byrd', '(trumpet', '-1,2,4,5)', 
# 'Cannonball', 'Adderley', '(alto', 'saxophone)', 
# 'Jerome', 'Richardson', '(tenor', 'saxophone,', 'flute', '-1,4/6)', 
# 'Horace', 'Silver', '(piano)', 
# 'Paul', 'Chambers', '(bass)', 
# 'Kenny', 'Clarke', '(drums)']