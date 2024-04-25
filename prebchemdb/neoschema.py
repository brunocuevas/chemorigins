from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, FloatProperty, ArrayProperty, RelationshipFrom, BooleanProperty, Relationship)


class Reactions(StructuredNode):
    """
    Reaction, defined as a smiles
    """
    test = BooleanProperty()
    role = StringProperty(choices=dict(reaction=None))
    key = StringProperty(unique_index=True, required=True)
    smiles = StringProperty(required=True)
    comments = StringProperty()
    similar_to = Relationship('Reactions', 'SIMILAR')


class Molecules(StructuredNode):
    """
    Molecule. Most fields are optional, to allow the input
    of molecules whose molecular description is not fully known
    (e.g "protein")
    """
    test = BooleanProperty()
    role = StringProperty(choices={'molecule':None})
    key = StringProperty(unique_index=True, required=True)
    hash = StringProperty(required=False)
    smiles = StringProperty()
    inchikey = StringProperty()
    inchi = StringProperty()
    title = StringProperty()
    iupac_name = StringProperty()
    cid = StringProperty()
    mw = FloatProperty()
    formula = StringProperty()
    comments = StringProperty()

    reacts_in = RelationshipTo(Reactions, 'REACTS_IN')
    reacts_out = RelationshipFrom(Reactions, 'REACTS_OUT')


class Conditions(StructuredNode):
    """
    Condition. It represents the environment at which 
    a reaction was detected. Note that our whole methodology
    rests on the annotation on conditions, from which the
    pipeline derives all the other data (e.g. reactions, molecules, etc)
    """
    role = StringProperty(choices={'conditions':None})
    key = StringProperty(unique_index=True, required=True)
    temperature = FloatProperty()
    pressure = FloatProperty()
    ph = FloatProperty()
    time = FloatProperty()
    source_file = StringProperty()
    test = BooleanProperty()
    describes = RelationshipTo(Reactions, 'DESCRIBES')


class Sources(StructuredNode):
    """
    Paper in which a reaction was reported.
    """
    role = StringProperty(choices={'sources':None})
    doi = StringProperty(unique_index=True, required=True)
    title = StringProperty()
    year = IntegerProperty()
    authors = StringProperty()
    journal = StringProperty()
    comments = StringProperty()
    test = BooleanProperty()
    reported = RelationshipTo(Conditions, 'REPORTED')

class Agents(StructuredNode):
    """
    Factors (e.g. molecules, cations, enzymes) that
    were required to catalyze a given chemical reaction under
    some conditions.
    """
    role = StringProperty(choices={'agent':None})
    key = StringProperty(unique_index=True, required=True)
    type = StringProperty(
        choices={
            'Mineral':None, 'Photon':None, 'Enzyme':None, 'Solute':None, 'Others':None
        }
    )
    smiles = StringProperty()
    name = StringProperty()
    test = BooleanProperty()
    comments = StringProperty()
    enables = RelationshipTo(Conditions, 'ENABLES')


class CrossRef(StructuredNode):
    """
    Codes relating our Molecules to Molecules from other
    databases.
    """
    role = StringProperty(choices={'crossref': None})
    type = StringProperty(
        choices={
            'kegg': None, 'pubchem': None
        }
    )
    link = StringProperty()
    crossref = StringProperty(unique_index=True, required=True)
    test = BooleanProperty()

    connects = RelationshipTo(Molecules, 'CONNECTS')


class PrebChemDBModule(StructuredNode):
    """
    PrebChemDBModule represents collections of reactions
    grouped for some reason (e.g. production of the same
    molecule, or sharing environmental conditions).
    """
    key = StringProperty(unique_index=True, required=True)
    role = StringProperty(choices={'module': None})
    link = StringProperty()
    description = StringProperty(required=True)
    name = StringProperty(required=True)

    connects = RelationshipTo(Reactions, 'INCLUDES')