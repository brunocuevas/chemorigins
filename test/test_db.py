import unittest
from prebchemdb.schema import ReactionAnnotation
import arango
import json

class TestSchema(unittest.TestCase):

    def test_upload(self):
        db = arango.ArangoClient(
            hosts='http://localhost:8529'
        ).db(
            'pORD', username='cuevaszuviri', password="fenzym-donna0-mYhsod"
        )

        try:
            db.delete_collection('test')
        except:
            pass

        test_collection = db.create_collection('test')

        with open('test/test_data.json') as f:
            test_data = json.load(f)

        for annotation in map(lambda x: ReactionAnnotation(** x), test_data):
            test_collection.insert(annotation.dict())


        u = db.aql.execute('FOR u IN test RETURN u')
        self.assertEqual(len(list(u)), len(test_data))