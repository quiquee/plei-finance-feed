** This is the Plei Finance Feed
A set of tools and documentation to extract data from the different Blockchains and feed finance systems (potentially as well others)

** Current Status
Priority is Ronin blockchain, as for Ethereum or Binance we have ways to download data
On top of that, Ronin has many more transactions, and of different kind, that have to be processed automatically to be able to make sense of that

** Process
Build a file *accountlist.tsv* with the different addresses to scan, transactions for those addresses are downloaded using Covalent and then processed in a way that can be imported for finance systems

The *accountlist.tsv* file is a Tab Separated Value files that contains 3 columns: 1st is a human readeable name of the account, 2nd is the ronin address, 3rd is a description for the account

Run the financefeed.py script and redirect STDOUT to a csv file that can be imported in a spreadsheet.
Using Covalent we can download all transactions in a JSON. You will need an API KEY for that.

Doc in Covalenthq:
https://www.covalenthq.com/docs/api/#/0/Get%20transactions%20for%20address/USD/1



** TODO
Include processing of Binance blockchain and Ethereum

Feed a bd in the backend with the data, ensuring incremental updates are possible
