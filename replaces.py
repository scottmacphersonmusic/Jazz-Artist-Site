# deal with personnel strings that use 'replaces' with multiple artists
	
import personnelparser

p_s = "Johnny Coles, Louis Mucci, Ernie Royal (trumpet) Joe Bennett, Tom Mitchell, Frank Rehak (trombone) Julius Watkins (French horn) Harvey Phillips (tuba) Cannonball Adderley (alto saxophone) Jerry Sanfino (reeds) Gil Evans (piano, arranger, conductor) Chuck Wayne (guitar) Paul Chambers (bass) Art Blakey (drums)"
# p_s = "Lee Morgan (trumpet) Curtis Fuller (trombone) Herbie Mann (flute, piccolo) Cannonball Adderley (alto saxophone) Benny Golson (tenor saxophone) Sahib Shihab (baritone saxophone) Wynton Kelly (piano) Jimmy Garrison (bass) Philly Joe Jones (drums)"
# p_s = "Lee Morgan (trumpet) Bobbi Humphrey (flute) Billy Harper (tenor saxophone) George Devens (vibraphone, marimba, percussion) Hank Jones (piano, electric piano) Gene Bertoncini (guitar) George Duvivier (bass) Idris Muhammad (drums) Ray Armando (congas) Wade Marcus (arranger)"

ex = "Bill Barber (tuba) Phil Bodner (reeds) Philly Joe Jones (drums) \
replaces Phillips, Sanfino, Blakey"
# ex = "Blue Mitchell (trumpet) Sam Jones (bass) replaces Mann, Garrison"
# ex = "Frank Owens (piano, electric piano) Gordon Edwards (electric bass) Jimmy Johnson (drums) replaces Jones, Duvivier, Muhammad"
# ex = "Bill Barber (tuba) replaces Phillips"

class replace_personnel():

	def __init__(self, original_personnel, replacement_personnel):
		self.original_personnel = personnelparser.album_artists(original_personnel)
		self.replacement_personnel = replacement_personnel

	def split_replaces(self, replacement_personnel):
		subs_targets = replacement_personnel.split('replaces')
		subs, targets = subs_targets[0], subs_targets[1]
		return subs, targets

	def split_subs(self, subs):
		split_subs = subs.split(')')
		full_subs = [word + ")" for word in split_subs[:(len(split_subs) - 1)]]
		return full_subs

	def split_targets(self, targets):
		split_targets = targets.split(',')
		clean_targets = [word.strip() for word in split_targets]
		return clean_targets

	def create_sub_target_tuples(self, subs, targets):
		sub_dicts = [personnelparser.album_artists(sub)[0] for sub in subs]
		sub_target_tuples = []
		index = 0
		for sub in sub_dicts:
			sub_target_tuples.append((sub, targets[index]))
			index += 1
		return sub_target_tuples

	def replace_artists(self, sub_target_tuples, original_personnel):
		# original_personnel = personnelparser.album_artists(original_personnel)
		for t in sub_target_tuples:
			for d in original_personnel:
				if t[1] in d.values():
					original_personnel.remove(d)
					original_personnel.append(t[0])
		return original_personnel

	# write another function to call the necessary functions and return the revised personnel
	def build_replacement_personnel(self):
		"""
		Call all of the functions necessary to produce a list of dicts of
		replacement personnel.
		"""
		subs, targets = self.split_replaces(self.replacement_personnel)
		full_subs = self.split_subs(subs)
		clean_targets = self.split_targets(targets)
		sub_target_tuples = self.create_sub_target_tuples(full_subs, clean_targets)
		replace_artists = self.replace_artists(sub_target_tuples, self.original_personnel)
		return replace_artists


r_a = replace_personnel(p_s, ex)

print "Original Personnel:", "\n"

for d in r_a.original_personnel:
	print d, "\n"

print "Replacement Personnel:", "\n"

for d in r_a.build_replacement_personnel():
	print d, "\n"



# subs, targets = split_replaces(ex)
# split_subs = split_subs(subs)
# split_targets = split_targets(targets)
# sub_target_tuples = create_sub_target_tuples(split_subs, split_targets)

# print "Original Personnel:", "\n"
# for d in personnelparser.album_artists(p_s):
# 	print d, "\n"
# print "Revised Personnel:", "\n"
# for d in replace_artists(sub_target_tuples, p_s):
# 	print d, "\n"
	
