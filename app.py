import json, os

from binance.client import Client
from binance.enums import *

from flask import Flask, render_template, request, flash

app = Flask(__name__)

app.secret_key = "manbearpig_MUDMAN888"
apikey=os.environ.get('API_KEY')
apisecret=os.environ.get('API_SECRET')

client = Client(os.environ.get('API_KEY'), os.environ.get('API_SECRET'))

def order(side, quantity, symbol, order_price, passphrase, order_type=ORDER_TYPE_LIMIT, timeInForce=TIME_IN_FORCE_GTC):
    try:
        print(f"{passphrase} {symbol} Sending order {order_type} - {side} {quantity} {symbol} at {order_price}.")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, timeInForce=timeInForce, price=order_price)
        #print(f" {passphrase} {symbol} Not Executed order {order_type} - {side} {quantity} {symbol} at {order_price}.")
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False

    return order

@app.route('/')
def welcome():
    return "<h1>Questo è il mio primo trading bot</h1>"

@app.route("/hello")
def index():
	flash("Qual'è il tuo nome?")
	return render_template("index.html")

@app.route("/greet", methods=['POST', 'GET'])
def greeter():
	flash("Hi " + str(request.form['name_input']) + ", great to see you!")
	return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['passphrase'] != os.environ.get('WEBHOOK_PASSPHRASE'):
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }
    side = data['strategy']['order_action'].upper()
    quantity = 0.001  #data['strategy']['order_contracts']
    ticker = data['ticker'].upper()
    order_price = round(data['strategy']['order_price'],2)

    order_response = order(side, quantity, ticker, order_price, data['passphrase'])


    if order_response:
        return {
            "code": "success",
            "message": "Order executed."
        }
    else:
        print("Order Failed.")

        return {
            "code": "error",
            "message": "Order Failed."
        }
