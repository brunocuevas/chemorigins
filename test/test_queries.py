import unittest
from prebchemdb.retrieve import _reactions_from_molecule, _all_reaction_info, _all_agent_info, _all_source_info# , Reactions, Molecules, 
from prebchemdb.retrieve import _obtain_module, _all_molecule_info, _new_search_function
from prebchemdb.neoschema import Reactions, Molecules
from neomodel import config
import os


config.DATABASE_URL = "neo4j+s://neo4j:" + os.environ['NEO4J_KEY'] + "@" + os.environ['NEO4J_URL']  # default


class TestQueries(unittest.TestCase):

    def test_queryreactions(self):

        r = Reactions.nodes.get(key='pbr-000001')
        self.assertEqual(r.key, 'pbr-000001')


    def test_querymolecules(self):

        r = Molecules.nodes.get(key='pbm-000170')
        self.assertEqual(r.key, 'pbm-000170')

    def test_query_reactions_from_molecule(self):

        r = _reactions_from_molecule(query='pbm-000542')
        self.assertEqual(1, 1)

    def test_query_all_reaction_info(self):

        r = _all_reaction_info(query='pbr-000292')
        self.assertEqual(1, 1)

    def test_query_all_condition_info(self):

        r = _all_agent_info(query='pbg-000001')
        self.assertEqual(1, 1)

    def test_query_all_molecule_info(self):

        r = _all_molecule_info(query='pbm-000542')
        self.assertEqual(1, 1)

    def test_query_all_source_info(self):

        r = _all_source_info(query='10.1038/s41559-020-1125-6')
        self.assertEqual(1, 1)

    def test_query_module(self):

        r = _obtain_module('pbmdl-000001')
        self.assertEqual(1, 1)

    def test_new_search(self):

        u = _new_search_function('pbm-000226')
        self.assertEqual(1, 1)



if __name__ == '__main__':
    unittest.main()