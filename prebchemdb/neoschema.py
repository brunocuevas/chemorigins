from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, FloatProperty, ArrayProperty, RelationshipFrom, BooleanProperty)


class Reactions(StructuredNode):
    test = BooleanProperty()
    role = StringProperty(choices=dict(reaction=None))
    key = StringProperty(unique_index=True, required=True)
    smiles = StringProperty(required=True)
    comments = StringProperty()


class Molecules(StructuredNode):
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
