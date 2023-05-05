import click
import requests
import pandas as pd
import tqdm


def cross_pubchem(query):

    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{:s}/property/CanonicalSMILES,Title,MolecularFormula,IUPACName,Complexity/json?MaxRecords=5"
    r = requests.get(url.format(query))
    if r.status_code == 200:
        return r.json()['PropertyTable']['Properties']
    else:
        return None



@click.command()
@click.argument('MOLECULES_CSV', type=click.File('r'))
@click.argument('PUBCHEM_CSV', type=click.File('w'))
def run(molecules_csv, pubchem_csv):
    out = []
    molecules = pd.read_csv(molecules_csv)
    for k, mol in tqdm.tqdm(molecules.iterrows(), total=len(molecules)):
        m = cross_pubchem(mol.inchikey)
        if m is not None:
            out.append(
                dict(**m[0], **mol.to_dict())
            )

    pd.DataFrame.from_records(out).to_csv(pubchem_csv, index=None)

if __name__ == "__main__":
    run()