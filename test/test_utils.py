import unittest
from prebchemdb.utils import hash_reaction, hash_molecule, neutralize_atoms
from rdkit.Chem.rdChemReactions import ReactionFromSmarts
from rdkit.Chem import MolFromSmiles, MolToInchiKey



class TestUtils(unittest.TestCase):

    def test_hash_reaction(self):
        ReactionFromSmiles = lambda x: ReactionFromSmarts(x, useSmiles=True)
        r1 = ReactionFromSmiles('CCN.O>>CCO.N')
        r3 = ReactionFromSmiles('NCC.O>>CCO.N')
        r2 = ReactionFromSmiles('NCC.O>>OCC.N')
        rx = ReactionFromSmiles('NCC.O>>NCOC')
        r2p = ReactionFromSmiles('OCC.N>>NCC.O')
        
        h1 = hash_reaction(r1)
        h2 = hash_reaction(r2)
        h3 = hash_reaction(r3)
        h2p = hash_reaction(r2p)
        hx = hash_reaction(rx)
        
        self.assertEqual(h1, h2)
        self.assertEqual(h2, h3)
        self.assertEqual(h1, h3)
        self.assertNotEqual(h2p, h2)
        self.assertNotEqual(hx, h1)

    def test_hash_reaction_charge(self):
        ReactionFromSmiles = lambda x: ReactionFromSmarts(x, useSmiles=True)
        ra = ReactionFromSmiles('CCCCCCCCC(=O)O.N>>CCCCCCC.O')
        rb = ReactionFromSmiles('CCCCCCCCC(=O)[O-].N>>CCCCCCC.O')
        rc = ReactionFromSmiles('CCCCCCCCC(=O)[O-].[NH4+]>>CCCCCCC.O')

        ha = hash_reaction(ra)
        hb = hash_reaction(rb)
        hc = hash_reaction(rc)

        self.assertEqual(ha, hb)
        self.assertNotEqual(ha, hc)

    def test_hash_molecule_small(self):

        m1 = MolFromSmiles('CCO')
        m2 = MolFromSmiles('OCC')
        m3 = MolFromSmiles('COC')

        h1 = hash_molecule(m1)
        h2 = hash_molecule(m2)
        h3 = hash_molecule(m3)

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)

        m1 = MolFromSmiles('N')
        m2 = MolFromSmiles('[NH4+]')
        m3 = MolFromSmiles('[NH2]')

        h1 = hash_molecule(m1)
        h2 = hash_molecule(m2)
        h3 = hash_molecule(m3)

        self.assertNotEqual(h1, h2)
        self.assertNotEqual(h1, h3)

    def test_hash_molecule_large(self):

        m1 = MolFromSmiles('CCCCCCO')
        m2 = MolFromSmiles('OCCCCCC')
        m3 = MolFromSmiles('OCCCCCO')

        h1 = hash_molecule(m1)
        h2 = hash_molecule(m2)
        h3 = hash_molecule(m3)

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)

        m1 = MolFromSmiles('NCCCCC(=O)O')
        m2 = MolFromSmiles('NCCCCC(=O)[O-]')
        m3 = MolFromSmiles('[NH3+]CCCCC(=O)O')
        m4 = MolFromSmiles('[NH3+]CCCCC(=O)[O-]')

        h1 = hash_molecule(m1)
        h2 = hash_molecule(m2)
        h3 = hash_molecule(m3)
        h4 = hash_molecule(m4)

        self.assertEqual(h1, h2)
        self.assertEqual(h1, h3)
        self.assertEqual(h1, h4)

    def test_charge_neutralization(self):

        test_cases = [

            ('[O-]P(=O)([O-])[O-]', '[O-]P(=O)([O-])O'),
            ('[O-]P(=O)([O-])[O-]', '[O-]P(=O)(O)O'),
            ('[O-]P(=O)([O-])[O-]', 'OP(=O)(O)O'),
            ('C#N', '[C-]#N'),
            ('C(C(=O)[O-])C(CC(=O)[O-])(C(=O)[O-])O', 'C(C(=O)[O-])C(CC(=O)[O-])(C(=O)O)O'),
            ('C(C(=O)[O-])C(CC(=O)[O-])(C(=O)[O-])O', 'C(C(=O)O)C(CC(=O)[O-])(C(=O)O)O'),
            ('[NH4+]', 'N')
        ]

        fail_cases = [
            ('[OH]', '[OH-]'),
            ('[Fe]', '[Fe+3]')
        ]

        for sx, sy in test_cases:

            x = MolFromSmiles(sx)
            y = MolFromSmiles(sy)

            y = neutralize_atoms(y)
            x = neutralize_atoms(x)
            
            xh = MolToInchiKey(x)
            yh = MolToInchiKey(y)
            self.assertEqual(xh, yh, msg=f'{sx} {sy}')

        for sx, sy in fail_cases:

            x = MolFromSmiles(sx)
            y = MolFromSmiles(sy)

            y = neutralize_atoms(y)
            x = neutralize_atoms(x)
            
            xh = MolToInchiKey(x)
            yh = MolToInchiKey(y)
            self.assertNotEqual(xh, yh, msg=f'{sx} {sy}')

        

if __name__ == "__main__":

    unittest.main()