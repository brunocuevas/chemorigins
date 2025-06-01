from rdkit.Chem.rdChemReactions import ReactionFromSmarts
from rdkit.Chem import MolFromSmiles, MolToInchiKey
from prebchemdb.depict import reaction_smiles_to_base64, molecule_smiles_to_base64, network_to_diagram
from prebchemdb.buffer import ImageBuffer
from neomodel import db
from prebchemdb.neoschema import Reactions, Molecules, Conditions, Agents, Sources, PrebChemDBModule
import os
import time
import logging



def create_image_buffer(path):
    ibf = ImageBuffer(
        db_path = path + '/image-buffer.db',
        save_path = path 
    )
    ibf.create_table('reactions')
    ibf.create_table('module_diagrams')
    ibf.create_table('molecules')
    return ibf

ibf = create_image_buffer(os.environ['PREBCHEMDB_IMAGE_BUFFER'])

def _reactions_from_molecule(query):
    molecule = Molecules.nodes.get(key=query)
    
    reactant_in = db.cypher_query(
        """
        MATCH (reactant: Molecules {key:$key})-[r:REACTS_IN]->(x:Reactions) RETURN x
        """, {"key": molecule.key}, resolve_objects=True
    )

    product_in = db.cypher_query(
        """
        MATCH (product: Molecules {key:$key})<-[r:REACTS_OUT]-(x:Reactions) RETURN x
        """, {"key": molecule.key}, resolve_objects=True
    )
    
    crossrefs = db.cypher_query(
        """
        MATCH (m: Molecules {key:$key})<-[:CONNECTS]-(x:CrossRef) RETURN x
        """, {"key": molecule.key}, resolve_objects=True
    )

    modules = db.cypher_query(
        """
        MATCH (x:Molecules {key: $key})<-[]->(r:Reactions)<-[:INCLUDES]-(m:PrebChemDBModule) RETURN m
        """, {"key": molecule.key}, resolve_objects=True
    )

    image = ibf.generate_molecule_image(entry=molecule.key, smiles=molecule.smiles)
    # image = molecule_smiles_to_base64(molecule.smiles)

    context = {
        'molecule': molecule.__properties__,
        'img': image,
        'crossrefs': [item[0].__properties__ for item in crossrefs[0]],
        'reactant_in': [item[0].__properties__ for item in reactant_in[0]],
        'product_in': [item[0].__properties__ for item in product_in[0]],
        'involved_in': [item[0].__properties__['key'] for item in reactant_in[0]] + [item[0].__properties__['key'] for item in product_in[0]],
        'modules': [item[0].__properties__ for item in modules[0]]
    }
    return context

def _all_reaction_info(query, include_images=True):
    reaction = Reactions.nodes.get(key=query)
    
    reactants = db.cypher_query(
        """
        MATCH (reactant: Molecules)-[r:REACTS_IN]->(x:Reactions {key:$key}) RETURN reactant
        """, {"key": reaction.key}, resolve_objects=True
    )

    products = db.cypher_query(
        """
        MATCH (product: Molecules)<-[r:REACTS_OUT]-(x:Reactions {key:$key}) RETURN product
        """, {"key": reaction.key}, resolve_objects=True
    )

    conditions = db.cypher_query(
        """
        MATCH (c:Conditions)-[r:DESCRIBES]->(x:Reactions {key:$key}) RETURN c
        """,{"key": reaction.key}, resolve_objects=True
    )

    modules = db.cypher_query(
        """
        MATCH (r:Reactions {key: $key})<-[:INCLUDES]-(m:PrebChemDBModule) RETURN m
        """, {"key": reaction.key}, resolve_objects=True
    )
    
    context = {
        'reaction': reaction.__properties__,
        'img': ibf.generate_reaction_image(entry=reaction.key, smiles=reaction.smiles),
        'reactants': [item[0].__properties__ for item in reactants[0]],
        'products': [item[0].__properties__ for item in products[0]],
        'conditions': [_expand_condition(item[0].__properties__) for item in conditions[0]],
        'modules': [item[0].__properties__ for item in modules[0]]
    }
    return context


def _all_agent_info(query, include_images=True):

    agent = Agents.nodes.get(key=query)

    conditions_and_reactions, _ = db.cypher_query(
        """
        
        MATCH (a:Agents {key:$key})-[:ENABLES]->(c:Conditions) 
        MATCH (c)-[:DESCRIBES]->(r:Reactions)
        MATCH (c)<-[:REPORTED]->(s:Sources)
        RETURN c, r, s
        
        """, {"key": agent.key}, resolve_objects=True
    )

    def obtain_image(x):
        if include_images:
            return reaction_smiles_to_base64(x)
        else:
            return None 
        
    context = dict(
        agent=agent.__properties__,
        conditions_and_reactions=[
            dict(
                condition=item[0].__properties__, 
                reaction=item[1].__properties__, 
                source=item[2].__properties__,
                img=ibf.generate_reaction_image(entry=item[1].__properties__['key'], smiles=item[1].__properties__['smiles'])
            ) for item in conditions_and_reactions
        ]
        
    )
    return context

def _all_source_info(query, include_images=True):
    source = Sources.nodes.get(doi=query)
    conditions_and_reactions, _ = db.cypher_query(
        """
        
        MATCH (c)-[:DESCRIBES]->(r:Reactions)
        MATCH (c)<-[:REPORTED]->(s:Sources {doi: $key})
        RETURN c, r
        
        """, {"key": source.doi}, resolve_objects=True
    )

    def obtain_image(x):
        if include_images:
            return reaction_smiles_to_base64(x)
        else:
            return None 

    context=dict(
        source=source.__properties__,
        conditions_and_reactions=[
            dict(
                condition=_expand_condition(item[0].__properties__), 
                reaction=item[1].__properties__, 
                img=ibf.generate_reaction_image(entry=item[1].__properties__['key'], smiles=item[1].__properties__['smiles'])
            ) for item in conditions_and_reactions
        ]
    )
    return context

def _all_molecule_info(query, include_images=True):
    molecule = Molecules.nodes.get(key=query)
    conditions_and_reactions_product, _ = db.cypher_query(
        """
        
        MATCH (r)-[]->(m:Molecules {key: $key})
        MATCH (r)<-[:DESCRIBES]-(c:Conditions)
        MATCH (c)<-[:REPORTED]-(s:Sources)
        RETURN c, r
        
        """, {"key": molecule.key}, resolve_objects=True
    )
    conditions_and_reactions_reactant, _ = db.cypher_query(
        """
        
        MATCH (r)<-[]-(m:Molecules {key: $key})
        MATCH (r)<-[:DESCRIBES]-(c:Conditions)
        MATCH (c)<-[:REPORTED]-(s:Sources)
        RETURN c, r
        
        """, {"key": molecule.key}, resolve_objects=True
    )

    
    modules = db.cypher_query(
        """
        MATCH (x:Molecules {key: $key})<-[]->(r:Reactions)<-[:INCLUDES]-(m:PrebChemDBModule) RETURN DISTINCT(m)
        """, {"key": molecule.key}, resolve_objects=True
    )    

    context=dict(
        molecule=molecule.__properties__,
        img=ibf.generate_molecule_image(entry=molecule.key, smiles=molecule.smiles),
        conditions_and_reactions_reactant=[
            dict(
                condition=_expand_condition(item[0].__properties__), 
                reaction=item[1].__properties__, 
                img = ibf.generate_reaction_image(
                    entry=item[1].__properties__['key'], 
                    smiles=item[1].__properties__['smiles']
                )
                
            ) for item in conditions_and_reactions_reactant
        ],
        conditions_and_reactions_product=[
            dict(
                condition=_expand_condition(item[0].__properties__), 
                reaction=item[1].__properties__, 
                img = ibf.generate_reaction_image(
                    entry=item[1].__properties__['key'], 
                    smiles=item[1].__properties__['smiles']
                )
            ) for item in conditions_and_reactions_product
        ],
        modules=[item[0].__properties__ for item in modules[0]]
    )
    return context


def _expand_condition(condition):
    agents = db.cypher_query(
        """
        MATCH (a:Agents)-[r:ENABLES]->(c:Conditions {key: $key}) RETURN a
        """, {"key": condition['key']}, resolve_objects=True
    )

    sources = db.cypher_query(
        """
        MATCH (a:Sources)-[r:REPORTED]->(c:Conditions {key: $key}) RETURN a
        """, {"key": condition['key']}, resolve_objects=True
    )
    context = dict(
        condition=condition, 
        agents=[item[0].__properties__ for item in agents[0]],
        sources=sources[0][0][0].__properties__
    )
    return context

def _list_all_reaction_ids():
    reaction = [item.__properties__ for item in Reactions.nodes.all()]
    return reaction


def _search_molecule(query):

    if query[:3] == 'pbm':
        return [query]

    try:
        molecule_inchikey_query = MolToInchiKey(MolFromSmiles(query))
    except:
        molecule_inchikey_query = None

    if molecule_inchikey_query is not None:
        keys, meta = db.cypher_query(
            """
            MATCH (node:Molecules) WHERE node.inchikey = "{:s}"  RETURN node.key
            """.format(molecule_inchikey_query), resolve_objects=False
        )
        keys = list(map(lambda x: x[0], keys))
        return keys
    
    keys, meta = db.cypher_query(
        """
        CALL db.index.fulltext.queryNodes("titles","{:s}~") YIELD node, score
        MATCH (node:Molecules) RETURN node.key
        """.format(query), resolve_objects=False
    )
    
    keys = list(map(lambda x: x[0], keys))
    return keys

def _search_agent(query):

    if query[:3] == 'pbg':
        return [query]

    try:
        molecule_inchikey_query = MolToInchiKey(MolFromSmiles(query))
    except:
        molecule_inchikey_query = None

    if molecule_inchikey_query is not None:
        keys, meta = db.cypher_query(
            """
            MATCH (node:Agents) WHERE node.inchikey = "{:s}"  RETURN node.key
            """.format(molecule_inchikey_query), resolve_objects=False
        )
        keys = list(map(lambda x: x[0], keys))
        return keys
    
    keys, meta = db.cypher_query(
        """
        CALL db.index.fulltext.queryNodes("agent_titles","{:s}~") YIELD node, score
        MATCH (node:Agents) RETURN node.key
        """.format(query), resolve_objects=False
    )
    
    keys = list(map(lambda x: x[0], keys))
    return keys


def _search_reaction(query):
    if query[:3] == 'pbr':
        return [query]
    else:
        return []
    
def _search_sources(query):
    if query[:2] == '10':
        return [query]
    else: 
        keys, meta = db.cypher_query(
            """
            CALL db.index.fulltext.queryNodes("publication_titles","{:s}~") YIELD node, score
            MATCH (node:Sources) WHERE score > 1.0 RETURN node.doi
            """.format(query), resolve_objects=False
        )
        
        keys = list(map(lambda x: x[0], keys))
        return keys
    
def _full_search_results(q, include_images=True, include_molecules=True, include_reactions=True):
    
    start = time.time()

    molecule_keys = _search_molecule(q)
    agent_keys = _search_agent(q)
    reaction_keys = _search_reaction(q)
    publication_keys = _search_sources(q)
    molecule_images = []
    reaction_images = []
    reactions = []
    molecules = []
    agents = []
    sources = []

    end = time.time()
    print("creating results index, time spent = {:8.4f}s".format(end - start))

        
    def obtain_image_molecules(x):
        if include_images:
            return molecule_smiles_to_base64(x)
        else:
            return None 

    start = time.time()
    for mol_key in molecule_keys:

        mol = Molecules.nodes.get(key=mol_key).__properties__
        if include_molecules:
            molecules.append(mol)
            molecule_images.append(ibf.generate_molecule_image(mol['key'], mol['smiles']))
        if include_reactions:
            mol_reactions = _reactions_from_molecule(mol_key)['involved_in']
            for r in mol_reactions:
                reaction = _all_reaction_info(r, include_images=include_images)
                
                reactions += [reaction]
    end = time.time()
    print("molecule info, time spent = {:8.4f}s".format(end - start))

    start = time.time()
    for agent_key in agent_keys:
        agent = Agents.nodes.get(key=agent_key).__properties__
        agents.append(agent)
    end = time.time()
    print("agents info, time spent = {:8.4f}s".format(end - start))

    start = time.time()
    for publication_key in publication_keys:
        publication = Sources.nodes.get(doi=publication_key).__properties__
        sources.append(publication)
    end = time.time()
    print("publication info, time spent = {:8.4f}s".format(end - start))

    start = time.time()
    for reaction_key in reaction_keys:
        reaction = _all_reaction_info(reaction_key, include_images=include_images)
        reactions += [reaction]
    end = time.time()
    print("reaction info, time spent = {:8.4f}s".format(end - start))

    context = dict(search_term=q)
    
    if include_reactions:
        context['reactions'] = reactions

    if include_molecules:
        context['molecules'] = list(zip(molecule_images, molecules))
    context['agents'] = agents
    context['sources'] = sources
    return context


def _obtain_module(module):

    module = PrebChemDBModule.nodes.get(key=module)
    reactions = module.connects.all()

    context = dict(
        module=module.__properties__,
        reactions=[_all_reaction_info(r.key) for r in reactions]
    )

    context['img'] = ibf.generate_diagram(module.key, reactions=context['reactions'])

    return context

def _index_modules():
    module = PrebChemDBModule.nodes.all()
    context = dict(
        modules=[m for m in module]
    )
    return context

def _find_similar_reactions(code):
    reaction = Reactions.nodes.get(key=code)
    similar_reactions = []
    for reaction in reaction.similar_to:
        rxn = reaction.__properties__
        rxn['img'] = ibf.generate_reaction_image(entry=reaction.key, smiles=reaction.smiles)
        similar_reactions.append(rxn)
    context = dict(
        similar_reactions=similar_reactions
    )
    return context

def _expansion_operator(seeds):
    out, meta = db.cypher_query(
        """MATCH (n:Molecules)-[:REACTS_IN]->(r:Reactions) 
        WITH r, collect(n.key) AS reactants
        WHERE ALL(x IN reactants WHERE x IN $seeds)
        MATCH (m:Molecules)-[:REACTS_IN]->(r:Reactions)-[:REACTS_OUT]->(p:Molecules)
        RETURN COLLECT(DISTINCT(r)), COLLECT(DISTINCT m), COLLECT(DISTINCT(p))""", params={
            'seeds': seeds
        }
    )
    out = out[0]
    reactions = []
    reactants = []
    products = []
    for reaction in out[0]:

        r = dict()
        r['img'] = ibf.generate_reaction_image(entry=reaction['key'], smiles=reaction['smiles'])
        r.update(**dict(reaction))
        reactions.append(r)

    for molecule in out[1]:
        m = dict()
        m['img'] = ibf.generate_molecule_image(entry=molecule['key'], smiles=molecule['smiles'])
        m.update(**dict(molecule))
        reactants.append(m)

    for molecule in out[2]:
        m = dict()
        m['img'] = ibf.generate_molecule_image(entry=molecule['key'], smiles=molecule['smiles'])
        m.update(**dict(molecule))
        products.append(m)
    reactions_all_info=[_all_reaction_info(r['key']) for r in reactions]
    diagram = ibf.generate_diagram(".".join(seeds), reactions=reactions_all_info)
    return {
        'seeds': seeds,
        'reactions': reactions,
        'molecules': reactants + products,
        'img': diagram
    }

def _expansion_operator_iteration(seeds):
    out, meta = db.cypher_query(
        """MATCH (n:Molecules)-[:REACTS_IN]->(r:Reactions) 
        WITH r, collect(n.key) AS reactants
        WHERE ALL(x IN reactants WHERE x IN $seeds)
        MATCH (m:Molecules)-[:REACTS_IN]->(r:Reactions)-[:REACTS_OUT]->(p:Molecules)
        RETURN COLLECT(DISTINCT(p.key))""", params={
            'seeds': seeds
        }
    )
    return list(set(seeds + out[0][0]))

def _iterative_expansion_operator(seeds, max_iterations=3, max_seeds=18):
    logging.debug("starting expansion, seed set size {0}".format(len(seeds)))
    logging.debug(
        "the expansion will run for {0} iterations or it will stop if expansions stop growing".format(
            max_iterations
        )
    )
    pool = seeds.copy()
    last_size = len(seeds)
    for i in range(max_iterations):
        pool = _expansion_operator_iteration(pool)
        logging.debug("iteration {0}, size {1}".format(i, len(pool)))
        if len(pool) == last_size:
            logging.debug("no expansion growth, stopping algorithm")
            break
        elif len(pool) > max_seeds:
            logging.debug("reached maximum extension")
            break
        else:
            last_size = len(pool)
    return _expansion_operator(pool)


def _new_search_function(q):
    molecule_keys = _search_molecule(q)
    agent_keys = _search_agent(q)
    reaction_keys = _search_reaction(q)
    publication_keys = _search_sources(q)
    molecule_images = []
    reaction_images = []
    reactions = []
    molecules = []
    agents = []
    sources = []

    # Searching for molecules
    molecules_results, meta = db.cypher_query(
        """
        MATCH (n:Molecules)
        WITH n, collect(n.key) AS reactants
        WHERE ANY(x IN reactants WHERE x IN $seeds)
        RETURN n
        """, 
        params={
            'seeds': molecule_keys
        }, resolve_objects=True
    )
    # Reactions
    reactions_results, meta = db.cypher_query(
        """
        MATCH (n:Molecules)-[:REACTS_IN]->(r:Reactions) 
        WITH r, collect(n.key) AS reactants
        WHERE ANY(x IN reactants WHERE x IN $seeds)
        WITH DISTINCT(r) AS rl
        MATCH (c:Conditions)-[:DESCRIBES]-> (rl)
        MATCH (s:Sources)-[:REPORTED]->(c)
        OPTIONAL MATCH (a:Agents)-[:ENABLES]->(c)
        WITH rl, c, s.doi AS source, COLLECT(a) AS agents
        WITH rl, COLLECT(c{.*,agents, source}) AS conditions
        RETURN rl, conditions
        """, 
        params={
            'seeds': molecule_keys
        }, resolve_objects=True
    )

    for reaction, conditions in reactions_results:
        for condition in conditions[0]:
            condition['agents'] = [a._properties for a in condition['agents']]

        reactions.append({
            'reaction': reaction.__properties__,
            'img': ibf.generate_reaction_image(entry=reaction.key, smiles=reaction.smiles),
            'conditions': [c for c in conditions[0]]
        })
        
    for molecule  in molecules_results[0]:
        molecules.append({
            'molecule': molecule.__properties__,
            'img': ibf.generate_molecule_image(entry=molecule.key, smiles=molecule.smiles)
        })

    
    for agent_key in agent_keys:
        agent = Agents.nodes.get(key=agent_key).__properties__
        agents.append(agent)
    

    
    for publication_key in publication_keys:
        publication = Sources.nodes.get(doi=publication_key).__properties__
        sources.append(publication)
    
    

    return {
        "search_term": q,
        "reactions": reactions,
        "molecules": molecules,
        "agents": agents,
        "sources": sources
    }