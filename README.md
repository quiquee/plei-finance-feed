## This is the Plei Finance Feed
A set of tools and documentation to extract data from the different Blockchains and feed finance systems (potentially as well others)

## Current Status
Include processing of Binance blockchain, matic (poligon) and Ethereum
It feeds a database (connection for now hardcoded in peidb.py)
No check for dups for now, it does import incremental by platform/blocknumber

## Process
Build a file *accountlist.tsv* with the different addresses to scan, transactions for those addresses are downloaded using Covalent and then processed in a way that can be imported for finance systems

The *accountlist.tsv* file is a Tab Separated Value files that contains 3 columns: 1st is a human readeable name of the account, 2nd is the ronin address, 3rd is a description for the account

Run the financefeed.py script and redirect STDOUT to a csv file that can be imported in a spreadsheet.

Doc in Covalenthq:
https://www.covalenthq.com/docs/api/#/0/Get%20transactions%20for%20address/USD/1

## TODO
Smarter updates, other than blocknumber, because if we add a new address, we want to be able
to catch up the history
Improve pleidb.py with configuration file
Better reporting

Create db 
```
cat createdb.sql| psql -d plei

```