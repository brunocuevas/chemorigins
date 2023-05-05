import streamlit as st
from pyArango.connection import *
from rdkit.Chem import rdChemReactions as rdr
from prebchemdb.schema import Reaction
from rdkit import Chem as chem
from rdkit.Chem import Draw as draw
from bcztools.pubchem import flexible_query
import pandas as pd
st.title('Prebchem')

def get_mol_identifier(mol: chem.rdchem.Mol):
    inchikey = chem.MolToInchiKey(mol)
    if inchikey == "":
        raise RuntimeError("couldn't generated identifier - {:s}".format(chem.MolToSmiles(mol)))
    if mol.GetNumHeavyAtoms() > 6:
        return 'mol-l-{:s}'.format(inchikey[:-2])
    else:
        return 'mol-s-{:s}'.format(inchikey)
    
def wrap_read_smiles(smiles):
    u = chem.MolFromSmiles(smiles)
    if u is None:
        raise RuntimeError("invalid smiles")
    else:
        return u

@st.cache_resource
def connect():
    conn = Connection(username="cuevaszuviri", password="fenzym-donna0-mYhsod")
    db = conn['pORD']
    return db

db = connect()

query = st.text_input('name a molecule!')


if st.button('look up'):
    try:
        u = wrap_read_smiles(query)
    except:
        _, u = flexible_query(query)
        u = chem.MolFromSmiles(u[0]['CanonicalSMILES'])
    

    id = get_mol_identifier(u)

    aql = f"""
        FOR molecule IN mainstage
            FILTER molecule.role == "molecule"
            FILTER molecule._key == @query
            FOR reaction, link_2 IN 1..1 OUTBOUND molecule mainstage_links
        RETURN reaction
        
    """
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=dict(
        query=id
    ))

    

    if len(queryResult) > 0:
        st.header('results')
        for result in queryResult:

            r = Reaction(**result)
            x = rdr.ReactionFromSmarts(r.smiles, useSmiles=True)
            st.subheader(r.key)
            st.dataframe(pd.DataFrame.from_records([r.dict()]).T, width=1200)
            st.image(draw.ReactionToImage(x))
    else:
        st.text('Sorry, we did not find any matching reaction')