import streamlit as st
from pyArango.connection import *
from rdkit.Chem import rdChemReactions as rdr
from prebchemdb.schema import Reaction
from rdkit import Chem as chem
from rdkit.Chem import Draw as draw
from bcztools.pubchem import flexible_query
import pandas as pd

st.title('Prebchem - Explore')

def report(result):
    db.AQLQuery(
        'UPDATE { _key: @key, reported: True } IN mainstage', rawResults=True, 
        bindVars=dict(key=result['_key'])
    )

@st.cache_resource
def connect():
    conn = Connection(username="cuevaszuviri", password="fenzym-donna0-mYhsod")
    db = conn['pORD']
    return db

db = connect()
@st.cache_resource
def imfeelingluck():
    aql = f"""
        FOR reaction IN mainstage
            SORT RAND()
            FILTER reaction.role == "reaction"
            LIMIT 10
            RETURN reaction
    """
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100)
    return queryResult


queryResult = imfeelingluck()
if len(queryResult) > 0:
    st.header('results')
    for i, result in enumerate(queryResult):

        r = Reaction(**result)
        x = rdr.ReactionFromSmarts(r.smiles, useSmiles=True)
        st.subheader(r.key)
        st.dataframe(pd.DataFrame.from_records([r.dict()]).T, width=1200)
        st.image(draw.ReactionToImage(x))
        st.button('report', key='report_{:06d}'.format(i), on_click=lambda : report(result))
            
else:
    st.text('Sorry, we did not find any matching reaction')