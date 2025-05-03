import requests
import pandas as pd
from datetime import date
import json
# from git import Repo


def convert_to_legacy_annotation(annotation):

    conditions = []
    if annotation['digest']['temperature'] is not None:
        conditions.append("T={0}".format(annotation['digest']['temperature']))

    if annotation['digest']['yield_'] is not None:
        conditions.append("yield={0}".format(annotation['digest']['yield_']))

    if annotation['digest']['pH'] is not None:
        conditions.append("pH={0}".format(annotation['digest']['pH']))

    if annotation['digest']['time'] is not None:
        conditions.append("time={0}".format(annotation['digest']['time']))
    
    if annotation['digest']['agents'] is None:
        annotation['digest']['agents'] = []

    l_annotation = {
        "agents": annotation['digest']['agents'],
        "attributes": "",
        "comments": "",
        "conditions": [],
        "crossref": [],
        "date_": date.today().isoformat(),
        "key": date.today().isoformat() + ":" + annotation['id'],
        "primary": annotation['text'],
        "smiles": annotation['reaction_string'],
        "source": annotation['doi'],
        "waste": []
    }
    return l_annotation

def branch(annotations, path):
    pass 

# def branch(annotations, path):

#     repo = Repo(path)
#     add_file = []
#     dump_name = "dump-" + date.today().isoformat()
#     for annotation in annotations:
#         file_name = annotation['key']
#         json.dump(annotation, open(path + file_name + '.json', 'w'), indent=4)
#         add_file.append(path + file_name + '.json')

#     new_branch = repo.create_head(dump_name)
#     repo.head.reference = new_branch
#     # empty_repo.heads.master.checkou
    
#     repo.index.add( add_file ) 
#     repo.index.commit(f"adding {len(annotation)} annotations")
#     #repo.create_remote(f"origin {file_name}", repo.remotes.origin.url)
#     # origin = repo.remotes.origin
#     repo.git.push("--set-upstream","origin",f"{dump_name}")
#     return dump_name

def publication_metadata(doi):
    r = requests.get(
        f'https://doi.org/{doi:s}', headers={"Accept": "application/vnd.citationstyles.csl+json"}
    )
    x = r.json()
    return {
        'doi': doi,
        'title': x['title'],
        'year': x['published']['date-parts'][0][0],
        'journal': x['container-title'],
        'authors': ','.join([item['family'] + ' ' + item['given'][0] for item in x['author']])
    }


def wrap(text, length=80):

    u = []
    words = text.split(' ')
    current_line = ""
    for w in words:
        current_line += " " + w
        if len(current_line) > length:
            u.append(current_line)
            current_line = ""
    if len(u) == 0:
        u.append(current_line)
    return '\n'.join(u)