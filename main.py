import re
from flask import Flask, render_template, request

PATTERNS = {
    'debit': {
        "INR": [
            r'INR\s(?P<amount>[\d,]+\.\d{2})\sspent\son\s(?P<bank>[A-Za-z]+\sBank)\sCard\s(?P<card>[A-Z]{2}\d{4})\son\s(?P<date>\d{1,2}-[A-Za-z]{3}-\d{2})\sat\s(?P<merchant>[^\.]+)\.\sAvl\sLmt:\sINR\s(?P<limit>[\d,]+\.\d{2})\.\sTo\sdispute,call\s(?P<phone1>\d+)/SMS\sBLOCK\s(?P<code>\d+)\sto\s(?P<phone2>\d+)',
        ],
        "HDFC": [
            r'(?P<bank>HDFC\sBank)\:\sRs\s(?P<amount>[\d,]+\.\d{2})\sdebited\ from\sa\/c\s(?P<card>[*]{2}\d{4})\son\s(?P<date>\d{1,2}-\d{2}-\d{2})\sto\sVPA\s(?P<merchant>[^\(]+).*',
        ],
        "You": [
            r'You\'ve\sspent\sRs\.(?P<amount>[\d,]+\.\d{2})\sOn\s(?P<bank>HDFC\sBank)\sCREDIT\sCard\s(?P<card>xx\d{4})\sAt\s(?P<merchant>[\w\ ]+)\sOn\s(?P<date>\d{4}-\d{2}-\d{2}):(?P<time>\d{2}:\d{2}:\d{2})\sAvl\sbal:\sRs\.(?P<limit>[\d,]+\.\d{2})\sCurr\sO\/s:\sRs\.(?P<current_outstanding>\d+\.\d{2})\sNot\syou\?Call\s(?P<contact_number>\d+)',
            r'You\'ve spent INR (?P<amount>[\d,]+\.\d{2}) at 17:44 on (?P<date>[a-zA-Z]+ \d{2}, \d{4}). If it wasn\'t done by you, ping us on the Fi app. -(?P<bank>Federal Bank)'
        ],
        "ICICI": [
            r'(?P<bank>ICICI Bank) Acc (?P<card>[A-Z0-9]+) debited Rs. (?P<amount>\d+\.\d{2}) on (?P<date>\d{2}-[A-Za-z]{3}-\d{2}) (?P<merchant>.+)\.Avl Bal Rs. (?P<limit>\d+\.\d+)\. To dispute call (?P<phone1>\d+) or SMS BLOCK (?P<phone2>\d+) to (?P<phone3>\d+)'
        ],
        "RS": [
            r'RS\.(?P<amount>[\d,]+\.\d{2}) spent on your (?P<bank>SBI Credit Card) ending (?P<card>\d{4}) at (?P<merchant>[^o]+) on (?P<date>\d{2}\/\d{2}\/\d{2})\. Trxn\. not done by you\? Report at .*'
        ],
        "Rs": [
            r'Rs\. (?P<amount>[\d,]+\.\d{2}) spent on card (?P<card>\d{4}) on (?P<date>\d{2}-[A-Z]{3}-\d{2}) at (?P<merchant>[^.]+)\. Limit available=Rs\. (?P<limit>[\d,]+\.\d{2})\.If not done by you, click www\.(?P<bank>citi)\.asia\/DIS\?cn=.*'
        ],
        "Hope": [
            r'Hope you and your family stay safe and healthy\! INR (?P<amount>[\d,]+\.\d{2}) spent on your (?P<bank>IDFC FIRST Bank Credit Card) ending (?P<card>XX\d{4}) at (?P<merchant>[\w\ ]+) on (?P<date>\d{2}-[A-Z]{3}-\d{4}) at 04:15 PM\. Avbl limit: RS\.(?P<limit>[\d,]+\.\d{2})\. If not done by you.*'
        ],
        "Transaction": [
            r'Transaction Successful! INR (?P<amount>[\d,]+\.\d{2}) spent on your (?P<bank>IDFC FIRST Bank Credit Card) ending (?P<card>XX\d{4}) at (?P<merchant>.+) on (?P<date>\d{2}-[A-Z]{3}-\d{4}) at 07:39 PM\. Avbl limit: RS\.(?P<limit>[\d,]+\.\d{2})\. If not done by you.*'
        ],
        "Your": [
            r'Your (?P<bank>Niyo DCB) account (?P<card>\d+) is debited for (?P<amount>[\d,]+\.\d{2})\. Please contact customer care if not you. -Niyo',
        ],
        "Hello": [
            r'Hello \w+, tranx for RS\.(?P<amount>[\d,]+\.\d{2}) completed on your (?P<bank>NiYO card) on (?P<date>[a-zA-Z]+, \d{2} [a-zA-Z]+ \d{4}) (?P<time>\d{2}:\d{2} (A|P)M) at (?P<merchant>.+)\. Current account balance is RS\.(?P<limit>[\d,]+\.\d{2})\. Thank You!'
        ],
        "Sent": [
            r'Sent Rs\.(?P<amount>[\d,]+\.\d{2}) from (?P<bank>Kotak Bank) AC (?P<card>XXXX\d{4}) to (?P<merchant>.+) on (?P<date>\d{2}-\d{2}-\d{2})\.UPI Ref 123456789012\.Bal:(?P<limit>[\d,]+\.\d{2})\.Click kotak\.com/fraud for dispute'
        ]
    },
    'credit': {
        "ICICI": [
            r'(?P<bank>ICICI Bank) Account (?P<account_num>[A-Z0-9]+) credited\:Rs\. (?P<amount>[\d,]+\.\d{2}) on (?P<date>\d{2}-[A-Za-z]{3}-\d{2})\. Info (?P<recipient>[^\.]+)\. Available Balance is Rs\. (?P<balance>[\d,]+\.\d{2}).*',
        ],
        "We": [
            r'We have credited your (?P<bank>ICICI Bank) Account (?P<account_num>[A-Z0-9]+) with INR (?P<amount>[\d,]+\.\d{2}) on (?P<date>\d{2}-[A-Za-z]{3}-\d{2})\. Info\:(?P<recipient>[^\.]+)\. The Available Balance is INR (?P<balance>[\d,]+\.\d{2}).*'
        ],
        "Your": [
            r'Your (?P<bank>Kotak Bank) a/c (?P<account_num>x\d{4}) credited with Rs (?P<amount>[\d,]+\.\d{2}) from (?P<recipient>Kotak Bank A/c x\d{4}) on (?P<date>\d{2}-\d{2}-\d{4})\.Ref No\.123456789012\.Bal:(?P<balance>[\d,]+\.\d{2}).*'
        ]
    }
}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/parse_sms', methods=['POST'])
def parse_sms():
    # Get the SMS text from the request body
    sms_text = request.json.get('sms_text')
    first_word = re.split('[^a-zA-Z]', sms_text)[0]

    if any(word in sms_text.lower() for word in ["spent", "debited", "withdrawn", "tranx", "sent"]):
        if first_word in PATTERNS['debit']:
            entities = {}
            for pattern in PATTERNS['debit'][first_word]:
                match = re.search(pattern, sms_text)
                if match:
                    groups = match.groupdict()
                    entities['type'] = 'debit'
                    entities['amount'] = groups.get("amount", None)
                    entities['bank'] = groups.get("bank", None)
                    entities['card'] = groups.get("card", None)
                    entities['date'] = groups.get("date", None)
                    entities['merchant'] = groups.get("merchant", None)
                    entities['limit'] = groups.get("limit", None)
                    return entities
    elif any(word in sms_text.lower() for word in ["credited"]):
        if first_word in PATTERNS['credit']:
            entities = {}
            for pattern in PATTERNS['credit'][first_word]:
                match = re.search(pattern, sms_text)
                if match:
                    groups = match.groupdict()
                    entities['type'] = 'credit'
                    entities['amount'] = groups.get("amount", None)
                    entities['bank'] = groups.get("bank", None)
                    entities['account_num'] = groups.get("account_num", None)
                    entities['date'] = groups.get("date", None)
                    entities['sender'] = groups.get("sender", None)
                    entities['balance'] = groups.get("balance", None)
                    return entities
    else:
        entities['error'] = 'no match found'

    return entities

if __name__ == '__main__':
    app.run(debug=True)
