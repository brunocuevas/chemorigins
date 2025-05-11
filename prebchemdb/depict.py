from rdkit.Chem.Draw import ReactionToImage, MolToImage
from rdkit.Chem.rdChemReactions import ReactionFromSmarts
from rdkit.Chem import MolFromSmiles
from io import BytesIO
import requests
from PIL import Image
import base64
import os

def reaction_smiles_to_base64(smiles):
    buff = BytesIO()
    image = ReactionToImage(ReactionFromSmarts(smiles, useSmiles=True), subImgSize=(600, 400))
    image.save(buff, format="PNG")
    img_str = base64.b64encode(buff.getvalue())
    img_str = img_str.decode("utf-8")  # convert to str and cut b'' chars
    return img_str

def molecule_smiles_to_base64(smiles):
    buff = BytesIO()
    image = MolToImage(MolFromSmiles(smiles), subImgSize=(600, 400))
    image.save(buff, format="PNG")
    img_str = base64.b64encode(buff.getvalue())
    img_str = img_str.decode("utf-8")  # convert to str and cut b'' chars
    return img_str

def network_to_diagram(reactions):
    """

    reactions should be a list with entries with exactly the same format as provided by _all_reaction_info
    """
    graph = """graph TB;\n"""

    for reaction in reactions:

        for mol in reaction['reactants']:
            graph += '  {0}["{1}"] --> {2};\n'.format(mol['key'], mol['title'], reaction['reaction']['key'])
        for mol in reaction['products']:
            graph += '  {2} --> {0}["{1}"];\n'.format(mol['key'], mol['title'], reaction['reaction']['key'])

    print(graph)
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    # img_data = Image.open()
    url = os.environ['MERMAID_ENDPOINT'] + base64_string
    print(url)
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    return img
