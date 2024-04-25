import duckdb
import pandas as pd
from prebchemdb.schema_v2 import Molecule
from prebchemdb.utils import hash_molecule
from rdkit import Chem as chem
import numpy as np
import requests
import urllib


def query_pubchem(query, url):
    """
    This function aims to work as a placeholder to
    specific query functions (e.g. query name, query formula, etc)

    Parameters
    ----------
    query: str
        Term to look up
    url: str
        URL. It must have a single placeholder to place the query.
    """
    url = urllib.parse.quote(url.format(query), safe=':/,?=')
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()['PropertyTable']['Properties']
    else:
        return None


def query_pubchem_name(name):
    """
    Allows to retrieve molecules matching either a smiles, a formula or a name

    Parameters
    ---
    name: str
        Either a smiles, formula or name
    """
    urls = [
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{:s}/property/CanonicalSMILES,Title,MolecularFormula,IUPACName,InChI,InChIKey,MolecularWeight/json?MaxRecords=5",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/{:s}/property/CanonicalSMILES,Title,MolecularFormula,IUPACName,InChI,InChIKey,MolecularWeight/json?MaxRecords=5",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{:s}/property/CanonicalSMILES,Title,MolecularFormula,IUPACName,InChI,InChIKey,MolecularWeight/json?MaxRecords=5",
    ]
    for url in urls:

        u = query_pubchem(name, url)
        if u is not None:
            break
    
    out = []
    if u is None:
        return []
    for mol in u:
        try:
            out.append(Molecule(
                key=hash_molecule(chem.MolFromSmiles(mol['CanonicalSMILES'])),
                smiles=mol['CanonicalSMILES'],
                inchi=mol['InChI'], inchikey=mol['InChIKey'], title=mol['Title'].lower(),
                formula=mol['MolecularFormula'],
                cid=mol['CID'], mw=mol['MolecularWeight'],
            ))
        except KeyError:
            print("unable to process {:s} match".format(name))
            continue
    return out


class MolDB():
    def __init__(self, file=None):
        """

        A local DB to ease the upload and the annotation of data to the DB. Its role
        is to preserve a caché of molecule names, so servers like PubChem or KEGG don't have to
        be called too many times during the upload of the DB.
        
        Parameters
        ---

        file: path
            File where the database will be stored

        """
        self.file = file
        molecules_x = pd.read_json(file)
        self.db = duckdb.connect()
        
        self.db.execute("CREATE TABLE molecules AS SELECT * FROM molecules_x")
        # self.db = self.connect_mol_db(file)

    def close(self):
        """
        Allows to close the DB file after usage, enabling its usage by other processes
        """
        self.db.execute("SELECT * FROM molecules").df().to_json(self.file, indent=4, orient='records')

    def create_table(self):
        """
        Required to start using the DB, in case it hasn't been called before.
        """
        
        self.db.sql(
            """CREATE TABLE molecules (
                key STRING, smiles STRING, inchi STRING, inchikey STRING, title STRING, iupac_name STRING, cid INTEGER, 
                mw FLOAT, formula STRING, name STRING
            )"""
        )

    def connect_mol_db(self, file=None):
        if file is None:
            file = self.default_file

        return duckdb.connect(file)

    def query_name(self, name):
        """
        Query a molecule by its name, it returns the molecule
        corresponding to that match.
        """

        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE name == '{:s}'".format(name.lower())
        ).fetchdf().replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(name))
        
        
        return Molecule(
            **match
        )

    def query_inchikey(self, inchikey):
        """
        Query a molecule by its inchikey, it returns the molecule
        corresponding to that match.
        """

        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE inchikey == '{:s}'".format(inchikey)
        ).fetchdf().replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(inchikey))
        
        
        return Molecule(
            **match
        )

            
    def query_key(self, key):
        """
        Query a molecule by its key, it returns the molecule
        corresponding to that match.
        """
        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE key == '{:s}'".format(key)
        ).fetchdf().replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(key))
        
        
        return Molecule(
            **match
        )

        
    def add_name(self, name):
        """
        Adds a new entry corresponding to a given name
        """
        matches = query_pubchem_name(name)
        if len(matches) > 0:
            match = matches[0]

            self.db.sql(
                f"""
                INSERT INTO molecules (key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw, name) 
                    VALUES ('{match.key}', '{match.title}', '{match.cid}', '{match.inchikey}', '{match.iupac_name}', 
                    '{match.smiles}', '{match.formula}', '{match.inchi}', '{match.mw}', '{name.lower()}')
                """
            )
        else:
            raise ValueError("unable to find {:s}".format(name))
        