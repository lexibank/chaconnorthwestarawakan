from collections import defaultdict

from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset 
from pylexibank import Language, FormSpec
from pylexibank import progressbar

from clldutils.misc import slug
import attr

from pyedictor import fetch
from lingpy import Wordlist


@attr.s
class CustomLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default='Tukanoan')



class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "chaconnorthwestarawakan"
    language_class = CustomLanguage
    form_spec = FormSpec(
            missing_data=("–", "-")
            )

    def cmd_download(self, args):
        fetch("jcbancor", self.raw_dir / "jcbancor.tsv")

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        concepts = args.writer.add_concepts(
                id_factory=lambda x: x.id.split('-')[-1]+'_'+slug(x.english),
                lookup_factory='Name'
                )
        languages = args.writer.add_languages(
                lookup_factory='Name')
        sources = {s["Name"]: s["ID"] for s in self.etc_dir.read_csv("sources.tsv", delimiter="\t", dicts=True)}
        args.writer.add_sources()
        wl = Wordlist(self.raw_dir.joinpath("jcbancor.tsv").as_posix())
        for idx in wl:
            lex = args.writer.add_form(
                    Parameter_ID=concepts[wl[idx, "concept"]],
                    Language_ID=languages[wl[idx, "language"]],
                    Value=wl[idx, "value"].strip() or "?",
                    Form="_".join(
                        [{"_": "+", "#": '+'}.get(t, t) for t in wl[idx, "tokens"]]),
                    Cognacy=wl[idx, "cogid"],
                    Source=sources.get(wl[idx, "source"], "")
                    )
            args.writer.add_cognate(
                    lexeme=lex,
                    Cognateset_ID=wl[idx, "cogid"],
                    Alignment=wl[idx, "alignment"])


