import streamlit as st
from streamlit_tags import st_tags
from prebchemdb.ai import query_text, MoleculeBuffer
from prebchemdb.format import branch, publication_metadata, wrap
import rdkit.Chem as chem 
import rdkit.Chem.rdChemReactions as rdr
import rdkit.Chem.Draw as draw
import yaml
from yaml.loader import SafeLoader
from datetime import date
import os
import json


def convert_to_legacy_annotation(annotation):

    conditions = []
    if annotation['temperature'] is not None:
        conditions.append("T={0}".format(annotation['temperature']))

    if annotation['yield'] is not None:
        conditions.append("yield={0}".format(annotation['yield']))

    if annotation['pH'] is not None:
        conditions.append("pH={0}".format(annotation['pH']))

    if annotation['time'] is not None:
        conditions.append("time={0}".format(annotation['time']))

    if annotation['wavelength'] is not None:
        conditions.append("wl={0}".format(annotation['wavelength']))


    l_annotation = {
        "agents": annotation['agents'],
        "attributes": "",
        "comments": "",
        "conditions": conditions,
        "crossref": [],
        "date_": date.today().isoformat(),
        "key": date.today().isoformat() + ":" + annotation['id'],
        "primary": annotation['reaction'],
        "smiles": annotation['reaction'],
        "source": annotation['doi'],
        "waste": []
    }
    return l_annotation




def clean_annotation(i):
    st.session_state['annotations'].pop(i)


LOCAL_DIR = os.getcwd() + '/data/'

# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)


st.title("PrebChemDB - Annotation tool")

"""
Hi there! Wellcome to PrebChemDB, developped with ❤️ by
Bruno Cuevas-Zuviría. The goal of this app is to ease the 
annotation of prebiotic chemistry literature.
"""





side = st.sidebar
button_container = side.container(border=True)


if 'annotations' not in st.session_state:
    st.session_state['annotations'] = [
    ]

if 'current-id' not in st.session_state:
    st.session_state['current-id'] = 0


@st.cache_resource
def load_molecule_buffer():
    mdb = MoleculeBuffer(file='annotation.buffer.db')
    mdb.create_table(overwrite=False)
    return mdb

mdb = load_molecule_buffer()




if button_container.button('compile', type="primary"):
    annotations = list(map(convert_to_legacy_annotation, st.session_state['annotations']))
    # branch_name = branch(annotations, LOCAL_DIR)
    with open(LOCAL_DIR + "/annotations." + date.today().isoformat() + ".json", 'w') as f:
        json.dump(annotations, f, indent=4)
    
    # st.info(f"Congratulations! Your branch was pushed as {branch_name}")
    st.balloons()

new_annotation = {

}
with st.container(border=True):

    st.subheader("Reaction")
    st.markdown("If you have trouble writing the chemical smiles, try online editors such as `molview`")

    new_annotation['reaction'] = st.text_area(
        label="Write here the reaction in SMILES", 
        key="reaction",
        value="OCCC#N.S>>OCCC(N)=S"
    )
    st.subheader("Publication")
    st.markdown("All submissions must have a DOI")
    new_annotation['doi'] = st.text_input(label="Publication doi", value="", key="doi")


    st.subheader("Conditions")
    new_annotation['agents'] = st.text_input(label="agents(catalysts, light sources, etc)", value="", key="agents")
    if st.checkbox(label="Do you know the temperature at which the reaction was carried out?", key='known_temperature', value=False):
        new_annotation['temperature'] = st.slider(label="temperature ºC", min_value=0, max_value=200, value=25)
    else:
        new_annotation['temperature'] = None
    if st.checkbox(label="Do you know the pH at which the reaction was carried out?", key='known_pH', value=False):
        new_annotation['pH'] = st.slider(label="pH", min_value=0.0, max_value=14.0, value=7.0)
    else:
        new_annotation['pH'] = None
    if st.checkbox(label="Do you know the pressure at which the reaction was carried out?", key='known_pressure', value=False):
        new_annotation['pressure'] = st.slider(label="Pressure (atm)", min_value=0.9, max_value=5.0, value=1.0)
    else:
        new_annotation['pressure'] = None
    if st.checkbox(label="Do you know the reaction yield?", key='known_yield', value=False):
        new_annotation['yield'] = st.slider(label="yield (atm)", min_value=0.0, max_value=100.0, value=50.0)
    else:
        new_annotation['yield'] = None
    if st.checkbox(label="Do you know the time where products were measured?", key='known_time', value=False):
        new_annotation['time'] = st.slider(label="time (h)", min_value=0.0, max_value=120.0, value=24.0)
    else:
        new_annotation['time'] = None

    if st.checkbox(label="Do you know the wavelength?", key='known_wavelength', value=False):
        new_annotation['wavelength'] = st.slider(label="nm", min_value=100.0, max_value=640.0, value=600.0)
    else:
        new_annotation['wavelength'] = None


    new_annotation['attributes'] = st.text_area(label="Additional attributes (this can be helpful for later curation)", value="")

    new_annotation['id'] = '{:03d}'.format(st.session_state['current-id'] + 1)


    st.session_state['current-id'] += 1
    if st.button('submit') and new_annotation['doi'] != "":
        pub = publication_metadata(new_annotation['doi'])
        st.session_state['annotations'].append(new_annotation)
        

for i, annotation in enumerate(st.session_state['annotations']):

    with side.container(border=True):
        col1, col2 = st.columns([0.7, 0.3])
        col1.header("Annotation: " + annotation['id'])
        col2.button(label="Remove", key="remove-{0}".format(annotation['id']), on_click=clean_annotation, args=[i])
        st.write(annotation)
        reaction_rdkit = rdr.ReactionFromSmarts(
            annotation['reaction'], useSmiles=True
        )
        st.image(draw.ReactionToImage(reaction_rdkit))
    
    
st.header("How to use it?")

st.write(
"""
It's easy:
1. Fill the different fields of the form
(e.g. the molecules involved, the time, the yield, the temperature).
2. **Very important**: Include a doi. We will verify whether the DOI exists before
doing anything. At this point, we only want data backed by publications.
3. Hit "Process". A couple scenarios can take place:
    - Your request is processed, in which case you will recover a JSON dictionary
    with the details extracted from your reaction, a chemical reaction diagram, and a
    dictionary with the publication data.
    - Your request fails, in which case you will recover an error. 
4. You can keep processing entries, and deleting those that didn't work out (NOTE: 
at this point we don't have a way to edit previous submissions).
5. Whenever you are ready, just click compile in the side bar. We will hanlde the rest.

**We hope that you enjoy it!**
"""
)

