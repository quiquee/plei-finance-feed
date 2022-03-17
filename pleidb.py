# select platform,tx->'block' , tx->'txtype',tx->'date', 
# tx->'from', tx->'to', 
# tx->'ccy' , tx->'amount', tx->'ccy2',tx->'amount2', 
# tx->'desciption' from accbctx_raw ;

import psycopg2, json

def pleidbconn(mode="rw"):
    try:
        conn = psycopg2.connect(
        host="localhost",
        database="plei",    
        user="pleibackend",
        password="oiower8hjb")

    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
        
    return conn

def getTx(address):
    conn=pleidbconn("rw")
    qry = "select platform,tx->'block' , tx->'txtype',tx->'date',  \
        tx->'from', tx->'to', \
        tx->'ccy' , tx->'amount', tx->'ccy2',tx->'amount2',  \
        tx->'desciption' from accbctx_raw \
        WHERE tx->>'from' LIKE '"+ address +"%' OR tx->>'to' LIKE '"+ address +"%'" 

    cursor = conn.cursor()
    cursor.execute(qry)
    txlist=cursor.fetchall()
    
    return txlist
    
def getLastBlock(address):
    conn=pleidbconn("rw")
    qry = "select max(tx->>'block') from accbctx_raw \
        WHERE tx->>'from' LIKE '"+ address +"%' OR tx->>'to' LIKE '"+ address +"%'" 
        
    cursor = conn.cursor()
    cursor.execute(qry)
    tx=cursor.fetchone()[0]
    return tx

def getAllAddress():
    conn=pleidbconn("rw")
    cursor = conn.cursor()

    qry = "select distinct platform, tx->>'from' from accbctx_raw "    
    cursor.execute(qry)
    txfrom=cursor.fetchall()
    
    qry = "select distinct platform, tx->>'to' from accbctx_raw "    
    cursor.execute(qry)
    txto=cursor.fetchall()

    return txto

def saveAcc(platform,data):
    conn=pleidbconn("rw")
    cursor = conn.cursor()
    
    count = 0 
    for tx in data:
        
        postgres_insert_query = """ INSERT INTO accbctx_raw (platform,txid,tx) VALUES (%s,%s,%s)"""
        record_to_insert = (platform,tx["tx"]+ "-" +str(tx["seq"]), json.dumps(tx))

        try:
            cursor.execute(postgres_insert_query, record_to_insert)
            conn.commit()            
        except Exception as error:
            
            # cant match this using errors....
            if (error.pgcode == '23505' or error.pgcode =='25P02' ):
                print("Warning: transaction in " + platform + " Tx-Seq " + tx["tx"] + "-" +str(tx["seq"])+ " already in database, skipping")
                continue

            else:
                print ("Oops! An exception has occured:", error)
                print ("Exception TYPE:", type(error), error.pgcode )
                print(postgres_insert_query, record_to_insert)
                break

        
        count = count + cursor.rowcount
        
    return count



def test_import():
    with open('./json_data.json') as json_file:
        data = json.load(json_file)
        saveAcc('ronin',data)



print(getLastBlock("Lunacian ventana Fraud"))