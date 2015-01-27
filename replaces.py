# deal with personnel strings that use 'replaces' with multiple artists

import personnelparser

p_s = "Johnny Coles, Louis Mucci, Ernie Royal (trumpet) Joe Bennett, Tom Mitchell, Frank Rehak (trombone) Julius Watkins (French horn) Harvey Phillips (tuba) Cannonball Adderley (alto saxophone) Jerry Sanfino (reeds) Gil Evans (piano, arranger, conductor) Chuck Wayne (guitar) Paul Chambers (bass) Art Blakey (drums)"
# p_s = "Lee Morgan (trumpet) Curtis Fuller (trombone) Herbie Mann (flute, piccolo) Cannonball Adderley (alto saxophone) Benny Golson (tenor saxophone) Sahib Shihab (baritone saxophone) Wynton Kelly (piano) Jimmy Garrison (bass) Philly Joe Jones (drums)"
# p_s = "Lee Morgan (trumpet) Bobbi Humphrey (flute) Billy Harper (tenor saxophone) George Devens (vibraphone, marimba, percussion) Hank Jones (piano, electric piano) Gene Bertoncini (guitar) George Duvivier (bass) Idris Muhammad (drums) Ray Armando (congas) Wade Marcus (arranger)"
# p_s = "Cannonball Adderley (alto saxophone) Junior Mance (piano) Dinah Washington (vocals) unidentified orchestra, Hal Mooney (arranger, conductor)"
# p_s = "Nat Adderley (cornet) Jimmy Cleveland (trombone) Cannonball Adderley (alto saxophone) Jerome Richardson (tenor saxophone, flute) Cecil Payne (baritone saxophone) John Williams (piano) Paul Chambers (bass) Kenny Clarke (drums) Quincy Jones (arranger)"

ex = "Bill Barber (tuba) Phil Bodner (reeds) Philly Joe Jones (drums) \
replaces Phillips, Sanfino, Blakey"
# ex = "Blue Mitchell (trumpet) Sam Jones (bass) replaces Mann, Garrison"
# ex = "Frank Owens (piano, electric piano) Gordon Edwards (electric bass) Jimmy Johnson (drums) replaces Jones, Duvivier, Muhammad"
# ex = "Bill Barber (tuba) replaces Phillips"
# ex = "unidentified orchestra, including strings replaces unidentified orchestra"
# ex = "J.J. Johnson (trombone) replaces Cleveland"
# ex = "Max Roach (drums) replaces Clarke"
# ex

class ReplacePersonnel():

        def __init__(self, original_personnel, replacement_personnel):
                self.original_personnel = original_personnel
                self.replacement_personnel = replacement_personnel

        def split_replaces(self, replacement_personnel):
                subs_targets = replacement_personnel.split('replaces')
                subs, targets = subs_targets[0], subs_targets[1]
                return subs, targets

        def split_subs(self, subs):
                if ")" in subs:
                        split_subs = subs.split(')')
                        full_subs = [word + ")" for word in split_subs[:(len(split_subs) - 1)]]
                        return full_subs
                else:
                        return [subs]

        def split_targets(self, targets):
                split_targets = targets.split(',')
                clean_targets = [word.strip() for word in split_targets]
                for i in clean_targets:
                        if " " in i:
                                index = clean_targets.index(i)
                                split = i.split()
                                clean_targets[index] = split
                return clean_targets

        def create_sub_target_tuples(self, subs, targets):
                sub_dicts = []
                for sub in subs:
                        if ')' in sub:
                                sub_dicts.append(personnelparser.album_artists(sub)[0])
                        elif type(sub) == str:    # really just looking for 'unidentified's here
                                split_string = sub.split()
                                counter = 1
                                odd_dict = {}
                                for word in split_string:
                                        key = "odd_" + str(counter)
                                        odd_dict[key] = word
                                        counter += 1
                                sub_dicts.append(odd_dict)
                        else:
                                print "Something peculiar is going on here..."
                #sub_dicts = [personnelparser.album_artists(sub)[0] for sub in subs]
                sub_target_tuples = []
                index = 0
                for sub in sub_dicts:
                        sub_target_tuples.append((sub, targets[index]))
                        index += 1
                return sub_target_tuples

        def replace_artists(self, sub_target_tuples, original_personnel):
                for t in sub_target_tuples:
                        if type(t[1]) == str:
                                for d in original_personnel:
                                        if t[1] in d.values():
                                                original_personnel.remove(d)
                                                original_personnel.append(t[0])
                        elif type(t[1]) == list:
                                for d in original_personnel:
                                        if t[1][0] in d.values():
                                                original_personnel.remove(d)
                                                original_personnel.append(t[0])



                return original_personnel

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


# r_a = ReplacePersonnel(personnelparser.album_artists(p_s), ex)
# print r_a.build_replacement_personnel()

# print "Original Personnel:", "\n"

# for d in r_a.original_personnel:
#       print d, "\n"


# print "Replacement Personnel:", "\n"

# for d in r_a.build_replacement_personnel():
#       print d, "\n"

# print personnelparser.album_artists(ex)



# print "Let's check it out: ", "\n"
# subs, targets = r_a.split_replaces(ex)
# print "Subs: ", subs
# print "Targets: ", targets, "\n"
# split_subs = r_a.split_subs(subs)
# print "Split Subs: ", split_subs, "\n"
# split_targets = r_a.split_targets(targets)
# print "Split Targets: ", split_targets, "\n"
# sub_target_tuples = r_a.create_sub_target_tuples(split_subs, split_targets)
# print "Sub, Target Tuples: ", sub_target_tuples, "\n"

# print "Original Personnel:", "\n"
# for d in personnelparser.album_artists(p_s):
#       print d, "\n"
# print "Revised Personnel:", "\n"
# for d in replace_artists(sub_target_tuples, p_s):
#       print d, "\n"
