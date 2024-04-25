import unittest
from prebchemdb.local_mol_db import MolDB
from prebchemdb.utils import hash_molecule
from rdkit.Chem import MolFromSmiles, MolToInchiKey
import json
import os

class TestLocalMolDB(unittest.TestCase):

    def test_db_creation(self):
        
        mdb = MolDB('test/test_local_mol_db.json')
        # mdb.create_table()


    def test_db_insertion(self):

        mdb = MolDB(file='/mnt/researchdrive/bCuevas/apps/prebchemdb/test/test_local_mol_db.json')
        # try:   
        #     mdb.create_table()
        # except:
        #     pass
        n = len(mdb.db.execute('SELECT * FROM molecules').df())
        try:
            u = mdb.query_name('pyruvic acid')
        except ValueError:
            mdb.add_name('pyruvic acid')
            u = mdb.query_name('pyruvic acid')

        self.assertEqual(u.cid, 1060)

        u = mdb.query_name('pyruvic acid')

        self.assertEqual(u.cid, 1060)
        
        mdb.close()

        with open('/mnt/researchdrive/bCuevas/apps/prebchemdb/test/test_local_mol_db.json') as f:
            u = json.load(f)
        
        print("")
        self.assertEqual(2, len(u))
        




    def test_cases(self):

        mdb = MolDB(file='/mnt/researchdrive/bCuevas/apps/prebchemdb/test/test_local_mol_db.json')
        try:   
            mdb.create_table()
        except:
            pass
        try:
            u = mdb.query_name('HCN')
        except ValueError:
            mdb.add_name('HCN')
            u = mdb.query_name('HCN')
    
        u = mdb.query_name('HCN')
    

    def test_db_key(self):
        mdb = MolDB(file='/mnt/researchdrive/bCuevas/apps/prebchemdb/test/test_local_mol_db.json')

        try:   
            mdb.create_table()
        except:
            pass

        u = MolFromSmiles('C#N')
        key1 = hash_molecule(u)

        mdb.add_name('C#N')
        v = mdb.query_key(key1)
        key2 = hash_molecule(MolFromSmiles(v.smiles))
        self.assertEqual(key1, key2)

    def test_db_inchikey(self):
        mdb = MolDB(file='/mnt/researchdrive/bCuevas/apps/prebchemdb/test/test_local_mol_db.json')

        try:   
            mdb.create_table()
        except:
            pass

        u = MolFromSmiles('C#N')
        u_inchikey = MolToInchiKey(u)
        mdb.add_name('C#N')
        result = mdb.query_inchikey(u_inchikey)
        
        self.assertEqual(u_inchikey, result.inchikey)



if __name__ == '__main__':
    unittest.main()
