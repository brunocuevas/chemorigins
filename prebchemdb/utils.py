from prebchemdb.schema import ReactionAnnotation, Reaction, Molecule
from prebchemdb.schema import ReactantLink, ProductLink
import rdkit.Chem.rdChemReactions as rdr
import rdkit.Chem as chem
import rdkit.Chem.AllChem as achem
import hashlib
import base64
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')



def hash_molecule(mol: chem.rdchem.Mol):
    """
    Provides a modified InChIKey identifier that preserves all the details in
    small molecules and neglects charge-protonation in larger molecules
    """
    mol = chem.Mol(mol)
    chem.RemoveStereochemistry(mol)
    inchikey = chem.MolToInchiKey(mol)
    if inchikey == "":
        raise RuntimeError("couldn't generated identifier - {:s}".format(chem.MolToSmiles(mol)))
    if mol.GetNumHeavyAtoms() > 6:
        return 'mol-l-{:s}'.format(inchikey[:-2])
    else:
        return 'mol-s-{:s}'.format(inchikey)
    
def hash_reaction(reaction: rdr.ChemicalReaction):
    """
    Generates a hash out of a chemical reaction in order to recognize
    their identity regardless of the SMILES employed

    """
    reactants = reaction.GetReactants()
    products = reaction.GetProducts()

    reactant_identifiers = list(map(hash_molecule, reactants))
    product_identifiers = list(map(hash_molecule, products))

    merged_ids = ','.join(sorted(reactant_identifiers)) + '->' + ','.join(sorted(product_identifiers))
    hasher = hashlib.sha1(merged_ids.encode('utf-8')).digest()[:12]
    new_key = 'rxn-' + base64.urlsafe_b64encode(hasher).decode('utf-8')
    return new_key


def neutralize_atoms(mol: chem.rdchem.Mol):
    """
    copied from 
    https://www.rdkit.org/docs/Cookbook.html
    
    """
    pattern = chem.MolFromSmarts("[+1!h0!$([*]~[-1,-2,-3,-4]),-1!$([*]~[+1,+2,+3,+4])]")
    at_matches = mol.GetSubstructMatches(pattern)
    at_matches_list = [y[0] for y in at_matches]
    if len(at_matches_list) > 0:
        for at_idx in at_matches_list:
            atom = mol.GetAtomWithIdx(at_idx)
            chg = atom.GetFormalCharge()
            hcount = atom.GetTotalNumHs()
            atom.SetFormalCharge(0)
            atom.SetNumExplicitHs(hcount - chg)
            atom.UpdatePropertyCache()
    return mol