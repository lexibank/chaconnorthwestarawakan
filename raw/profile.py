from lingpy import *
from collections import defaultdict
from pyclts import CLTS

bipa = CLTS().bipa
wl = Wordlist("jcbancor.tsv")

prof = defaultdict(int)
for idx in wl:
    for segment in wl[idx, 'tokens']:
        sound = bipa[segment]
        if sound.type != "unknownsound" and sound.type != "marker":
            sound_s = sound.s
        else:
            sound_s = "!"+segment
        prof[segment, sound_s] += 1
with open("../etc/orthography.tsv", "w") as f:
    f.write("Grapheme\tIPA\tFrequency\n")
    for seg, snd in sorted(prof, key=lambda x: prof[x], reverse=True):
        f.write("{0}\t{1}\t{2}\n".format(seg, snd, prof[seg, snd]))
