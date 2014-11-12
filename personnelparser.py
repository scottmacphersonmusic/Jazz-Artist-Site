import re

# personnel string templates:
# artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'
artists = "Pharoah Sanders (tenor,soprano saxophone, bells, percussion) Michael White (violin, percussion) Lonnie Liston Smith (piano, electric piano, claves, percussion) Cecil McBee (bass, finger cymbals, percussion) Clifford Jarvis (drums, maracas, bells, percussion) James Jordan (ring cymbals -3)"
# artists = "Clifford Brown, Art Farmer (trumpet) Ake Persson (trombone) Arne Domnerus (alto saxophone, clarinet) Lars Gullin (baritone saxophone) Bengt Hallberg (piano) Gunnar Johnson (bass) Jack Noren (drums) Quincy Jones (arranger, director)"

class AlbumPersonnel():

	def __init__(self, personnel_string):
		self.personnel_string = personnel_string	
		self._digits = re.compile('\d')
		self.artist_arrays = [] 
		self.final_arrays = []	# this is the attribute I will want out of the object
		self.correct_problem_arrays()
	
	def initial_artist_arrays(self):
	# should result in a list of artist lists
		artist_arrays = []
		temp_array = []
		split_strings = self.personnel_string.split(")")
		for s in split_strings[:-1]: 	# leaves out extra empty item
			s += ")"					# replaces delimiter for later use
			temp_array = s.split()
			artist_arrays.append(temp_array)
		return artist_arrays

	_digits = re.compile('\d')
	def contains_digits(self, d):
		return bool(self._digits.search(d))
	
	def partition_array_by_type(self, array):
		name = []
		instrument = []
		for word in array:
			if not word.startswith("("):
				name.append(word)
			else:
				break
		for word in array[len(name):]:
			instrument.append(word)
		partitioned_array = []
		partitioned_array.append(name)
		partitioned_array.append(instrument)
		return partitioned_array

	def partitioned_arrays(self):
		i_a_a = self.initial_artist_arrays()
		partitioned_arrays = []
		for a in i_a_a:
			partitioned_arrays.append(self.partition_array_by_type(a))
		return partitioned_arrays

	
# # # The Rogue-Array Correction Suite # # #

	def has_multiple_artists(self, array):
		multiple_artists = False
		for name in array:
			if name.endswith(","):
				multiple_artists = True
		return multiple_artists

	def multiple_artists_same_instrument(self, array):
		new_arrays = []
		temp_array = []
		array[len(array) - 1] += "," # simplifies system
		for name in array:
			if not name.endswith(","):
				temp_array.append(name)
			else:
				temp_array.append(name)
				new_arrays.append(temp_array)
				temp_array = []
		return new_arrays

		# # # # # # # # # # # # # # #

	def has_mult_ranges(self, word):
		multiple_range = False	
		for letter in word[:len(word) - 1]: # ignore trailing commas
				if letter == ",":
					multiple_range = True
		return multiple_range

	def mult_range_array(self, array):
		multiple_range = False
		for inst in array:
			if self.has_mult_ranges(inst) and not self.contains_digits(inst):
				multiple_range = True
		return multiple_range

	def multiple_inst_ranges(self, array):
		revised_array = []
		for inst in array:
			if self.has_mult_ranges(inst):
				base_inst = array[array.index(inst)+1]
				array.remove(base_inst)
				ranges = inst.split(",")
				for r in ranges:
					new_inst = r + " " + base_inst
					revised_array.append(new_inst)
			else:
				revised_array.append(inst)
		return revised_array
			
		# # # # # # # # # # # # # # #	
		
		# ex: ["(alto", "saxophone)"] - inst array
	def has_mult_word_inst(self, array):
		mult_name_inst = False
		for word in array:
			if not word.endswith(",") and not word.endswith(")") \
			and not self.contains_digits(word):
				mult_name_inst = True
		return mult_name_inst

	def multiple_word_instrument(self, array):
		revised_array = []
		for word in array:
			a = array.index(word)
			b = a + 1
			if not word.endswith(",") and not word.endswith(")") \
			and not self.contains_digits(word) and not self.contains_digits(array[b]):
				revised_array.append(word + " " + array[b])
				array.remove(array[b])
			else:
				revised_array.append(word)
		return revised_array


# #	# # # # # # # # # # # # # # # # # # # # #

	def correct_problem_arrays(self):
		p_a = self.partitioned_arrays()
		corrected_arrays = []
		for a in p_a:
			name = a[0]
			inst = a[1]
			# mult art
			if self.has_multiple_artists(name):
				m_a = self.multiple_artists_same_instrument(name)
				for artist in m_a:
					temp_array = []
					temp_array.append(artist)
					temp_array.append(inst)
					corrected_arrays.append(temp_array)
			# mult ranges
			elif self.mult_range_array(inst):
				temp_array = []
				inst = self.multiple_inst_ranges(inst)
				temp_array.append(name)
				temp_array.append(inst)
				corrected_arrays.append(temp_array)
			else:
				corrected_arrays.append(a)
		# multi-word instruments
		for a in corrected_arrays:
			name = a[0]
			inst = a[1]
			if self.has_mult_word_inst(inst):
				temp_array = []
				inst = self.multiple_word_instrument(inst)
				temp_array.append(name)
				temp_array.append(inst)
				self.final_arrays.append(temp_array)
			else:
				self.final_arrays.append(a)


class AlbumArtist(): 	# run once for each artist object
	# ex: [['Jerome', 'Richardson'], ['(tenor saxophone,', 'flute', '-1,4/6)']]
	def __init__(self, artist_array): 
		# takes a partitioned artist array
			# list of two lists - artist names, instrument/track info
		self.artist_array = artist_array
		self.names = artist_array[0]
		self.inst_track = artist_array[1]
		self.artist_dict = {} 	# this is the attr I will want at the end
		self.create_artist_dict()

	def clean_word(self, w):
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
		elif w.endswith(','):
			return w.rstrip(',')
		else:
			return w


	#	#	#	Assign Track Info 	#	#	#

		# may eventually need to deal with track-info shorthand
		#	ex: "1, 4/7" - the backslash implies "1, 4,5,6,7"

	_digits = re.compile('\d') # same function in AlbumPersonnel class - redundant
	def contains_digits(self, d):
		return bool(self._digits.search(d))

	def tracks_to_dict(self):
		for i in self.inst_track:
			if self.contains_digits(i):
				self.artist_dict['tracks'] = self.clean_word(i)
				self.inst_track.remove(i)

	#	#	#	Assign Instrument Info 	#	#	#

	def instruments_to_dict(self):
		n = 1
		for i in self.inst_track:
			key = "inst_" + str(n)
			self.artist_dict[key] = self.clean_word(self.clean_word(i)) # added comma protection
			n += 1

	#	#	#	Assign Name Info 	#	#	#

	def names_to_dict(self):
		n = 1
		for i in self.names:
			key = "name_" + str(n)
			self.artist_dict[key] = self.clean_word(i)
			n += 1

	#	#	#	#	#	#	#	#	#	#	#	#

	def create_artist_dict(self):
		self.tracks_to_dict()
		self.instruments_to_dict()
		self.names_to_dict()


# Temporary Instantiation Test:
# personnel = AlbumPersonnel(artists)
# artist_dicts = []
# for a in personnel.final_arrays:
# 	artist_dicts.append(AlbumArtist(a))
# for a in artist_dicts:
# 	print a.artist_dict

# adding this line just to make sure my git branch is set up correctly
 

# To Do:
	# - set this module up to automatically take in a personnel string and return
	#	 organized artist data in json format
