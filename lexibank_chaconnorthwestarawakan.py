import attr
from collections import defaultdict

from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset 
from pylexibank import Language, FormSpec

from clldutils.misc import slug
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

    def cmd_download(self, _):
        print("updating ...")
        with open(self.raw_dir.joinpath("jcbancor.tsv"), "w", encoding="utf-8") as f:
            f.write(
                fetch(
                    "jcbancor",
                    columns=[
                        "DOCULECT",
                        "CONCEPT",
                        "VALUE",
                        "TOKENS",
                        "LANGID",
                        "COGID",
                        "ALIGNMENT",
                        "CONCEPT_PORTUGUESE",
                        "CONCEPTICON_ID",
                        "CONCEPT_ORIGINAL_LISTS",
                        "SOURCE"
                    ],
                )
            )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        concepts = args.writer.add_concepts(
                id_factory=lambda x: x.id.split('-')[-1]+'_'+slug(x.english),
                lookup_factory='Name'
                )

        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
            args.writer.add_concept(
                ID=idx,
                Name=concept.english,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss
            )
            concepts[concept.english] = idx

        args.log.info("added concepts")

        languages = args.writer.add_languages(lookup_factory='Name')

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
                    Alignment=wl[idx, "alignment"]
                    )
