FROM python:3.9.10-alpine3.15

RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download es_core_news_sm

RUN pip install redis
RUN pip install progressbar

RUN pip install ipykernel

EXPOSE 8889
CMD ['jupyter' 'notebook', 'test.ipynb']