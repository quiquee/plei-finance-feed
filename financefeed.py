import requests
import csv
import json
import sys
import ast

cnames={
    "0x213073989821f738a7ba3520c3d31a1f9ad31bbd": "Marketplace Contract", 
    "0x0000000000000000000000000000000000000000": "0x0"
}

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



def extract(output,roninAddr):
    
    print ("#,Date,TxType,FromAddress,ToAddress, Ccy, Amount, Ccy2, Amount2, Description")
    i = 0
    for item in output["data"]["items"]:
        amount = 0
        description=""
        # Lets check if there is RON amount
        if int(item["value"]) > 0 :
            amount=dispAmt(item["value"],"RON")
            
            print(str(i)+","+
            item["block_signed_at"]+","+
            "transfer," +
            cn(item["from_address"])+","+
            cn(item["to_address"])+","+
            "RON"+","+
            f"{amount:.9f}"+",,,RON Transfer "+ "Tx " + item["tx_hash"])

        # This must be a ERC20 transfer (SLP most likely)
        if int(item["value"]) == 0 :
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
                            ",,,Transfer of axie [" + str(axie) +"] by "+event["sender_name"] + " Tx " + event["tx_hash"] )

                        
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
                            ",,,Transfer of axie [" + str(axie) +"] by "+event["sender_name"] + " Tx " + event["tx_hash"] )

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

                j=j+1

        # Lets check if there is gas cost
        if int(item["gas_spent"]* item["gas_price"]) > 0:
            amount=int(item["gas_spent"]* item["gas_price"])/1e18

            print(str(i)+","+
            item["block_signed_at"]+","+
            "Fee,"+
            cn(item["from_address"])+","+
            "Fees paid"+","+
            "RON"+","+
            f"{amount:.9f}"+",,,Fees paid in Ronin")

        i=i+1

covaApiKey = "ckey_55f1971fa82749ae89275572b5b"
with open("accuntlist.tsv") as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
        addr = line[1].replace("ronin:","0x")

        cnames[addr]=line[0] + " " + line[2]

with open("accuntlist.tsv") as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
        roninAddr=line[1]
        print("Processing address "+ roninAddr)
        covaReq ="https://api.covalenthq.com/v1/2020/address/" + roninAddr+"/transactions_v2/?key="+covaApiKey+"&page-size=7000&page-number=0"

        r = requests.get(covaReq)
        extract(r.json(),roninAddr)
