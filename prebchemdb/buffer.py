import duckdb
from PIL import Image
from prebchemdb.depict import ReactionToImage, ReactionFromSmarts, MolFromSmiles, MolToImage, network_to_diagram


class ImageBuffer:

    def __init__(self, db_path, save_path) -> None:
        self.db_path = db_path
        self.save_path = save_path
        self.db = None

    def open_database(self):
        # It has its own class just in case I can handle exceptions here
        self.db = duckdb.connect(self.db_path)

    def close_database(self):
        # It has its own class just in case I can handle exceptions here
        self.db.close()

    def create_table(self, category):
        self.open_database()
        try:
            self.db.execute('CREATE TABLE {0} (id VARCHAR, path VARCHAR)'.format(category))
        except duckdb.CatalogException:
            pass
        self.close_database()

    def find_image(self, entry, category):
        self.open_database()
        u = self.db.execute(f"SELECT * FROM {category} WHERE id = '{entry}' ".format(category, entry))
        try:
            out = u.fetchone()[1]
            self.close_database()
        except TypeError:
            self.close_database()
            raise IOError(f"{entry} not found among {category}")
        
        return out
    
    def add_image(self, entry, extension, image, category):
        self.open_database()
        image.save(self.save_path + entry + extension)
        self.db.execute(f"INSERT INTO {category} VALUES ('{entry}', '{entry + extension}')")
        self.close_database()
        return self.save_path + entry + extension
    

    def generate_reaction_image(self, entry, smiles):
        try:
            u = self.find_image(entry, 'reactions')
        except IOError:
            image = ReactionToImage(ReactionFromSmarts(smiles, useSmiles=True), subImgSize=(600, 400))
            self.add_image(entry=entry, extension='.png', image=image, category='reactions')
            u = self.find_image(entry, 'reactions')
        return u

    def generate_molecule_image(self, entry, smiles):
        try:
            u = self.find_image(entry, 'molecules')
        except IOError:
            image = MolToImage(MolFromSmiles(smiles), subImgSize=(600, 400))
            self.add_image(entry=entry, extension='.png', image=image, category='molecules')
            u = self.find_image(entry, 'molecules')
        return u

    def generate_diagram(self, entry, reactions):
        try:
            u = self.find_image(entry, 'module_diagrams')
        except IOError:
            image = network_to_diagram(reactions)
            self.add_image(entry=entry, extension='.png', image=image, category='module_diagrams')
            u = self.find_image(entry, 'module_diagrams')
        return u
        