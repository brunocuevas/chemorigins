from pydantic import BaseModel, PositiveInt
from typing import Literal, Any
from datetime import date

class ReactionAnnotation(BaseModel):
    """
    Class to store raw notes about chemical reaction networks. 
    Later processing of this data can turn the chemical
    reaction annotations into database items (reactions, molecules,
    sources, agents, etc)
    """
    source: str
    smiles: str
    date_: date | None = None
    # email: EmailStr = None 
    crossref: list[str] = []
    comments: str = ""
    primary: str = ""
    key: str = ""
    conditions: list[str] = []
    agents: list[str] = []
    waste: list[str] = []
    attributes: list[Any] = []
    class Config:
        fields = {'key':'_key'}


class Reaction(BaseModel):
    """
    Class aimed to check 
    """
    role: str = "reaction"
    key: str
    smiles: str
    crossref: list[str] = []
    comments: str = ""
    attributes: list[Any] = []
    class Config:
        fields = {'key':'_key'}

class Molecule(BaseModel):
    role: str = "molecule"
    key: str
    smiles: str
    inchi: str
    inchikey: str
    title: str | None = None 
    iupac_name: str | None = None
    cid: int | None = None
    mw: float | None = None
    formula: str | None = None
    attributes: list[Any] = []
    class Config:
        fields = {'key':'_key'}

class Conditions(BaseModel):
    key: str
    annotation: str
    role: str = "conditions"
    source: str
    temperature: float | None = None
    pressure: float | None = None
    ph: float | None = None
    time: float | None = None
    agents: list[str] = []
    waste: list[str] = []
    light: str | None = None
    
    class Config:
        fields = {'key':'_key'}

class Source(BaseModel):
    doi: str
    title: str
    year: int
    authors: list[str] = []
    tag: str | None = None
    keywords: list[str] = []


class ReactantLink(BaseModel):
    from_: str
    to_: str
    role: str = 'reactant'
    n: PositiveInt
    class Config:
        fields = {'from_': '_from', 'to_':'_to'}


class ProductLink(BaseModel):
    from_: str
    to_: str
    role: str = 'product'
    n: PositiveInt
    class Config:
        fields = {'from_': '_from', 'to_':'_to'}


class ReactionConditionsLink(BaseModel):
    from_: str
    to_: str
    role: str = 'described in'
    class Config:
        fields = {'from_': '_from', 'to_':'_to'}