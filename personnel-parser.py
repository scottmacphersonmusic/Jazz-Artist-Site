# redesign 'artist-info-parser' with classes to make personell objects
import re

artists = "Nat Adderley (cornet -1,2,4/6) Donald Byrd (trumpet -1,2,4,5) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute -1,4/6) Horace Silver (piano) Paul Chambers (bass) Kenny Clarke (drums)"
# artists = 'Nat Adderley (cornet) Ernie Royal (trumpet) Bobby Byrne, Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Danny Bank (baritone saxophone) Junior Mance (piano) Keter Betts (bass) Charles "Specs" Wright (drums)'
# artists = "Pharoah Sanders (tenor,soprano saxophone, bells, percussion) Michael White (violin, percussion) Lonnie Liston Smith (piano, electric piano, claves, percussion) Cecil McBee (bass, finger cymbals, percussion) Clifford Jarvis (drums, maracas, bells, percussion) James Jordan (ring cymbals -3)"

class AlbumPersonnel():
	
	def __init__(self, personnel_string):
		self.personnel_string = personnel_string	

	def initial_artist_arrays(self):
	# should result in a list of artist lists
		artist_arrays = []
		temp_array = []
		split_strings = self.personnel_string.split(")")
		for s in split_strings[:-1]: 	# leaves out extra empty item
			s += ")"				# replaces delimiter for later use
			temp_array = s.split()
			artist_arrays.append(temp_array)
		return artist_arrays
	
	


ex = AlbumPersonnel(artists)

for a in ex.initial_artist_arrays():
	print a, "\n"



class AlbumArtist(AlbumPersonnel):
	def __init__(self, name, instrument, track):
		# should probably call AlbumPersonnel in the init
		self.name = name
		self.instrument = instrument
		self.track = track

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

