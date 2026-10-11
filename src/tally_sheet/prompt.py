from tally_sheet.ballot import CANDIDATE_PARTIES

SOURCES = {
    "vision": "three overlapping image crops, from top to bottom, of the sheet",
    "ocr": "the OCR text of the sheet, one printed line per text line",
}

READING_GUIDANCE = {
    "vision": "Copy both exactly as printed.",
    "ocr": (
        "The OCR text has recognition errors: misspelled words such as 'Caro' "
        "for 'Cero', or digits that were dropped or misread. Return what the "
        "sheet actually says: write the words as correct Spanish digit words, "
        "and use digits, words and totals to recover each printed value."
    ),
}


def build_prompt(source):
    return f"""\
You are reading an "Acta de escrutinio" from the 2024 Venezuelan presidential
election. You are given {SOURCES[source]}.

Extract into the JSON schema:
- registered_voters: the number printed before "Electores".
- voters_on_machine: the row "En la maquina de votacion" of the "Votantes" table.
- parties: every party row, in the printed order. Each row has the columns
  Sigla, Codigo, NRO. and Letras. Votes are the NRO. column and its Letras.
  The Codigo column is a fixed party code, never votes.
- summary: rows "Votos", "Votos validos", "Votos nulos" and "Votos vacios" of
  "Resumen de votos".

Every number appears twice: as digits (NRO.) and spelled out in Spanish, one
word per digit (Letras, e.g. "Cero, Dos, Cinco, Tres" for 253).
{READING_GUIDANCE[source]}

Use the party acronyms exactly as listed here, grouped by candidate:
{_ballot_listing()}
"""


def _ballot_listing():
    return "\n".join(
        f"- {candidate}: {', '.join(parties)}"
        for candidate, parties in CANDIDATE_PARTIES
    )
