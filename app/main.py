from flask import Flask, url_for, request, redirect
from flask import render_template, Response, abort
from wtforms import Form, SearchField
from prebchemdb.retrieve import _all_molecule_info, _all_reaction_info, ibf, _all_agent_info, _all_source_info, _obtain_module, _index_modules, _find_similar_reactions, _expansion_operator, _new_search_function, _iterative_expansion_operator, database_statistics
from neomodel import config
import json
import os
import neo4j

app = Flask(__name__)

def try_connect(url):
    try:
        config.DATABASE_URL = url
        _index_modules()  # Only call this if the connection succeeds
        return True
    except Exception as e:
        return False

url = "{2}://neo4j:{0}@{1}".format(os.environ['NEO4J_KEY'], os.environ['NEO4J_URL'], os.environ['NEO4J_MODE'])
print(url)
if not try_connect(url):
	raise RuntimeError("Failed to connect to Neo4j ")

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

class SearchForm(Form):
    query = SearchField(label='query')

class ExpansionSearchForm(Form):
    expquery = SearchField(label='expansion_query')

if os.path.exists(os.environ['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'):
    ibf.db_path = os.environ['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'
    ibf.save_path = os.environ['PREBCHEMDB_IMAGE_BUFFER']
else:
    ibf.db_path = os.environ['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'
    ibf.save_path = os.environ['PREBCHEMDB_IMAGE_BUFFER']
    ibf.create_table('molecules')
    ibf.create_table('reactions')
    ibf.create_table('modules')
    # ibf.create_table('molecules')

@app.route("/", methods=['POST', 'GET'])
def home():
    """
    Provides access to the home-page, which consists only on an additional search bar; all
    the other content is static.
    """
    context = database_statistics()
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('home.html', form=form, **context)


@app.route("/molecules/<mol_id>", methods=['POST', 'GET'])
def molecules(mol_id):
    """
    Provides access to molecules through their mol_id, which is under
    the format pbm-XXXXXX. 
    """
    context = _all_molecule_info(mol_id)
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('molecules.html', form=form, **context)


@app.route("/api/molecules/<mol_id>")
def api_molecules(mol_id):
    """
    Provides access to molecules through their mol_id, which is under
    the format pbm-XXXXXX. Returns a json document.
    """
    context = _all_molecule_info(mol_id)
    return context


@app.route("/reactions/<reaction_id>", methods=['POST', 'GET'])
def reactions(reaction_id):
    """
    Provides access to reactions through their mol_id, which is under
    the format pbr-XXXXXX. 
    """
    form = SearchForm(request.form)
    context = _all_reaction_info(reaction_id)
    similar_reactions = _find_similar_reactions(reaction_id)
    context['similar_reactions'] = similar_reactions['similar_reactions']
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('reactions.html', form=form, **context)


@app.route("/api/reactions/<reaction_id>")
def api_reactions(reaction_id):
    """
    Provides access to reactions through their mol_id, which is under
    the format pbr-XXXXXX.  Returns a json document.
    """
    context = _all_reaction_info(reaction_id)
    similar_reactions = _find_similar_reactions(reaction_id)
    context['similar_reactions'] = similar_reactions['similar_reactions']
    return context


@app.route("/agents/<agent_id>", methods=['POST', 'GET'])
def agents(agent_id):
    """
    Provides access to agents through their agent_id, which is under the
    format pba-XXXXXX. 
    """
    form = SearchForm(request.form)
    context = _all_agent_info(agent_id)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('agents.html', form=form, **context)


@app.route("/api/agents/<agent_id>")
def api_agents(agent_id):
    """
    Provides access to agents through their agent_id, which is under the
    format pba-XXXXXX. Returns a JSON document.
    """
    context = _all_agent_info(agent_id)
    return context


@app.route("/sources/<path:doi>", methods=['POST', 'GET'])
def sources(doi):
    """
    Provides access to sources through their doi. 
    """
    form = SearchForm(request.form)
    context = _all_source_info(doi)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('source.html', form=form,  **context)


@app.route("/api/sources/<path:doi>")
def api_sources(doi):
    """
    Provides access to sources through their doi. Returns a JSON document
    """
    context = _all_source_info(doi)
    return context


@app.route("/modules/", methods=['POST', 'GET'])
def modules_index():
    """
    Lists all the modules in an index-page.
    """
    form = SearchForm(request.form)
    context = _index_modules()
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('modules_index.html', form=form, **context)


@app.route("/api/modules/")
def api_modules_index():
    """
    Lists all the modules, returning a JSON document.
    """
    context = _index_modules()
    return context


@app.route("/modules/<code>", methods=['POST', 'GET'])
def modules(code):
    """
    Returns a specific module, identified by the module id, which is
    usually under the format pbmdl-XXXXXX.
    """
    form = SearchForm(request.form)
    context = _obtain_module(code)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('modules.html', form=form, **context)


@app.route("/api/modules/<code>")
def api_modules(code):
    """
    Returns a specific module, identified by the module id, which is
    usually under the format pbmdl-XXXXXX. Returns a JSON file.
    """
    context = _obtain_module(code)
    return context


@app.route("/expansion/<seeds>", methods=['POST', 'GET'])
@app.route("/expansion/", methods=['POST', 'GET'])
def expansion(seeds=None):
    """
    Runs a network expansion algorithm on a set of molecular entries
    separated by a dot. For instance, pbm-000032.pbm-0001459.pbm-000123.
    """
    context = dict()
    
    form = SearchForm(request.form)
    expform = ExpansionSearchForm(request.form)

    print(context)
    if seeds is None:
        context['search_flag'] = False
    
    else:
        context['search_flag'] = True
        seeds = seeds.split('.')
        context.update(**_iterative_expansion_operator(seeds, max_iterations=2, max_seeds=8))
        context['seeds'] = ' + '.join(seeds)

    if request.method == 'POST' and form.query.data is not None:
        print(form.data, form.validate())
        print(expform.data, expform.validate())
        print(list(request.form.items()))
        return redirect(url_for('search', query=form.query.data))
        
    elif request.method == 'POST' and expform.expquery.data is not None:
        print(form.data, form.validate())
        print(expform.data, expform.validate())
        print(list(request.form.items()))
        return redirect(url_for('expansion', seeds=expform.expquery.data))
    
    return render_template('expansion.html', form=form, expform=expform, **context)

@app.route("/api/expansion/<codes>")
def api_expansion(codes):
    """
    Runs a network expansion algorithm on a set of molecular entries
    separated by a dot. For instance, pbm-000032.pbm-0001459.pbm-000123.
    Returns a JSON file.
    """
    codes = codes.split('.')
    context = context.update(**_iterative_expansion_operator(codes, max_iterations=2, max_seeds=8))
    return context



@app.route("/search/", methods=['POST', 'GET'])
def search():
    """
    Runs a search using different fields. ´_new_search_function´ handles
    the task of detecting which kind of query was introduced. 
    """
    query = request.args.get('query', None)
    app.logger.info('searching "{0}" using _new_search_function'.format(query))
    
    form = SearchForm(request.form)
    try:
        context = _new_search_function(query)
    except Exception:
        
        abort(500)
        return ""
        
    app.logger.info('returning results for "{0}" using _new_search_function'.format(query))
    if request.method == 'POST':
        
        return redirect(url_for('search', query=form.query.data))
    return render_template('results.html', form=form, **context)


@app.route("/api/search/<query>")
def api_search(query):
    """
    Runs a search using different fields. ´_new_search_function´ handles
    the task of detecting which kind of query was introduced. Returns a JSON file.
    """
    context = _new_search_function(query)
    return context

@app.errorhandler(404)
def page_not_found(e):
    form = SearchForm(request.form)
    return render_template('not_found.html', form=form), 404

@app.errorhandler(500)
def internal_error(e):
    print("error 500 detected")
    form = SearchForm(request.form)
    return render_template('not_found.html', form=form), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')
