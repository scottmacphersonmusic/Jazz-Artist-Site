# a script to parse the artist-info string and create navigable dicts out of them
# put this all in a class?
import re

# artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'
artists = "Pharoah Sanders (tenor,soprano saxophone, bells, percussion) Michael White (violin, percussion) Lonnie Liston Smith (piano, electric piano, claves, percussion) Cecil McBee (bass, finger cymbals, percussion) Clifford Jarvis (drums, maracas, bells, percussion) James Jordan (ring cymbals -3)"
word_list = artists.split()

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

def has_multiple(l): # use for both multiple artists and multiple instruments
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

# return boolean for whether or not an instrument has multiple ranges represented, i.e. alto,tenor,baritone saxophone
def multiple_ranges_inst(word):
	multiple_ranges = False
	for letter in word[:len(word) - 1]: # avoid the last comma if its there
		if letter == ",":
			multiple_ranges = True
	return multiple_ranges

# return boolean for whether or not multiple-word instruments are present in a list
def multiple_word_instrument(inst_list): # takes list of instruments
	multiple_names = False
	for word in inst_list:
		if not word.endswith(",") and not word.endswith(")"):
			multiple_names = True
	return multiple_names

# ex_list = ['Pharoah', 'Sanders', '(tenor,soprano', 'saxophone,', 'bells,', 'percussion)']
ex_list = ['John', 'Coltrane', '(soprano,alto,tenor', 'saxophone,', 'percussion)']
# ex_list = ['Earl', 'Bostic', '(alto', 'saxophone,', 'trumpet,', 'clarinet,', 'guitar)']
# deal with multiple artists on same instrument - use inside of list_of_artist_lists()
def multiple_instruments_same_artist(l): # where l is an artist list
	names = []
	instruments = []
	revised_instruments = []
	for word in l:
		if not word.startswith('('):
			names.append(word)
		else:
			break
	for word in l[len(names):]:
		instruments.append(word)
	#get the non-complicated ones out of the way first
	for word in instruments:
		if not 

	#check for ranges - ex) baritone,alto saxophone or soprano,alto,baritone saxophone
	split_ranges = []
	for word in instruments:
		if multiple_ranges_inst(word) == True:
			base_instrument = instruments[instruments.index(word)+1]
			ranges = word.split(",")
			for r in ranges:
				new_instrument = r + " " + base_instrument
				split_ranges.append(new_instrument)
	#check for two-worded instruments (commas)
	joined_instruments = []
	for word in instruments:
		if multiple_word_instrument(instruments):
			
	print instruments
	print split_ranges
	print joined_instruments

# ['(alto', 'saxophone,', 'trumpet,', 'clarinet,', 'guitar)']
# ['(tenor,soprano', 'saxophone,', 'bells,', 'percussion)']
multiple_instruments_same_artist(ex_list)

# does not yet adress dealing with track info!!!
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
		if not has_multiple(a_l):
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

# list_of_artist_dicts = make_list_of_artist_dicts()

# for d in list_of_artist_dicts:
# 	print d, "\n"

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
	# adress multiple-word instrument names, ex: 'alto saxophone'
		# saxophone - soprano, alto, tenor, baritone, 'baritone,alto saxophone', 
		# clarinet - bass, electric, contrabass, 
		# flute - wood, 
		# trumpet - pocket, 
		# violin - electric, Indian, 
		# something to do with formatting rather than identifying every instrument
		#	possibilty - commas, spaces - the only crazy formatting so far is the
		#	'baritone,alto saxophone' thing, also '(soprano,tenor saxophone)'
	# sometimes double-quote marks are in string - " "??? won't be an issue coming from site, right?
	# address redundancy of spliting lists into names and instruments/tracks

# ['Nat', 'Adderley', '(cornet', '-1,2,4/6)', 
# 'Donald', 'Byrd', '(trumpet', '-1,2,4,5)', 
# 'Cannonball', 'Adderley', '(alto', 'saxophone)', 
# 'Jerome', 'Richardson', '(tenor', 'saxophone,', 'flute', '-1,4/6)', 
# 'Horace', 'Silver', '(piano)', 
# 'Paul', 'Chambers', '(bass)', 
# 'Kenny', 'Clarke', '(drums)']