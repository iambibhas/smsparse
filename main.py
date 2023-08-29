from flask import Flask, render_template, request

app = Flask(__name__)

import re

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parse_sms', methods=['POST'])
def parse_sms():
    # Get the SMS text from the request body
    sms_text = request.json.get('sms_text')
    entities = {}

    if set(sms_text.lower().split(" ")).intersection(set(["spent", "debited", "withdrawn"])):
        debit_patterns = {
            "INR": [
                r'INR\s(?P<amount>[\d,]+\.\d{2})\sspent\son\s(?P<bank>[A-Za-z]+\sBank)\sCard\s(?P<card>[A-Z]{2}\d{4})\son\s(?P<date>\d{1,2}-[A-Za-z]{3}-\d{2})\sat\s(?P<merchant>[^\.]+)\.\sAvl\sLmt:\sINR\s(?P<limit>[\d,]+\.\d{2})\.\sTo\sdispute,call\s(?P<phone1>\d+)/SMS\sBLOCK\s(?P<code>\d+)\sto\s(?P<phone2>\d+)',
            ],
            "HDFC": [
                r'(?P<bank>HDFC\sBank)\:\sRs\s(?P<amount>[\d,]+\.\d{2})\sdebited\ from\sa\/c\s(?P<card>[*]{2}\d{4})\son\s(?P<date>\d{1,2}-\d{2}-\d{2})\sto\sVPA\s(?P<merchant>[^\(]+).*',
            ],
            "You've": [
                r'You\'ve\sspent\sRs\.(?P<amount>[\d,]+\.\d{2})\sOn\s(?P<bank>HDFC\sBank)\sCREDIT\sCard\s(?P<card>xx\d{4})\sAt\s(?P<merchant>[\w\ ]+)\sOn\s(?P<date>\d{4}-\d{2}-\d{2}):(?P<time>\d{2}:\d{2}:\d{2})\sAvl\sbal:\sRs\.(?P<limit>[\d,]+\.\d{2})\sCurr\sO\/s:\sRs\.(?P<current_outstanding>\d+\.\d{2})\sNot\syou\?Call\s(?P<contact_number>\d+)'
            ]
        }

        first_word = sms_text.split(" ")[0]
        if first_word in debit_patterns:
            for pattern in debit_patterns[first_word]:
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
                else:
                    print("No match found for pattern: ", pattern, flush=True)

    return entities

if __name__ == '__main__':
    app.run()
