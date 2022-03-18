from readline import append_history_file
import requests
import csv
import json
import sys
import ast
import re
import pleidb

cnames={
    "0x213073989821f738a7ba3520c3d31a1f9ad31bbd": "Marketplace Contract", 
    "0x0000000000000000000000000000000000000000": "0x0",
    "0x7d0556d55ca1a92708681e2e231733ebd922597d": "Katana Router Contract",
    "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap"
}

ccies={
    "ethereum": "ETH",
    "ronin": "RON",
    "binance": "BNB"
}

covaApiKey = "ckey_55f1971fa82749ae89275572b5b"


def cn(address):

    if cnames.get(address):
        return cnames[address]
    else:
        return address


def dispAmt(amount, ccy):
    if ccy == "USDC":
        return int(amount)/1e6
    elif ccy == "SLP":
        return int(amount)
    else:
        return int(amount)/1e18

def paramValue(params, name):
    if not params: return "#N/A"
    for param in params:
        if param["name"] == name:
            return param["value"]
    return ""



def extract(output,paramaddress, platform):
    
    i = 0
    data=[]
    
    cnparam = cn(paramaddress.replace("ronin:","0x"))
    print("Cn param: (" + paramaddress + ") " + cnparam )
    

    for item in output["data"]["items"]:
        xdata={
                "block": item["block_height"],
                "tx": item["tx_hash"],
                "seq": "",                
                "date": item["block_signed_at"],
                "txtype": "",
                "from": "",
                "to": "",
                "ccy": "",
                "amount": "",
                "ccy2": "",
                "amount2": "",
                "description": ""
            }
        amount = 0
        
        description=""
        # Lets check if there is an amount
        if int(item["value"]) > 0 :
            amount=dispAmt(item["value"],ccies[platform])
            
            xdata["seq"]=100
            xdata['txtype']="transfer"
            xdata['from']=cn(item["from_address"])          
            xdata['to']=cn(item["to_address"])
            xdata['ccy']=ccies[platform] 
            xdata['amount']=amount
            xdata['description']="Transfer"
            if cnparam == xdata["from"] or cnparam == xdata["to"]:
                print(xdata)
                data.append(xdata)
                

         # Lets check if there is gas cost
        if int(item["gas_spent"]* item["gas_price"]) > 0:
            amount=int(item["gas_spent"]* item["gas_price"])/1e18

            xdata['txtype']="Fee "+ platform 
            xdata['seq']=101
            xdata['from']=cn(item["from_address"])
            xdata['to']=""
            xdata['ccy']=ccies[platform]
            xdata['amount']=amount
            xdata['description']="Fees paid for transaction" 
            if cnparam == xdata["from"] or cnparam == xdata["to"]:
                print(xdata)
                data.append(xdata)                            
        
        j=199
        for event in item["log_events"]:
            j=j+1
            matched = ""
            if event["decoded"]:
                xdata={
                    "block": item["block_height"],
                    "tx": item["tx_hash"],
                    "seq": j,                
                    "date": item["block_signed_at"],
                    "txtype": "",
                    "from": "",
                    "to": "",
                    "ccy": "",
                    "amount": "",
                    "ccy2": "",
                    "amount2": "",
                    "description": ""
                }
                
                eventType=event["decoded"]["name"]
            
                eventparams = event["decoded"]["params"]

                if eventType == "Swap" and paramValue(eventparams,"amount0In"):
                    matched = "YES"
                    # this looks like a swap in Ronin
                    if int(paramValue(eventparams,"amount0In")) == 0:
                        ccy1 = event["sender_contract_ticker_symbol"].split("-")[1]
                        ccy2 = event["sender_contract_ticker_symbol"].split("-")[0]
                        amount1=dispAmt(paramValue(eventparams,"amount1In"),ccy1)
                        amount2=dispAmt(paramValue(eventparams,"amount0Out"),ccy2)
                    else:
                        ccy1 = event["sender_contract_ticker_symbol"].split("-")[0]
                        ccy2 = event["sender_contract_ticker_symbol"].split("-")[1]
                        amount1=dispAmt(paramValue(eventparams,"amount0In"),ccy1)
                        amount2=dispAmt(paramValue(eventparams,"amount1Out"),ccy2)
                        

                    xdata['txtype']="Swap"
                    xdata['from']=cn(paramValue(eventparams,"sender"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=ccy1
                    xdata['amount']=amount1
                    xdata['ccy2']=ccy2
                    xdata['amount2']=amount2
                    xdata['description']="Swap "+ event["sender_name"] + " " +xdata['ccy'] + " for " + xdata['ccy2']


                if matched != "YES" and eventType == "Swap" and paramValue(eventparams,"amount0"):
                    matched = "YES"
                    # this looks like a swap in Uniswap
                    
                    ccy1 = "???"
                    ccy2 = "???"
                    amount1=dispAmt(paramValue(eventparams,"amount1"),ccy1)
                    amount2=dispAmt(paramValue(eventparams,"amount0"),ccy2)
   
                    xdata['txtype']="Swap"
                    xdata['from']=cn(paramValue(eventparams,"sender"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=ccy1
                    xdata['amount']=amount1
                    xdata['ccy2']=ccy2
                    xdata['amount2']=amount2
                    xdata['description']="Swap in Uniswap" 

                if eventType == "AuctionSuccesful" :
                    matched="YES"
                    # This is an axie transfer
                    axie = ast.literal_eval(event["raw_log_topics"][3])

                    xdata['txtype']="Axie Auction"
                    xdata['from']=cn(paramValue(eventparams,"_seller"))
                    xdata['to']=cn(paramValue(eventparams,"_buyer"))
                    xdata['ccy']="WETH"
                    xdata['amount']=dispAmt(paramValue(eventparams,"_totalPrice"),"WETH")
                    xdata['ccy2']="AXIE "+ str(axie)
                    xdata['amount2']=1
                    xdata['description']="Auction of axie [" + str(axie) +"] by "+event["_seller"] 

                    
                if eventType == "Transfer" and event["sender_name"] == "Axie":
                    matched="YES"
                    # This is an axie transfer
                    axie = ast.literal_eval(event["raw_log_topics"][3])
     
                    xdata['txtype']="Axie Transfer"
                    xdata['from']=cn(paramValue(eventparams,"from"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=event["sender_contract_ticker_symbol"]
                    xdata['amount']=1                    
                    xdata['description']="Axie Transfer [" + str(axie) +"]" 


                if eventType == "Transfer" and event["sender_name"] == "Decentraland LAND":
                    matched = "YES"
                    # 3rd param is the amount
                    if paramValue(eventparams,"value") :
                        amount = dispAmt(paramValue(eventparams,"value"),event["sender_contract_ticker_symbol"])
                        
                        xdata['txtype']="Transfer Land"
                        xdata['from']=cn(paramValue(eventparams,"from"))
                        xdata['to']=cn(paramValue(eventparams,"to"))
                        xdata['ccy']=event["sender_contract_ticker_symbol"]
                        xdata['amount']=1                    
                        xdata['description']="Transfer of "+ xdata['ccy'] 


                if eventType == "Transfer" and event["sender_name"] != "Axie":
                    matched = "YES"
                    # 3rd param is the amount
                    if paramValue(eventparams,"value") :
                        amount = dispAmt(paramValue(eventparams,"value"),event["sender_contract_ticker_symbol"])
                
                        xdata['txtype']="Transfer"
                        xdata['from']=cn(paramValue(eventparams,"from"))
                        xdata['to']=cn(paramValue(eventparams,"to"))
                        xdata['ccy']=event["sender_contract_ticker_symbol"]
                        xdata['amount']=amount                    
                        xdata['description']="Transfer of "+ xdata['ccy'] 


                if matched != "YES":
      
                    xdata['txtype']="Unknown"
                    xdata['from']=cn(paramValue(eventparams,"from"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=""
                    xdata['amount']=0
                    xdata['description']="Unknown transaction" 
            
                if cnparam == xdata["from"] or cnparam == xdata["to"]:
                    print(xdata)
                    data.append(xdata)
                else:
                    print(cnparam + "!=" + xdata["from"] +" or " + xdata["to"])
    i=i+1

    return data

if len(sys.argv) ==1:
    print("You have to provide an input file")
    exit
else:
    inputFile = sys.argv[1]

from datetime import datetime
import os
now = datetime.now() # current date and time
logdir = "logs/"+now.strftime("%m%d%Y%-H%M%S") 
os.mkdir(logdir )
# This is to populate the cnames (aliases) for accounts in input file
with open(inputFile) as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
        if not line:
            continue
        if re.search("^#", line[0]):
            continue

        if len(line)<3:
            print("Cant process line: ")
            print(*line, sep = "\t")
            continue

        addr = line[1]
        if "ronin:" in line[1]:
            addr = line[1].replace("ronin:","0x")
        
        cnames[addr]=line[0] + " " + line[2].lstrip().rstrip()

# Now process all addresses
with open(inputFile) as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
        if not line:
            continue
        if re.search("^#", line[0]):
            continue

        address=line[1]
        if len(line) >=3 :
            platform=line[2].lower().lstrip().rstrip()
        else:
            print("Error: missing platform in line ", line )
            continue

        print("Processing address "+ platform + " - " + address)
        chainid=""
        if platform == "binance_sc":
            chainid="56"
            print("Platform not supported yet ", platform )
            continue

        elif platform == "ethereum":
            chainid="1"
            print("Platform not supported yet ", platform )
            continue

        elif platform == "polygon":
            chainid="137"
            print("Platform not supported yet ", platform )
            continue

        elif platform == "ronin" :
            chainid="2020"
            

        else:
            print("Unknown platform ", platform )
            break
        


        pageSize = 7000
        covaReq ="https://api.covalenthq.com/v1/"+ chainid + \
        "/address/" + address+"/transactions_v2/?"+ \
        "key="+covaApiKey+ \
        "&page-size="+str(pageSize)+ \
        "&page-number=0"
        
        response = requests.get(covaReq).json()
        if response["error"]:
            print("Covalent backend gave an error, this is the full response:")
            print(response)
            continue
        elif len( response["data"]["items"]) == 0:
            print("No transactions found, this is the full response:")
            print(response)
        else:
            with open(logdir + '/covalent-' +platform + '-' + address +  '.json', 'w') as outfile:
                json.dump(response, outfile)                

            data = extract(response,address, platform)
            with open(logdir+'/pleacc-' +platform + '-' + address + '.json', 'w') as outfile:
                json.dump(data, outfile)
                print("Trying to import: " + str(len(data)))        
                imported=pleidb.saveAcc(platform,data)
                print("Imported: " + str(imported) + " out of " + str(len(data)))
                