from flask import Flask, url_for, request, redirect
from flask import render_template
from wtforms import Form, SearchField
from prebchemdb.retrieve import _all_molecule_info, _all_reaction_info, ibf, _full_search_results, _all_agent_info, _all_source_info, _obtain_module, _index_modules, _find_similar_reactions, _expansion_operator, _new_search_function
from neomodel import config
from flask_flatpages import FlatPages
import json
import os
import time

# DEBUG = True
# FLATPAGES_AUTO_RELOAD = DEBUG
# FLATPAGES_EXTENSION = '.md'
# FLATPAGES_ROOT = 'blog'
# POST_DIR = 'insights'
# MOLECULE_OF_THE_MONTH_ROOT = 'molecules'
# MOLECULE_OF_THE_MONTH = 'formamide'

# config_file = 'config.json'

app = Flask(__name__)

with open('config.json') as f:
    app.config.update(json.load(f))

flatpages = FlatPages(app)
app.config.from_object(__name__)
config.DATABASE_URL = "neo4j+s://neo4j:{0}@{1}".format(os.environ['NEO4J_KEY'], os.environ['NEO4J_URL'])


from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

class SearchForm(Form):
    query = SearchField(label='query')

class ExpansionSearchForm(Form):
    expquery = SearchField(label='expansion_query')

if os.path.exists(app.config['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'):
    ibf.db_path = app.config['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'
    ibf.save_path = app.config['PREBCHEMDB_IMAGE_BUFFER']
else:
    ibf.db_path = app.config['PREBCHEMDB_IMAGE_BUFFER'] + '/image-buffer.db'
    ibf.save_path = app.config['PREBCHEMDB_IMAGE_BUFFER']
    ibf.create_table('molecules')
    ibf.create_table('reactions')
    ibf.create_table('modules')
    # ibf.create_table('molecules')

@app.route("/", methods=['POST', 'GET'])
def home():
    print("wellcome to main")
    form = SearchForm(request.form)

    # path = '{}/{}'.format(app.config['MOLECULE_OF_THE_MONTH_ROOT'], app.config['MOLECULE_OF_THE_MONTH'])
    
    # molecule_of_the_moth_post = flatpages.get_or_404(path)
    
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('home.html', form=form)# , motm=molecule_of_the_moth_post)


@app.route("/molecules/<mol_id>", methods=['POST', 'GET'])
def molecules(mol_id):
    context = _all_molecule_info(mol_id)
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('molecules.html', form=form, **context)


@app.route("/api/molecules/<mol_id>")
def api_molecules(mol_id):
    context = _all_molecule_info(mol_id)
    return context


@app.route("/reactions/<reaction_id>", methods=['POST', 'GET'])
def reactions(reaction_id):
    form = SearchForm(request.form)
    context = _all_reaction_info(reaction_id)
    similar_reactions = _find_similar_reactions(reaction_id)
    context['similar_reactions'] = similar_reactions['similar_reactions']
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('reactions.html', form=form, **context)


@app.route("/api/reactions/<reaction_id>")
def api_reactions(reaction_id):
    context = _all_reaction_info(reaction_id)
    similar_reactions = _find_similar_reactions(reaction_id)
    context['similar_reactions'] = similar_reactions['similar_reactions']
    return context


@app.route("/agents/<agent_id>", methods=['POST', 'GET'])
def agents(agent_id):
    form = SearchForm(request.form)
    context = _all_agent_info(agent_id)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('agents.html', form=form, **context)


@app.route("/api/agents/<agent_id>")
def api_agents(agent_id):
    context = _all_agent_info(agent_id)
    return context


@app.route("/sources/<path:doi>", methods=['POST', 'GET'])
def sources(doi):
    form = SearchForm(request.form)
    context = _all_source_info(doi)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('source.html', form=form,  **context)


@app.route("/api/sources/<path:doi>")
def api_sources(doi):
    
    context = _all_source_info(doi)
    return context


@app.route("/modules/", methods=['POST', 'GET'])
def modules_index():
    form = SearchForm(request.form)
    context = _index_modules()
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('modules_index.html', form=form, **context)


@app.route("/api/modules/")
def api_modules_index():
    context = _index_modules()
    return context


@app.route("/modules/<code>", methods=['POST', 'GET'])
def modules(code):
    form = SearchForm(request.form)
    context = _obtain_module(code)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('search', query=form.query.data))
    return render_template('modules.html', form=form, **context)


@app.route("/api/modules/<code>")
def api_modules(code):
    context = _obtain_module(code)
    return context


@app.route("/expansion/<seeds>", methods=['POST', 'GET'])
@app.route("/expansion/", methods=['POST', 'GET'])
def expansion(seeds=None):
    context = dict()
    
    form = SearchForm(request.form)
    expform = ExpansionSearchForm(request.form)

    print(context)
    if seeds is None:
        context['search_flag'] = False
    
    else:
        context['search_flag'] = True
        seeds = seeds.split('.')
        context.update(**_expansion_operator(seeds))
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
    codes = codes.split('.')
    context = _expansion_operator(codes)
    return context



@app.route("/search/", methods=['POST', 'GET'])
def search():
    query = request.args.get('query', None)
    # include_reactions = request.args.get('reactions', type=lambda x: x == 'True', default=True)
    # include_molecules = request.args.get('molecules', type=lambda x: x == 'True', default=True)
    # min_temperature = request.args.get('mintemp', type=float, default=None)
    # max_temperature = request.args.get('maxtemp', type=float, default=None)
    
    app.logger.info('searching "{0}" using _new_search_function'.format(query))
    context = _new_search_function(query)
    app.logger.info('returning results for "{0}" using _new_search_function'.format(query))
    form = SearchForm(request.form)
    
    if request.method == 'POST':
        
        return redirect(url_for('search', query=form.query.data))
    return render_template('results.html', form=form, **context)


@app.route("/api/search/<query>")
def api_search(query):
    
    context = _new_search_function(query)
    return context

@app.route("/blog/<entry_id>")
def blog(entry_id):
    path = '{}/{}'.format(app.config['POST_DIR'], entry_id)
    
    post = flatpages.get_or_404(path)
    return render_template('blog.html', post=post)

@app.route("/blog/")
def blog_index():
    posts = [p for p in flatpages]
    
    return render_template('blog_index.html', posts=posts)

if __name__ == "__main__":
    app.run(host='0.0.0.0')