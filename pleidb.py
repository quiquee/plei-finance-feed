# select platform,tx->'block' , tx->'txtype',tx->'date', 
# tx->'from', tx->'to', 
# tx->'ccy' , tx->'amount', tx->'ccy2',tx->'amount2', 
# tx->'desciption' from accbctx_raw ;

import psycopg2, json

def saveAcc(platform,data):
    try:
        conn = psycopg2.connect(
        host="localhost",
        database="plei",    
        user="pleibackend",
        password="oiower8hjb")

    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
        return 0

    block_start=0
    cursor = conn.cursor()
    qry = "SELECT max(block) FROM accbctx_raw WHERE platform='"+ "" +"'"
    cursor.execute(qry)
    block_start=cursor.fetchone()[0]
    if not block_start:
        block_start=0
        
    count = 0 
    for tx in data:
        #if tx["block"] < block_start:
        #    break

        postgres_insert_query = """ INSERT INTO accbctx_raw (platform,block,tx) VALUES (%s,%s,%s)"""
        record_to_insert = (platform,tx["block"], json.dumps(tx))

        try:
            cursor.execute(postgres_insert_query, record_to_insert)
        except Exception as error:
            print ("Oops! An exception has occured:", error)
            print ("Exception TYPE:", type(error))
            return count

        conn.commit()
        count = count + cursor.rowcount
        
    return count



def test():
    with open('./json_data.json') as json_file:
        data = json.load(json_file)
        saveAcc('ronin',data)



print(test())