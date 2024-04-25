import unittest
from prebchemdb.buffer import ImageBuffer
from prebchemdb.depict import ReactionFromSmarts, ReactionToImage
from prebchemdb.retrieve import PrebChemDBModule, _all_reaction_info


class TestBuffer(unittest.TestCase):

    def test_buffer(self):

        bfi = ImageBuffer('test/testdb.db', 'test/images/')
        bfi.create_table('reactions')

        image = ReactionToImage(
            ReactionFromSmarts('CCCC>>CCC.C', useSmiles=True), subImgSize=(600, 400)
        )
        bfi.add_image(entry='r01', extension='.png', image=image, category='reactions')
        x = bfi.find_image('r01', 'reactions')
        self.assertEqual(x, 'r01.png')
        

        try:
            x = bfi.find_image('r02', 'reactions')
        except IOError:
            image = ReactionToImage(
                ReactionFromSmarts('CCCCN>>CCC.CN', useSmiles=True), subImgSize=(600, 400)
            )
            bfi.add_image(entry='r02', extension='.png', image=image, category='reactions')
            x = bfi.find_image('r02', 'reactions')
            self.assertEqual(x, 'r02.png')

    def test_buffer_reaction(self):

        bfi = ImageBuffer('test/testdb.db', 'test/images/')
        bfi.create_table('reactions')
        u = bfi.generate_reaction_image('r01', 'CCCC>>CCC.C')
        self.assertEqual('r01.png', u)
        
        u = bfi.generate_reaction_image('r07', 'CCCC.N>>CCC.CN')
        self.assertEqual('r07.png', u)

    def test_buffer_molecule(self):

        bfi = ImageBuffer('test/testdb.db', 'test/images/')
        bfi.create_table('molecules')

        u = bfi.generate_molecule_image('m01', 'CCCN')
        self.assertEqual('m01.png', u)
        
        u = bfi.generate_molecule_image('m02', 'C#N')
        self.assertEqual('m02.png', u)

    def test_buffer_diagram(self):

        bfi = ImageBuffer('test/testdb.db', 'test/images/')
        bfi.create_table('module_diagrams')
        module = 'pbmdl-000001'
        module = PrebChemDBModule.nodes.get(key=module)
        reactions = module.connects.all()
        reactions=[_all_reaction_info(r.key) for r in reactions]
        u = bfi.generate_diagram(entry=module.key, reactions=reactions)
        self.assertEqual(module.key + '.png', u)


if __name__ == "__main__":
    unittest.main()