import click
from neomodel import db, Q, config
from prebchemdb.retrieve import (
    Reactions, Molecules, Agents, Sources, Conditions, _reactions_from_molecule, 
    _all_reaction_info, _all_agent_info, _all_source_info, _all_molecule_info,
    _list_all_reaction_ids,
    _full_search_results, _find_similar_reactions,
    _search_molecule, _obtain_module, _index_modules, _expansion_operator,
    _new_search_function
)
import json
import os

config.DATABASE_URL = "neo4j+s://neo4j:{0}@{1}".format(
    os.environ['NEO4J_KEY'], os.environ['NEO4J_URL']
)  # default

@click.command()
@click.argument('CODE')
def reaction(code):
    click.echo(json.dumps(Reactions.nodes.get(key=code).__properties__, indent=4))
    db.driver.close()

@click.command()
@click.argument('CODE')
def molecule(code):
    click.echo(json.dumps(Molecules.nodes.get(key=code).__properties__, indent=4))
    db.driver.close()

@click.command()
@click.argument('CODE')
def agent(code):
    click.echo(json.dumps(Agents.nodes.get(key=code).__properties__, indent=4))
    db.driver.close()


@click.command()
@click.argument('CODE')
def source(code):
    click.echo(json.dumps(Sources.nodes.get(doi=code).__properties__, indent=4))
    db.driver.close()

@click.command()
@click.argument('CODE')
def conditions(code):
    click.echo(json.dumps(Conditions.nodes.get(key=code).__properties__, indent=4))
    db.driver.close()


@click.command()
@click.argument('CODE')
def search_molecule(code):
    print(code)
    codes = _search_molecule(code)
    match = []
    for code in codes:
        match.append(Molecules.nodes.get(key=code).__properties__)
    click.echo(json.dumps(match, indent=4))
    db.driver.close()


@click.command()
@click.argument('CODE')
def reactions_from_molecule(code):

    ctxt = _reactions_from_molecule(code)
    click.echo(json.dumps(ctxt, indent=4))    
    db.driver.close()

@click.command()
@click.argument('CODE')
@click.option('--img', default=False)
def all_reaction_info(code, img):

    ctxt = _all_reaction_info(code, img)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
@click.option('--img', default=False)
@click.argument('CODE')
def all_agent_info(code, img):
    ctxt = _all_agent_info(code, img)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()

@click.command()
@click.option('--img', default=False)
@click.argument('CODE')
def all_source_info(code, img):
    ctxt = _all_source_info(code, img)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()

@click.command()
@click.argument('CODE')
def all_molecule_info(code):
    ctxt = _all_molecule_info(code)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
def list_all_reactions():
    ctxt = _list_all_reaction_ids()
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()

@click.command()
def list_all_modules():
    ctxt = _index_modules()
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()

@click.command()
@click.argument('SEARCH_TERM')
def modules(search_term):
    ctxt = _obtain_module(search_term)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
@click.option('--img', default=True)
@click.option('--reactions', default=True)
@click.option('--molecules', default=True)
@click.argument('SEARCH_TERM')
def full_search_results(search_term, img, reactions, molecules):
    ctxt = _full_search_results(search_term, img, include_molecules=molecules, include_reactions=reactions)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
@click.argument('CODE')
def similar_reactions(code):
    ctxt = _find_similar_reactions(code)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
@click.argument('CODES', nargs=-1)
def expansion(codes):
    print(codes)
    ctxt = _expansion_operator(codes)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


@click.command()
@click.argument('SEARCH_TERM')
def new_search_results(search_term):
    ctxt = _new_search_function(search_term)
    click.echo(json.dumps(ctxt, indent=4))
    db.driver.close()


cli = click.Group()
cli.add_command(reaction)
cli.add_command(molecule)
cli.add_command(source)
cli.add_command(agent)
cli.add_command(conditions)
cli.add_command(search_molecule)
cli.add_command(reactions_from_molecule)
cli.add_command(all_reaction_info)
cli.add_command(all_agent_info)
cli.add_command(all_source_info)
cli.add_command(all_molecule_info)
cli.add_command(list_all_reactions)
cli.add_command(list_all_modules)
cli.add_command(full_search_results)
cli.add_command(modules)
cli.add_command(similar_reactions)
cli.add_command(expansion)
cli.add_command(new_search_results)


if __name__ == '__main__':
    cli()