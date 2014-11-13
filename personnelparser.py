"""
Recieve a string describing album personnel and generate a dictionary for each
artist on the album giving key:value access to data regarding name/s, 
instrument/s and track/s.

The AlbumPersonnel class recieves the personnel string and generates a list of artist
arrays broken down into two sub-lists [[name], [instruments/tracks]] stored in 
self.final_arrays.

The AlbumArtist class takes as input one partitioned artist array from the list
generated by the AlbumPersonnel class and generates an artist dictionary with
key:value pairings for each name (first, middle, last, nicknames), instrument,
and which tracks they performed on if specified. Said dict is stored in
self.artist_dict.
"""

import re

# Personnel String Templates (for testing):
# artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'
artists = "Pharoah Sanders (tenor,soprano saxophone, bells, percussion) Michael White (violin, percussion) Lonnie Liston Smith (piano, electric piano, claves, percussion) Cecil McBee (bass, finger cymbals, percussion) Clifford Jarvis (drums, maracas, bells, percussion) James Jordan (ring cymbals -3)"
# artists = "Clifford Brown, Art Farmer (trumpet) Ake Persson (trombone) Arne Domnerus (alto saxophone, clarinet) Lars Gullin (baritone saxophone) Bengt Hallberg (piano) Gunnar Johnson (bass) Jack Noren (drums) Quincy Jones (arranger, director)"

class AlbumPersonnel():

	def __init__(self, personnel_string):
		"""
		Recieve a string of personnel info for a given album and generate
		a list which has a sub-array for each artist. Each artist sub-array 
		has two further sub-arrays for that artist's name and instrument/track
		info.

		Once the various shorthand strategies employed in the initial personnel
		string have been corrected for, said list will be stored in
		self.final_arrays in __init__.   
		"""
		self.personnel_string = personnel_string	
		self._digits = re.compile('\d')
		self.artist_arrays = [] 
		self.final_arrays = []
		self.correct_problem_arrays()
	
	def initial_artist_arrays(self):
		"""
		Split personnel_string into words and return a list of arrays each
		containing an artist's name/s and associated instrument/track info.
		"""
		artist_arrays = []
		temp_array = []
		split_strings = self.personnel_string.split(")")
		for s in split_strings[:-1]: 	# leaves out extra empty item
			s += ")"					# replaces delimiter for later use
			temp_array = s.split()
			artist_arrays.append(temp_array)
		return artist_arrays

	def contains_digits(self, d):
		"""Return True if digits are present in a word (targets track info)."""
		return bool(self._digits.search(d))
	
	def partition_array_by_type(self, array):
		"""
		Recieve one of the artist arrays generated by initial_artist_arrays() and 
		return an array partitioned into two sub-arrays: 
		[[name], [instruments/tracks]].
		"""
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
		"""
		Call partition_array_by_type() on each array generated by calling
		initial_artist_arrays() and return a list of partitioned artist arrays.
		"""
		i_a_a = self.initial_artist_arrays()
		partitioned_arrays = []
		for a in i_a_a:
			partitioned_arrays.append(self.partition_array_by_type(a))
		return partitioned_arrays

	
# # # The Rogue-Array Correction Suite # # #
	
	# The following methods are called in correct_problem_arrays()

	def has_multiple_artists(self, array):
		"""
		Recieve the 'name' sub-array of a given artist array and return True
		if there appear to be multiple artists represented.
		"""
		multiple_artists = False
		for name in array:
			if name.endswith(","):
				multiple_artists = True
		return multiple_artists

	def multiple_artists_same_instrument(self, array):
		"""
		Recieve the 'name' sub-array of a given artist array and return a new
		array which contains a sub-array for each artist represented.

			Example:
				['Bobby', 'Byrne,', 'Jimmy', 'Cleveland'] becomes:
				[['Bobby', 'Byrne,'], ['Jimmy', 'Cleveland']]
		"""
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
		"""
		Recieve a single word from the 'instrument/track' sub-array of a given
		artist array and return True if that word indicates multiple ranges.
		"""
		multiple_range = False	
		for letter in word[:len(word) - 1]: # ignore trailing commas
				if letter == ",":
					multiple_range = True
		return multiple_range

	def mult_range_array(self, array):
		"""
		Recieve the 'instrument/track' sub-array of an artist array and return
		True if any of the words in that array indicate multiple ranges.
		"""
		multiple_range = False
		for inst in array:
			if self.has_mult_ranges(inst) and not self.contains_digits(inst):
				multiple_range = True
		return multiple_range

	def multiple_inst_ranges(self, array):
		"""
		Recieve the 'instrument/track' sub-array of an artist array and return
		a new array which unpacks the shorthand instrument notation from the
		initial personnel string into a new instrument item pairing each range
		with its base-instrument.

			Example:
				['soprano,alto,tenor', 'saxophone'] becomes:
				['soprano saxophone', 'alto saxophone', 'tenor saxophone'] 
		"""
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
		
	def has_mult_word_inst(self, array):
		"""
		Recieve the 'instrument/track' sub-array of an artist array and return
		True if a multiple-word instrument appears to be present.
		"""
		mult_name_inst = False
		for word in array:
			if not word.endswith(",") and not word.endswith(")") \
			and not self.contains_digits(word):
				mult_name_inst = True
		return mult_name_inst

	def multiple_word_instrument(self, array):
		"""
		Recieve the 'instrument/track' sub-array of an artist array and return
		a new array which combines the words of a multiple-word instrument
		into a single string.

			Example:
				['alto', 'saxophone'] becomes: ['alto saxophone']
		"""
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
		"""
		Apply methods from the 'Rogue-Array Correction Suite'.

		Call partitioned_arrays() to generate a list of partitioned arrays,
		test whether multiple_artists_same_instrument() or 
		multiple_inst_ranges() should be called to correct their 
		corresponding 'rogue' array issues and append the results to
		corrected_arrays.

		Test the contents of corrected_arrays to see if/when 
		multiple_word_instrument() needs to be called and append the results
		to self.final_arrays in __init__.
		"""
		p_a = self.partitioned_arrays()
		corrected_arrays = []
		for a in p_a:
			name = a[0]
			inst = a[1]
			# multiple artists
			if self.has_multiple_artists(name):
				m_a = self.multiple_artists_same_instrument(name)
				for artist in m_a:
					temp_array = []
					temp_array.append(artist)
					temp_array.append(inst)
					corrected_arrays.append(temp_array)
			# multiple range instruments
			elif self.mult_range_array(inst):
				temp_array = []
				inst = self.multiple_inst_ranges(inst)
				temp_array.append(name)
				temp_array.append(inst)
				corrected_arrays.append(temp_array)
			else:
				corrected_arrays.append(a)
		# multiple-word instruments
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


class AlbumArtist():

	def __init__(self, artist_array): 
		"""
		Recieve a single artist array from the list generated by the 
		AlbumPersonnel class and stored in its self.final_arrays attribute.

		Example:
		[['Jerome', 'Richardson'], ['(tenor saxophone,', 'flute', '-1,4/6)']]

		Generate a dictionary which has key:value pairings for every piece of
		name, instrument, and track info given in the artist array and store
		that dict in the attribute self.artist_dict in __init__.
		"""
		self.artist_array = artist_array
		self.names = artist_array[0]
		self.inst_track = artist_array[1]
		self._digits = re.compile('\d')
		self.artist_dict = {}
		self.create_artist_dict()

	def clean_word(self, w):
		"""
		Recieve a word (w) and return the word stripped of unnecessary
		characters.
		"""
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

	def contains_digits(self, d):
		"""Return True if digits are present in a word (targets track info)."""
		return bool(self._digits.search(d))

	#	#	#	Assign artist_dict Info 	#	#	#

		# may eventually need to deal with track-info shorthand
		#	ex: "1, 4/7" - the backslash implies "1, 4,5,6,7"

	def tracks_to_dict(self):
		"""
		Identify any track info in the 'inst_track' sub-array and assign a
		clean_word() version to self.artist_dict, then remove track info from
		the 'inst_track' sub-array leaving only instrument info.
		"""
		for i in self.inst_track:
			if self.contains_digits(i):
				self.artist_dict['tracks'] = self.clean_word(i)
				self.inst_track.remove(i)

	def instruments_to_dict(self):
		"""Assign instrument info to artist_dict."""
		n = 1
		for i in self.inst_track:
			key = "inst_" + str(n)
			self.artist_dict[key] = self.clean_word(self.clean_word(i)) # added comma protection
			n += 1

	def names_to_dict(self):
		"""Assign name info to artist_dict."""
		n = 1
		for i in self.names:
			key = "name_" + str(n)
			self.artist_dict[key] = self.clean_word(i)
			n += 1

	#	#	#	#	#	#	#	#	#	#	#	#

	def create_artist_dict(self):
		"""
		Generate the final artist dictionary by calling each of the
		artist_dict assignment functions.
		"""
		self.tracks_to_dict()
		self.instruments_to_dict()
		self.names_to_dict()


# Temporary Instantiation Test:

personnel = AlbumPersonnel(artists)
artist_dicts = []
for a in personnel.final_arrays:
	artist_dicts.append(AlbumArtist(a))
for a in artist_dicts:
	print a.artist_dict


# To Do:
	# - set this module up to automatically take in a personnel string and return
	#	 organized artist data in json format
