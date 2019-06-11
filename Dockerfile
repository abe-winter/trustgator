FROM python:3.7

WORKDIR /srv/trustgator
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sql ./sql
COPY trustgator ./trustgator
COPY varyaml.yml .
COPY logo ./logo
CMD gunicorn something
