# Uploading and curating data in ChemOrigins

## Introduction

In ChemOrigins we aim to address the systematization of prebiotic chemistry. Doing so
requires a large effort. We believe that only a community effort will be able to
achieve such a great goal.

ChemOrigins uses version control systems (VCS) to enable data upload and curation. By
allowing users to commit branches and curates to merge those branches, we can keep track 
of changes, who proposed those changes, without ever losing data. Although computational
scientists might be very familiar with this process, less experienced users might not be
so aware of the process. Therefore, we also enable users to make their own submissions
using a simple annotation app that will do all the heavy lifting for them.

## Annotations: the root of ChemOrigins data

The data in ChemOrigins is created as annotations. An example of reaction 
annotation is shown below. We use JSON format for now (though we will probably switch to 
YAML format soon).



We can observe a few different fields here:
- 

So far, we are only enabling annotations at reaction/condition/source level. Future
work will aim to include annotations that span all the items of the database.

## Upload

We will visit the two forms of upload.
- Through `git`, best suited for computational scientists.
- Through the upload app, best suited for everyone else.

### Git

To upload new annotations, we recommend following this protocol.

- Create your annotations as different files. Name them by the data that you are
preparing them, as their name will probably change once they are accepted. 
- Clone the ChemOrigins repository. Use:
```
    git clone 
```
- Create a new branch, with a self-explanatory data.
```
    git checkout -b cyabo-sulfidic.2025-05-02
```
- Add your changes, commit them and push.
```
    git add *.json
    git commit -m "cyano-sulfidic reactions from my lab".
    git push -u origin
```
- In principle, the curators will handle it from here. But you can send an email
to the following address to inform us about the new information uploaded.

### App

The app is designed to be self-explanatory. You fill the data form, and you create
a stack of annotations. Then, you click on submit. We will handle it from there, but
you can also send an email to inform us about the new information uploaded.

## Curation

Curation is as important as upload, otherwise the database would become crowded with
trashy data and it would not be useful. We provide three avenues for curation.

- **Github issues**: If you find data that you believe is not really accurate, and
you are willing to devote some time to solve it (thanks!), you can open a Github
issue, indicating the data that you find wrong, and a possible solution. A good example
of message would be something like:

```
    Hi everyone

    I found that pbr-XXX considers a metal as a reactant and product, being present in
    the chemical equation in both sides. I am pretty sure that in this case, the Fe0
    would not be a reactant or a product but a catalyst. Similar problems could be found
    in pbr-XXX and pbr-XXX.
```

- **Flag**. If you just find that there might be an issue, but you lack the time to solve
it, you can click on the "flag" button, so a report is created on that instance. That way,
curators can find issues more quickly.
- **Join the curators team**. This might be a long commitment, meetings will take place
periodically. If you want to join the team, you can freely join the ChemOrigins Slack.

