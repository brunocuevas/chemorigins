import duckdb
import pandas as pd
from bcztools.pubchem import query_pubchem
from prebchemdb.schema_v2 import Molecule
from prebchemdb.utils import hash_molecule
from rdkit import Chem as chem
import numpy as np

def query_pubchem_name(name):
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
                _key=hash_molecule(chem.MolFromSmiles(mol['CanonicalSMILES'])),
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
    # default_file = '/home/bcz/.local/share/prebchemdb/local_mold.db'
    def __init__(self, file=None):
        self.file = file
        molecules = pd.read_json(file)
        self.db = duckdb.connect()
        self.db.execute("CREATE TABLE molecules AS SELECT * FROM molecules")
        # self.db = self.connect_mol_db(file)

    def close(self):
        self.db.execute("SELECT * FROM molecules").df().to_json(self.file, indent=4, orient='records')

    def create_table(self):
        
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

        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE name == '{:s}'".format(name.lower())
        ).fetchdf().rename(columns={"key":"_key"}).replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(name))
        
        
        return Molecule(
            **match
        )

    def query_inchikey(self, inchikey):

        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE inchikey == '{:s}'".format(inchikey)
        ).fetchdf().rename(columns={"key":"_key"}).replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(inchikey))
        
        
        return Molecule(
            **match
        )

            
    def query_key(self, key):
        match = self.db.query(
            "SELECT key, title, cid, inchikey, iupac_name, smiles, formula, inchi, mw FROM molecules WHERE key == '{:s}'".format(key)
        ).fetchdf().rename(columns={"key":"_key"}).replace(np.nan, None)

        try:
            match = match.loc[0].to_dict()
        except KeyError:
            raise ValueError("unable to find {:s}".format(key))
        
        
        return Molecule(
            **match
        )

        
    def add_name(self, name):
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
        