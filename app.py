# from paddleocr import PaddleOCR,draw_ocr
# ocr = PaddleOCR(lang='en') # need to run only once to download and load model into memory
# img_path = './img1.jpeg'
# result = ocr.ocr(img_path, cls=False)
# for idx in range(len(result)):
#     res = result[idx]
#     for line in res:
#         print(line)

# import pywhatkit

# # Send a WhatsApp Message to a Contact at 1:30 PM
# pywhatkit.sendwhatmsg("+919962689777", "watsapp testing", 17, 46)

from flask import Flask, request, jsonify
import random
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

app = Flask(__name__, template_folder='./cred/surfgeo-sale.json')
# app.config['SECRET_KEY'] = 'your_secret_key'

# Configure Firebase credentials
cred = credentials.Certificate('./cred/surfgeo-sale.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

FAST2SMS_API_KEY = 'YX9TfQk4yRNqk78SRiLWLDF3LIUMcTMshWZOlCjLAYVTSrHUc1n0SD8EtWjU'

@app.route('/', methods=['GET'])
def api_check():
    return "api work"
@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.form.get('phone_number')

    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Send the OTP via Fast2SMS
    url = "https://www.fast2sms.com/dev/bulk"
    payload = f"sender_id=FSTSMS&message=Your OTP is {otp}&language=english&route=p&numbers={phone_number}"
    headers = {
        'authorization': FAST2SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }
    data= {
        'otp': otp,
        'timestamp': int(time.time())
    }
    db.collection(u'store_file_name_log').document(phone_number).set(data)
    # otp_ref = db.collrence(f'otp/{phone_number}')
    # otp_ref.set({
    #     'otp': otp,
    #     'timestamp': int(time.time())
    # })

    response = requests.request("POST", url, data=payload, headers=headers)

    return jsonify({'message': 'OTP sent successfully.'})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    phone_number = request.form.get('phone_number')
    otp = request.form.get('otp')

    # Retrieve the stored OTP and timestamp from Firebase Realtime Database
# Retrieve a specific document from Firestore
    document_ref = db.collection('store_file_name_log').document(phone_number)
    document = document_ref.get()
    if document.exists:
        otp_data = document.to_dict()
    # print(otp_data)
        if otp_data is not None and otp == otp_data['otp']:
            # Calculate the time elapsed since OTP generation
            current_timestamp = int(time.time())
            elapsed_time = current_timestamp - otp_data['timestamp']
            # print(elapsed_time)
            # elapsed_time = 672
            # minutes = elapsed_time / 60
            # print(minutes)
            # seconds = int()*60
            # print(seconds)
            if elapsed_time<60:
                return jsonify({'message': 'successfull login.'}), 200
            else:
                return jsonify({'message': 'otp time duration is ended please try again.'}), 200
        else:
            return jsonify({'message': 'Invalid OTP.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
