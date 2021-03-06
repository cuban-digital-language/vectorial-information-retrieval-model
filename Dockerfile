FROM python:3.9.10
# FROM jupyter/base-notebook

RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download es_core_news_sm

RUN pip install redis
RUN pip install progressbar

RUN pip install ipykernel
RUN pip install notebook

COPY . ./usr/src
RUN cd ./usr/src

EXPOSE 8888
EXPOSE 8889

ENV HOST_DB=redis
ENV PORT_DB=6379



CMD ["bash", "jupyter", "notebook"]
# CMD ["bash","jupyter", "notebook", "test.ipynb", "--allow-root", "--ip", "'0.0.0.0'"]