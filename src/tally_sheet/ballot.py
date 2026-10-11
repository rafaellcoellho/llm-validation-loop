CANDIDATE_PARTIES = (
    (
        "NICOLAS MADURO",
        ("PSUV", "PCV", "TUPAMARO", "PPT", "MSV", "PODEMOS", "MEP")
        + ("APC", "ORA", "UPV", "EV", "PVV", "PFV"),
    ),
    ("LUIS MARTINEZ", ("AD", "COPEI", "MR", "BR", "DDP", "UNE")),
    ("JAVIER BERTUCCI", ("EL CAMBIO",)),
    ("JOSE BRITO", ("PV", "VU", "UVV", "MPJ")),
    (
        "ANTONIO ECARRI",
        ("AP", "MOVEV", "CMC", "FV", "ALIANZA DEL LAPIZ", "MIN UNIDAD"),
    ),
    ("CLAUDIO FERMIN", ("SPV",)),
    ("DANIEL CEBALLOS", ("VPA", "AREPA")),
    ("EDMUNDO GONZALEZ", ("UNTC", "MPV", "MUD")),
    ("ENRIQUE MARQUEZ", ("CENTRADOS",)),
    ("BENJAMIN RAUSSEO", ("CONDE",)),
)

PARTIES = tuple(party for _, parties in CANDIDATE_PARTIES for party in parties)
