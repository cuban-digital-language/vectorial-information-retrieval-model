class Document:
    def __init__(self, text, url):
        self.text = text
        self.url = url
        self.total_term = 0
        self.f_max = 0
        self.vector = None

class Term:
    def __init__(self):
        self.doc_count = {}
    
    def add_match(self, hsh_doc):
        try: self.doc_count[hsh_doc] += 1
        except KeyError: self.doc_count[hsh_doc] = 1
    
    def match_by_document(self, hsh_doc):
        try: return self.doc_count[hsh_doc]
        except: return 0
    
    @property
    def match_len(self):
        return len(self.doc_count)

import progressbar
def get_progressbar(N, name = ""):
    return progressbar.ProgressBar(
        maxval=N, 
        widgets=[progressbar.Bar('#', '[', ']'), 
        name, 
        progressbar.Percentage()])

    
def pretty(dict_, *texts):
    result = list(texts)
    for key in dict_:
        for i, text in enumerate(texts):
            lower_text : str = text.lower()
            index = 0
            while True:
                try: 
                    index = lower_text.index(key, index)
                    result[i] = text[0:index] + "\33[47m{}\033[00m".format(text[index: index + len(key)]) + text[index + len(key) + 1: ]
                    index += len(key) 
                except ValueError:
                    break
    return tuple(result)