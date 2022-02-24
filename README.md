## This is the Plei Finance Feed
A set of tools and documentation to extract data from the different Blockchains and feed finance systems (potentially as well others)

## Current Status
Priority is Ronin blockchain, as for Ethereum or Binance we have ways to download data
On top of that, Ronin has many more transactions, and of different kind, that have to be processed automatically to be able to make sense of that

## Process
Using Covalent we can download all transactions in a JSON. You will need an API KEY for that.

Doc in Covalenthq:
https://www.covalenthq.com/docs/api/#/0/Get%20transactions%20for%20address/USD/1

First we download the data to a JSON. For example if the account is ronin:237b86abafd83da3c52b2a36a2b9f63d5cbf78e2 we can download using the v1 transactions method:

curl -X GET "https://api.covalenthq.com/v1/2020/address/ronin:237b86abafd83da3c52b2a36a2b9f63d5cbf78e2/transactions_v2/?key=<YOUR API KEY HERE>&page-size=7000&page-number=0"  -H "Accept: application/json" > myfile.json

Once we have the data in a file (myfile.json) this has to be processed using the python script "extract.py" (this name will certainly have to change one day) , which produces a CSV that can then be imported in excel for now

## TODO
Include processing of Binance blockchain and Ethereum
Add a configuration file with all different Plei addresses to scan
Feed a bd in the backend with the data, ensuring incremental updates are possible
