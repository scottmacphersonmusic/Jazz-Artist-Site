# a script to parse the artist-info string and create navigable dicts out of them
import re

artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"

word_list = artists.split()

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
	else:
		return w

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

# function that generates dicts - might need to break into smaller functions
def make_artist_dict():
	artist_dict = {}
	artist_list = make_artist_list()
	# create sub-lists for name, instrument, track
	names = []
	instrument = []
	for i in artist_list:
		if not i.startswith('('):
			names.append(clean_word(i))
		else:
			break
	for i in artist_list[len(names):]:
		if contains_digits(i):
			artist_dict['tracks'] = clean_word(i)
		else:
			instrument.append(i)
	# create dict name attrs
	if len(names) == 3:
		artist_dict['first_name'] = names[0]
		artist_dict['middle_name'] = names[1]
		artist_dict['last_name'] = names[2]
	elif len(names) == 2:
		artist_dict['first_name'] = names[0]
		artist_dict['last_name'] = names[1]
	elif len(names) == 1:
		artist_dict['first_name'] = names[0]
	else:
		print "does not fit the name system"
	# create dict instrument attrs
	if len(instrument) == 0:
		artist_dict['instrument'] = 'none'
	elif len(instrument) == 1:
		artist_dict['instrument'] = clean_word(instrument[0])
	elif len(instrument) >= 2:
		artist_dict['instrument'] = clean_word(instrument)
	else:
		print "does not fit instrument system"
	return artist_dict

def make_list_of_artist_dicts():
	artist_dicts = []
	print make_artist_dict()
	print make_artist_dict()
	print word_list


print make_list_of_artist_dicts()
	


# {
# 'f_name': 'x', 
# 'm_name': 'y', #? more than 2 names?
# 'l_name': 'x', 
# 'instrument/s': 'i', 
# 'tracks'; 't'} 
	

# use make_artist_dict() in list comprehension to make list of artist dicts!!!



# ['Nat', 'Adderley', '(cornet', '-1,2,4/6)', 

# 'Donald', 'Byrd', '(trumpet', '-1,2,4,5)', 

# 'Cannonball', 'Adderley', '(alto', 'saxophone)', 
# 'Jerome', 'Richardson', '(tenor', 'saxophone,', 'flute', '-1,4/6)', 
# 'Horace', 'Silver', '(piano)', 
# 'Paul', 'Chambers', '(bass)', 
# 'Kenny', 'Clarke', '(drums)']