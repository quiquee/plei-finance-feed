FROM python:3.9

WORKDIR /plei-acc

ADD financefeed.py /plei-acc/
ADD pleidb.py /plei-acc/
ADD accounts /plei-acc/accounts

RUN pip install psycopg2 requests

CMD [ "python", "financefeed.py accounts/accountlist.tsv" ]
