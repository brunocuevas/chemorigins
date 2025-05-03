from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from typing import List
import requests
import urllib
import duckdb
import pandas as pd




class Paragraph(BaseModel):
    temperature: float | None = Field(description="temperature at which the reaction took place in Celsius. null if not specified")
    pH: float | None = Field(description="pH at which the reaction took place. null if not specified")
    yield_: float | None = Field(description="percent of the expected product produced. null if not specified")
    time: float | None = Field(description="time in hours at which the products were measured. null if not specified")
    reactants: List[str] | None = Field(description="list of molecule names acting as reactants. null if not specified")
    products: List[str] | None = Field(description="list of molecule names acting as products. null if not specified")
    agents: List[str] | None  = Field(description="list of molecules acting as agents. null if not specified")


def load_model(openai_api_key):

    model = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o")
    parser = PydanticOutputParser(pydantic_object=Paragraph)
    prompt = PromptTemplate(
        template='Extract the following information from this paragraph\n{format_instructions}\n{query}\n',
        input_variables=['query'],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    prompt_and_model = prompt | model
    return prompt_and_model, parser


def query_text(text, openai_api_key):
    prompt_and_model, parser = load_model(openai_api_key)
    digest = prompt_and_model.invoke(
        {'query': text}
    )
    return parser.invoke(digest).dict()



class MoleculeBuffer:

    def __init__(self, file, openai_api_key=None) -> None:
        """
        MoleculeBuffer allows to ease the annotation of chemical
        reaction networks by providing and storing annotations
        for molecules.

        **WARNING: We do not recommend yet the use of OpenAI for this task**

        """
        self.file = file
        self.openai_api_key = openai_api_key

    def __transaction__(self, u):
        
        with duckdb.connect(self.file) as con:
            try:
                return con.sql(u).fetchall()
            except:
                return []
        # self.db = duckdb.connect(file)
    
    def create_table(self, overwrite=True):
        if overwrite:
            try:
                self.__transaction__("DROP TABLE molecules")
                
            except duckdb.duckdb.CatalogException:
                pass

        self.__transaction__(
            """
            CREATE TABLE molecules (
                title STRING, smiles STRING
            )
            """
        )
            

        
    def __qmol(self, name):
        matches = self.__transaction__(
            """
            SELECT title, smiles  FROM molecules WHERE title == '{:s}'
            """.format(name)
        )
        return [dict(
            title=u[0], smiles=u[1]
        ) for u in matches]
        
    
    def query(self, q):
        """
        Queries must be specified using SMILES. MoleculeBuffer
        hands everything else
        """
        
        u = self.__qmol(q)
    
        if len(u) == 0:
            u = self.query_pubchem(q)
            if len(u) > 0:
                for match in u:
                    self.__transaction__(
                        f"""
                        INSERT INTO molecules (title, smiles)
                            VALUES ('{match['title']}', '{match['smiles']}')
                        """
                    )
                u = self.__qmol(q)
            else:
                mu = self.make_up(q)
                if mu is not None:
                    self.__transaction__(
                            f"""
                            INSERT INTO molecules (title, smiles)
                                VALUES ('{q}', '{mu}')
                            """
                        )
                    u = self.__qmol(q)
                else:
                    u = [{"title": q, "smiles": ""}]
        
        return u


    @staticmethod
    def query_pubchem(name):
        """
        

        Parameters
        ----------
        name: str
            Smiles
        url: str
            URL. It must have a single placeholder to place the query.
        """
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{:s}/property/CanonicalSMILES/json?MaxRecords=1"
        url = urllib.parse.quote(url.format(name), safe=':/,?=')
        r = requests.get(url)
        out = []
        if r.status_code == 200:
            matches = r.json()['PropertyTable']['Properties']
            for mol in matches:
                try:
                    out.append(dict(
                        smiles=mol['CanonicalSMILES'],
                        title=name
                    ))
                except KeyError:
                    print("unable to process {:s} match".format(name))
                    continue
        else:
            return []
        return out
 

    def create_reaction_smiles(self, reactants, products):
        reactants = [self.query(mol)[0] for mol in reactants]
        products = [self.query(mol)[0] for mol in products]
        reactants = [mol['smiles'] for mol in reactants if mol['smiles'] != ""]
        products = [mol['smiles'] for mol in products if mol['smiles'] != ""]

        return '.'.join(reactants) + '>>' + '.'.join(products)


    def make_up(self, name):
        if self.openai_api_key is None:
            return ""
        else:
            model = ChatOpenAI(openai_api_key=self.openai_api_key, model_name="gpt-4o")
            message = [
                ("system", "Convert the following molecule to SMILES. Please, be very concise"),
                ("human", name),
            ]

            digest = model.invoke(
                message
            )
        return digest.content