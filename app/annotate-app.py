import streamlit as st
from prebchemdb.reann import process_reaction
from prebchemdb.schema import ReactionAnnotation
from pyArango.connection import *
import pandas as pd
import rdkit.Chem as chem 
import rdkit.Chem.rdChemReactions as rdr
import rdkit.Chem.Draw as draw
import pandas as pd

@st.cache_resource
def connect_db():
    conn = Connection(username="cuevaszuviri", password="fenzym-donna0-mYhsod")
    db = conn["pORD"]
    return db['staging']

db = connect_db()

header = st.container()
header.title('PrebChemDB - Annotation tool')
header_col1, header_col2 = header.columns(2)

if 'current_reaction' not in st.session_state:
    st.session_state['u'] = None

if 'current_reaction' not in st.session_state:
    st.session_state['smiles'] = ""

def query(payload):
    response = process_reaction(payload)
    return response

def get_text():
    reaction = st.text_input("Reaction", key="current_reaction")
    
    agents = st.text_area("Agents", key="current_agents")
    conditions = st.text_area("Conditions", key="current_conditions")
    publication = st.text_input("Publication", key="current_publication")
    
    return reaction, conditions, agents, publication


def plot_reaction():

    reaction_rdkit = rdr.ReactionFromSmarts(
        st.session_state['smiles'], useSmiles=True
    )
    placeholder1.image(draw.ReactionToImage(reaction_rdkit))
    placeholder2.text_area("Reaction Smiles", key='smiles', on_change=plot_reaction)


reaction, conditions, agents, source = get_text()
u = None
if header_col1.button('process', key='process'):
    reaction_smiles = query(reaction)
    st.session_state['smiles'] = reaction_smiles
    placeholder1 = st.empty()
    placeholder2 = st.empty()
    plot_reaction()
    st.session_state['u'] = ReactionAnnotation(
        primary=reaction,
        smiles=reaction_smiles, 
        conditions=[conditions],
        source=source,
        agents=[agents]
    )


if header_col2.button('upload', key='download') and st.session_state['u'] is not None:
    
    doc = db.createDocument()
    doc.set(st.session_state['u'].dict())
    doc.save()

    st.write(st.session_state['u'].dict())