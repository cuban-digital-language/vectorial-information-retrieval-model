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