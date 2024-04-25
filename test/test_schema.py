import unittest
from prebchemdb.schema_v2 import Reaction, Molecule, ReactionAnnotation, ReactantLink, Source


class TestSchema(unittest.TestCase):

    def test_schema(self):

        m1 = Molecule(
            key='m1',
            smiles="O", inchi="asadasd",
            inchikey="asdasada"
        )

        m2 = Molecule(
            key='m2',
            smiles="CC", inchi="asadasd",
            inchikey="asdasada"
        )

        m3 = Molecule(
            key='m3',
            smiles="OO", inchi="asadasd",
            inchikey="asdasada"
        )

        m4 = Molecule(
            key='m4',
            smiles="OCO", inchi="asadasd",
            inchikey="asdasada"
        )


        r = Reaction(
            key='asdads',
            curated=False,
            smiles='O.CC>>OO.OCO',
            source="",
            comments="jeje"
        )

        s = Source(
            doi="10.1126/sciadv.abj3984",
            title="Quantifying structural relationships of metal-binding sites suggests origins of biological electron transfer",
            tag="biochemistry", keywords=["journal article", "Science"],
            year=2022, authors=["Bromberg, Yana", "Arial Asda"]

        )

        print("hello!")

    def test_annotation(self):

        a = ReactionAnnotation(
            smiles='CC.O>>O.CC',
            agents=["water"],
            source="manual"
        )
        self.assertEqual(a.smiles, 'CC.O>>O.CC')
        print("foo!")

    def test_link(self):

        l = ReactantLink(from_="foo", to_="bar", n=10)
        print("hello!")


if __name__ == "__main__":
    unittest.main()