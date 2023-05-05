import arango
import json
import click
import tqdm


@click.command()
@click.argument('HOST')
@click.argument('USER')
@click.argument('PASSWORD')
@click.argument('DB')
@click.argument('collection')
def dump(host, user, password, db, collection):

    """
    Downloads the inputs of a collection, and then erases them
    from the database.
    """

    db = arango.ArangoClient(
        hosts=host
    ).db(
        db, username=user, password=password
    )

    db_collection = db.collection(collection)
    for doc in tqdm.tqdm(db_collection):
        with open(doc['_key'] + '.json', 'w') as f:
            json.dump(doc, f, sort_keys=True, indent=4)

@click.command()
@click.argument('HOST')
@click.argument('USER')
@click.argument('PASSWORD')
@click.argument('DB')
@click.argument('collection')
def clean(host, user, password, db, collection):

    db.aql.execute(
        """FOR u IN @@collection 
            REMOVE u IN @@collection""",
        bind_vars={"@collection":collection}
    )

cli = click.Group()
cli.add_command(clean)
cli.add_command(dump)

if __name__ == "__main__":
    cli()