from pydantic import BaseModel, PositiveInt
from typing import Literal, Any

class ReactionAnnotation(BaseModel):
    source: str
    smiles: str
    agents: list[str] = []
    waste: list[str] = []
    conditions: list[str] = []
    crossref: list[str] = []
    comments: str = ""
    primary: str = ""
    attributes: list[Any] = []
    curated: bool = False
    curated_by: str = ""
    key: str = ""
    class Config:
        fields = {'key':'_key'}

class Reaction(BaseModel):
    """
    Class aimed to check 
    """
    role: str = "reaction"
    key: str
    curated: bool = False
    source: str
    smiles: str
    curated_by: str | None = None
    temperature: float | None = None
    pressure: float | None = None
    ph: float | None = None
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
    mw: float | None = None
    class Config:
        fields = {'key':'_key'}

class Agent(BaseModel):
    id: str
    type: Literal['radiation', 'catalyst', 'disolvent']
    smiles: str | None
    attributes: list[Any]


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

class ReactionAnnotationLink(BaseModel):
    from_: str
    to_: str
    role: str = 'generated_from'
    class Config:
        fields = {'from_': '_from', 'to_':'_to'}

class AgentLink(BaseModel):
    agent: str
    reaction: str

class ReactionCollection(BaseModel):
    reactions: list[Reaction]

class MoleculeCollection(BaseModel):
    molecules: list[Molecule]

class AgentCollection(BaseModel):
    agents: list[Agent]

class MoleculeLinkCollection(BaseModel):
    reactants: list[ReactantLink]
    products: list[ProductLink]

class AgentLinkCollection(BaseModel):
    links: list[AgentLink]

class ReactionAnnotationCollection(BaseModel):
    annotation: list[ReactionAnnotation] = []

class ReactionAnnotationLinkCollection(BaseModel):
    links: list[ReactionAnnotationLink] = []
