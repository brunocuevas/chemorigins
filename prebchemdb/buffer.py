import sqlite3
from PIL import Image
from prebchemdb.depict import ReactionToImage, ReactionFromSmarts, MolFromSmiles, MolToImage, network_to_diagram


class ImageBuffer:

    def __init__(self, db_path, save_path) -> None:
        self.db_path = db_path
        self.save_path = save_path
        self.conn = None

    def open_database(self):
        # Open a connection to the SQLite database
        self.conn = sqlite3.connect(self.db_path)

    def close_database(self):
        # Close the SQLite database connection
        if self.conn:
            self.conn.close()

    def create_table(self, category):
        self.open_database()
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {category} (id TEXT PRIMARY KEY, path TEXT)')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table {category}: {e}")
        finally:
            self.close_database()

    def find_image(self, entry, category):
        self.open_database()
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT path FROM {category} WHERE id = ?", (entry,))
            result = cursor.fetchone()
            if result is None:
                raise IOError(f"{entry} not found among {category}")
            return result[0]
        finally:
            self.close_database()

    def add_image(self, entry, extension, image, category):
        self.open_database()
        try:
            # image_path = self.save_path + entry + extension
            image_path = self.save_path + entry + extension
            image.save(image_path)
            cursor = self.conn.cursor()
            cursor.execute(f"INSERT INTO {category} (id, path) VALUES (?, ?)", (entry, entry + extension))
            self.conn.commit()
            return image_path
        except sqlite3.Error as e:
            print(f"Error adding image {entry} to {category}: {e}")
        finally:
            self.close_database()

    def generate_reaction_image(self, entry, smiles):
        try:
            return self.find_image(entry, 'reactions')
        except IOError:
            image = ReactionToImage(ReactionFromSmarts(smiles, useSmiles=True), subImgSize=(600, 400))
            self.add_image(entry=entry, extension='.png', image=image, category='reactions')
            return self.find_image(entry, 'reactions')

    def generate_molecule_image(self, entry, smiles):
        try:
            return self.find_image(entry, 'molecules')
        except IOError:
            image = MolToImage(MolFromSmiles(smiles), subImgSize=(600, 400))
            self.add_image(entry=entry, extension='.png', image=image, category='molecules')
            return self.find_image(entry, 'molecules')

    def generate_diagram(self, entry, reactions):
        try:
            return self.find_image(entry, 'module_diagrams')
        except IOError:
            image = network_to_diagram(reactions)
            self.add_image(entry=entry, extension='.png', image=image, category='module_diagrams')
            return self.find_image(entry, 'module_diagrams')
