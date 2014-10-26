# redesign 'artist-info-parser' with classes to make personell objects
import re

artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'
# artists = "Pharoah Sanders (tenor,soprano saxophone, bells, percussion) Michael White (violin, percussion) Lonnie Liston Smith (piano, electric piano, claves, percussion) Cecil McBee (bass, finger cymbals, percussion) Clifford Jarvis (drums, maracas, bells, percussion) James Jordan (ring cymbals -3)"

class AlbumPersonnel():

	def __init__(self, personnel_string):
		self.personnel_string = personnel_string	
		self._digits = re.compile('\d')
		self.artist_arrays = [] #append() formatted artist arrays here to send to AlbumArtist constructor
	
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
			if not word.endswith(",") and not word.endswith(")"):
				mult_name_inst = True
		return mult_name_inst

	def multiple_word_instrument(self, array):
		revised_array = []
		for word in array:
			a = array.index(word)
			b = a + 1
			if not word.endswith(",") and not word.endswith(")") \
				and not self.contains_digits(word):
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
		final_arrays = []
		for a in corrected_arrays:
			name = a[0]
			inst = a[1]
			if self.has_mult_word_inst(inst):
				temp_array = []
				inst = self.multiple_word_instrument(inst)
				temp_array.append(name)
				temp_array.append(inst)
				final_arrays.append(temp_array)
			else:
				final_arrays.append(a)
		return final_arrays


ex = AlbumPersonnel(artists)
for a in ex.correct_problem_arrays():
	print a, "\n"


class AlbumArtist(): # will this be a child of AlbumPersonnel?
	def __init__(self, artist_array):
		# takes a partitioned artist array
		# should probably call AlbumPersonnel in the init
		self.artist_array[0] = name
		self.artist_array[1] = instrument
		self.artist_array[2] = track # need to check if there IS track info

# Design:
	# make a class which creates a Personnel object out of the initial string
		# this is where each artist should be broken down into self-contained 
		#	arrays by inidividual
		# deals with fixing artist arrays so they will nicely work with Artist 
		#	objects and have methods to do so
		# split multiple artist per inst into multiple artist arrays
		# a good place to put functions regarding string-parsing by commas,
		#	parens, hyphens...

	# sub-class for individual artists
		# each artist object should have attributes for name/s, instrument/s, 
		# 	and track/s
		# this is probably where the clean_word function should come into effect

