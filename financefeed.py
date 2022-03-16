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



def extract(output,roninAddr, platform):
    
    print ("#,Date,TxType,FromAddress,ToAddress, Ccy, Amount, Ccy2, Amount2, Description")
    i = 0
    data=[]

    for item in output["data"]["items"]:
        xdata={
                "block": item["block_height"],
                "tx": item["tx_hash"],
                "seq": str(i),                
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
            
            print(str(i)+","+
            item["block_signed_at"]+","+
            "transfer," +
            cn(item["from_address"])+","+
            cn(item["to_address"])+","+
            ccies[platform] +","+
            f"{amount:.9f}"+",,, Transfer "+ "Tx " + item["tx_hash"])
            
            xdata['txtype']="transfer"
            xdata['from']=item["from_address"]
            xdata['to']=item["to_address"]
            xdata['ccy']=ccies[platform] 
            xdata['amount']=amount
            xdata['description']="Transfer"

            data.append(xdata)
        
         # Lets check if there is gas cost
        if int(item["gas_spent"]* item["gas_price"]) > 0:
            amount=int(item["gas_spent"]* item["gas_price"])/1e18

            print(str(i)+","+
            item["block_signed_at"]+","+
            "Fee "+ platform + "," +
            cn(item["from_address"])+","+
            "Fees paid"+","+
            ccies[platform]+","+
            f"{amount:.9f}"+",,,Fees paid")

            xdata['txtype']="Fee "+ platform 
            xdata['from']=cn(item["from_address"])
            xdata['to']=""
            xdata['ccy']=ccies[platform]
            xdata['amount']=amount
            xdata['description']="Fees paid for transaction" 
            
            data.append(xdata)

        j = 0
        
        for event in item["log_events"]:
            matched = ""
            if event["decoded"]:
                eventType=event["decoded"]["name"]
            
                eventparams = event["decoded"]["params"]

                if eventType == "Swap":
                    matched = "YES"
                    
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
                        

                    print(str(i)+"-"+str(j)+","+
                    event["block_signed_at"]+","+
                    eventType + "," +
                    cn(paramValue(eventparams,"sender"))+","+
                    cn(paramValue(eventparams,"to"))+","+
                    ccy1+","+
                    f"{amount1:.9f}"+","+
                    ccy2+","+
                    f"{amount2:.9f}"+","+
                    "Swap "+event["sender_name"]+" Tx " + event["tx_hash"])

                    xdata['txtype']="Swap"
                    xdata['from']=cn(paramValue(eventparams,"sender"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=ccy1
                    xdata['amount']=amount1
                    xdata['ccy2']=ccy2
                    xdata['amount2']=amount2
                    xdata['description']="Swap "+ event["sender_name"] + " " +xdata['ccy'] + " for " + xdata['ccy2']

                if eventType == "AuctionSuccesful" :
                    matched="YES"
                    # This is an axie transfer
                    axie = ast.literal_eval(event["raw_log_topics"][3])
                    print(str(i)+"-"+str(j)+","+
                        event["block_signed_at"]+","+
                        eventType + "," +
                        cn(paramValue(eventparams,"_seller"))+","+
                        cn(paramValue(eventparams,"_buyer"))+","+
                        "WETH"+","+
                        dispAmt(paramValue(eventparams,"_totalPrice"),"WETH")+
                        ",,,Transfer of axie [" + str(axie) +"] by "+event["sender_name"] )

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
                    print(str(i)+"-"+str(j)+","+
                        event["block_signed_at"]+","+
                        eventType + "," +
                        cn(paramValue(eventparams,"from"))+","+
                        cn(paramValue(eventparams,"to"))+","+
                        event["sender_contract_ticker_symbol"]+","+
                        "1"+
                        ",,,Transfer of axie [" + str(axie) +"] by "+cn(paramValue(eventparams,"from")) + " Tx " + event["tx_hash"] )

                    xdata['txtype']="Axie Transfer"
                    xdata['from']=cn(paramValue(eventparams,"from"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=event["sender_contract_ticker_symbol"]
                    xdata['amount']=1                    
                    xdata['description']="Axie Transfer [" + str(axie) +"]" 


                if eventType == "Transfer" and event["sender_name"] != "Axie":
                    matched = "YES"
                    # 3rd param is the amount
                    if paramValue(eventparams,"value") :
                        amount = dispAmt(paramValue(eventparams,"value"),event["sender_contract_ticker_symbol"])
                        
                        print(str(i)+"-"+str(j)+","+
                        event["block_signed_at"]+","+
                        eventType + "," +
                        cn(paramValue(eventparams,"from"))+","+
                        cn(paramValue(eventparams,"to"))+","+
                        event["sender_contract_ticker_symbol"]+","+
                        f"{amount:.9f}"+
                        ",,,Transfer "+event["sender_name"]+ " Tx " + event["tx_hash"])

                        xdata['txtype']="Transfer"
                        xdata['from']=cn(paramValue(eventparams,"from"))
                        xdata['to']=cn(paramValue(eventparams,"to"))
                        xdata['ccy']=event["sender_contract_ticker_symbol"]
                        xdata['amount']=amount                    
                        xdata['description']="Transfer of "+ xdata['ccy'] 


                    else:
                        print(str(i)+"-"+str(j)+
                        event["block_signed_at"]+","+
                        eventType + "," +
                        cn(paramValue(eventparams,"from"))+","+
                        cn(paramValue(eventparams,"to"))+","+
                        ",,,,"+
                        "Transfer with null value,what to do here? "+ "Tx " + event["tx_hash"])
                
            

                if matched != "YES":
                    print(str(i)+"-"+str(j)+","+
                    event["block_signed_at"]+","+
                    eventType + "," +
                    cn(paramValue(eventparams,"from"))+","+
                    cn(paramValue(eventparams,"to"))+","+
                    ",,,,"+
                    " Tx " + event["tx_hash"])

                    xdata['txtype']="Unknown"
                    xdata['from']=cn(paramValue(eventparams,"from"))
                    xdata['to']=cn(paramValue(eventparams,"to"))
                    xdata['ccy']=""
                    xdata['amount']=0
                    xdata['description']="Unknown transaction" 

            data.append(xdata)
            j=j+1
        i=i+1

    return data

if len(sys.argv) ==1:
    print("You have to provide an input file")
    exit
else:
    inputFile = sys.argv[1]

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
        
        cnames[addr]=line[0] + " " + line[2]

# Now process all addresses
with open(inputFile) as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
        if not line:
            continue
        if re.search("^#", line[0]):
            continue

        roninAddr=line[1]
        if len(line) == 3:
            platform=line[2].lower()
        else:
            platform="ronin"

        print("Processing address "+ platform + " - " + roninAddr)
        chainid=""
        if platform == "binance_sc":
            chainid="56"

        if platform == "ethereum":
            chainid="1"
        
        if platform == "poligon":
            chainid="137"
            
        else:
            chainid="2020"
        
        pageSize = 7000
        covaReq ="https://api.covalenthq.com/v1/"+ chainid + \
        "/address/" + roninAddr+"/transactions_v2/?"+ \
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
            data = extract(response,roninAddr, platform)
            with open('json_data.json', 'w') as outfile:
                json.dump(data, outfile)
                pleidb.saveAcc(platform,data)