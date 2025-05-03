import streamlit as st
from prebchemdb.ai import query_text, MoleculeBuffer
from prebchemdb.format import convert_to_legacy_annotation, branch, publication_metadata, wrap
import rdkit.Chem as chem 
import rdkit.Chem.rdChemReactions as rdr
import rdkit.Chem.Draw as draw
import yaml
from yaml.loader import SafeLoader
import os
# from git import Repo

def clean_annotation(i):
    st.session_state['annotations'].pop(i)



LOCAL_DIR = os.getcwd() + '/data/'

# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)
# with open('secrets.yaml') as file:
#     tokkens = yaml.load(file, Loader=SafeLoader)


st.title("PrebChemDB - Annotation tool")

"""
Hi there! Wellcome to PrebChemDB, developped with ❤️ by
Bruno Cuevas-Zuviría. The goal of this app is to ease the 
annotation of prebiotic chemistry literature. For this goal,
we are combining some AI tool with some query/retrieval
systems and automating the creation of branches. In other
words, we are trying to make your experience smoother!
"""


st.warning(
"""
At this time, the project is depending on personal funds. As
we are using AI computing units (with their economic and environmental
cost), we maintain this app open for suscribed users only. **How to suscribe?**
For now, just send me a mail to brunocuevaszuviria at proton.me.
"""
)


# if not config['git_started']:

#     tokken = tokkens['github_tokken']
#     repo_url = f'https://{tokken}:x-oauth-basic@github.com/brunocuevas/test-prebchemdb-data.git'
#     # repo = Repo.clone_from(repo_url, LOCAL_DIR)
#     config['git_started'] = True
#     with open('config.yaml', 'w') as file:
#         yaml.dump(config, file)



# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['pre-authorized'], 
# )

button_container = st.container(border=True)


# if st.session_state['authentication_status']:
#     # authenticator.logout()
#     pass
    
# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
#     st.stop()
# elif st.session_state['authentication_status'] is None:
#     name, authentication_status, username = authenticator.login()
#     st.stop()



side = st.sidebar

side.header("How to use it?")

side.write(
"""
It's easy:
1. Write down a text piece where you describe information about the experiment
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
5. Whenever you are ready, just click submit. We will hanlde the rest.

**We hope that you enjoy it!**
"""
)

if 'annotations' not in st.session_state:
    st.session_state['annotations'] = [
    ]

if 'current-id' not in st.session_state:
    st.session_state['current-id'] = 0


@st.cache_resource
def load_molecule_buffer():
    mdb = MoleculeBuffer(file='buffer.db')
    mdb.create_table(overwrite=False)
    return mdb

mdb = load_molecule_buffer()




if button_container.button('compile', type="primary"):
    annotations = list(map(convert_to_legacy_annotation, st.session_state['annotations']))
    branch_name = branch(annotations, LOCAL_DIR)

    st.info(f"Congratulations! Your branch was pushed as {branch_name}")
    st.balloons()

new_annotation = {

}
cont = st.container(border=True)
new_annotation['text'] = cont.text_area(
    label="Write here the information that you want to annotate", 
    key="content", max_chars=1000, 
    value="After 12h at 90C, Pyruvate reacted with ... "
)
new_annotation['doi'] = cont.text_input("doi", value="")
new_annotation['id'] = '{:03d}'.format(st.session_state['current-id'] + 1)
st.session_state['current-id'] += 1
if cont.button('submit') and new_annotation['doi'] != "":
    pub = publication_metadata(new_annotation['doi'])
    u = query_text(new_annotation['text'], openai_api_key=tokkens['openai_tokken'])
    new_annotation['digest'] = u
    new_annotation['pub'] = pub
    st.write(u)
    try:
        new_annotation['reaction_string'] = mdb.create_reaction_smiles(u['reactants'], u['products'])
        st.session_state['annotations'].append(new_annotation)
    except TypeError:
        st.error("We are having trouble to process this entry")
    except KeyError:
        st.error("We are having trouble to process this entry")
    

for i, annotation in enumerate(st.session_state['annotations']):

    cont = st.container(border=True)
    col1, col2 = cont.columns([0.85, 0.15])
    col1.header("Annotation: " + annotation['id'])
    col2.button(label="Remove", key="remove-{0}".format(annotation['id']), on_click=clean_annotation, args=[i])
    cont.subheader("Request")
    cont.code(wrap(annotation['text'], length=60), language=None)
    cont.subheader("Digest")
    cont.write(annotation['digest'])
    cont.subheader("Publication")
    cont.write(annotation['pub'])
    cont.subheader("Reaction Image")
    reaction_rdkit = rdr.ReactionFromSmarts(
        annotation['reaction_string'], useSmiles=True
    )
    cont.image(draw.ReactionToImage(reaction_rdkit))
    
    
        