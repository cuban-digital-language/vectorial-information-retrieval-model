import spacy
import ast
from math import log
import os
from redis import Redis
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


def vectorized(query):
    key = 'query'
    query_term_dict = {}
    doc = nlp(query)
    count = 0

    for token in doc:
        if token.is_stop or token.is_punct or token.is_digit:
            continue
        count += 1
        try:
            term = query_term_dict[token.lemma_.lower()]
        except KeyError:
            term = query_term_dict[token.lemma_.lower()] = Term()
        term.add_match(key)

    for entity in doc.ents:
        try:
            term = query_term_dict[entity.text.lower()]
        except KeyError:
            term = query_term_dict[entity.text.lower()] = Term()
        count += 1
        term.add_match(key)

    f_list = []
    for term in query_term_dict:
        if vectorial_db.get(term) is None:
            continue
        f_list.append(query_term_dict[term].match_by_document(key))

    fiq_max = max(f_list)
    N = int(vectorial_db.get('_$N$_'))
    q_vector = []
    for word in query_term_dict:
        dict_ = vectorial_db.get(word)
        if dict_ is None:
            continue

        try:
            fi = query_term_dict[word].match_by_document(key)
        except KeyError:
            fi = 0

        idf = log(N/len(ast.literal_eval(dict_.decode())))
        q_vector.append((0.5 + 0.5 * fi/fiq_max) * idf)

    return q_vector, query_term_dict


def get_ranking(q_vector, query_term_dict):
    a = vectorial_db.keys()

    document_list = []
    for key in a:
        try:
            document_list.append(int(key))
        except ValueError:
            pass

    wq2 = sum([w*w for w in q_vector])

    t_dict = {}
    for term in query_term_dict:
        dict_ = vectorial_db.get(term)
        if dict_ is None:
            t_dict[term] = dict_
        else:
            t_dict[term] = ast.literal_eval(dict_.decode())

    bar = get_progressbar(len(document_list), 'ranking sorted')
    bar.start()
    ranking_list = []
    for i, tuple_ in enumerate(zip(document_list, vectorial_db.mget(document_list))):
        doc_vector = []
        key, doc = tuple_
        if doc is None:
            continue
        doc = ast.literal_eval(doc.decode())
        if not 'w2' in doc:
            continue

        for term in query_term_dict:
            dict_ = t_dict[term]
            if dict_ is None:
                continue

            try:
                doc_vector.append(dict_[key]/doc['f_max'])
            except:
                doc_vector.append(0)

        wij = sum([d*q for d, q in zip(doc_vector, q_vector)])

        ranking_list.append((wij/(wq2 * doc['w2']), doc['text']))
        bar.update(i+1)

    bar.finish()

    ranking_list.sort(key=lambda x: x[0], reverse=True)
    return ranking_list
