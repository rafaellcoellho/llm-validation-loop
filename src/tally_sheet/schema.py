from pydantic import BaseModel, Field


class Number(BaseModel):
    digits: int = Field(description="The value printed in the NRO. column")
    words: str = Field(description="The value spelled out in the Letras column")


class PartyVotes(BaseModel):
    party: str = Field(description="Party acronym from the Sigla column")
    votes: Number


class VoteSummary(BaseModel):
    total: Number = Field(description="Row 'Votos' of 'Resumen de votos'")
    valid: Number = Field(description="Row 'Votos validos'")
    null: Number = Field(description="Row 'Votos nulos'")
    blank: Number = Field(description="Row 'Votos vacios'")


class TallySheet(BaseModel):
    registered_voters: int = Field(description="Number before 'Electores'")
    voters_on_machine: Number = Field(description="'En la maquina de votacion'")
    parties: list[PartyVotes] = Field(description="All 38 party rows, in order")
    summary: VoteSummary
