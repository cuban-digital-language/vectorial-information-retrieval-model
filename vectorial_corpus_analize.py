import json
import spacy
import os
from math import log
from dotenv import load_dotenv

from redis import Redis
try:
    from .data_struct import Document, Term, get_progressbar
except (ModuleNotFoundError, ImportError):
    from data_struct import Document, Term, get_progressbar

load_dotenv()
nlp = spacy.load("es_core_news_sm")

host = 'localhost'
port = os.getenv('PORT', 6379)

vectorial_db = Redis(host=host, port=port, db=6)
social_net = 'cubadebate'


def main():
    all_keys = vectorial_db.keys()
    if any(all_keys):
        return

    # Opening JSON file
    f = open('./cubadebate.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    f.close()
    document_dict = {}

    for obj in data:
        header = obj['text']
        url = obj['url']
        for c in obj['comments']:
            all_text = header + ' -> ' + c['text']
            hsh = hash(all_text)
            document_dict[hsh] = Document(all_text, url)

    N = len(document_dict)
    print(f"{N} document total")

    term_dict = {}

    bar = get_progressbar(N, 'tokenizer documents')
    bar.start()
    for i, key in enumerate(document_dict):
        doc = nlp(document_dict[key].text)
        count = 0
        for token in doc:
            if token.is_stop or token.is_punct or token.is_digit:
                continue

            count += 1
            try:
                term = term_dict[token.lemma_.lower()]
            except KeyError:
                term = term_dict[token.lemma_.lower()] = Term()

            term.add_match(key)

        for entity in doc.ents:

            try:
                term = term_dict[entity.text.lower()]
            except KeyError:
                term = term_dict[entity.text.lower()] = Term()
            count += 1
            term.add_match(key)

        bar.update(i+1)
        document_dict[key].total_term = count

    bar.finish()

    tn = len(term_dict)
    print(f"{tn} term total")

    bar = get_progressbar(N, 'term indexation')
    bar.start()
    for i, key in enumerate(document_dict):
        f_list = []
        for term in term_dict:
            f_list.append(term_dict[term].match_by_document(key))

        document_dict[key].f_max = max(f_list)
        bar.update(i+1)

    bar.finish()

    def get_weight(word, hsh_doc):
        term = term_dict[word]
        doc = document_dict[hsh_doc]
        tf = term.match_by_document(hsh_doc) / doc.f_max
        idf = log(N/term.match_len)

        return tf * idf

    bar = get_progressbar(N, 'document vectorized')
    bar.start()
    for i, key in enumerate(document_dict):
        vector = []
        for term in term_dict:
            vector.append(get_weight(term, key))

        document_dict[key].vector = vector
        bar.update(i+1)

    bar.finish()

    bar = get_progressbar(len(term_dict), 'save values computed about terms')
    bar.start()
    for i, term in enumerate(term_dict):
        temp = {}
        for key in document_dict:
            try:
                w = document_dict[key].vector[i]
            except:
                w = 0
            if w != 0:
                temp[key] = w

        bar.update(i+1)
        vectorial_db.set(term, str(temp))
    bar.finish()

    bar = get_progressbar(N, 'save values computed about document')
    bar.start()
    for i, key in enumerate(document_dict):
        doc = document_dict[key]
        wd2 = sum([w*w for w in doc.vector])
        vectorial_db.set(key, str({
            'text': document_dict[key].text,
            'f_max': document_dict[key].f_max,
            'w2': wd2
        }))
        bar.update(i+1)
    bar.finish()

    vectorial_db.set('_$N$_', N)
