import json, os
import ccxt
from time import sleep
from datetime import datetime
from binance.client import Client
from binance.enums import *

from flask import Flask, render_template, request, flash

app = Flask(__name__)

#app.secret_key = "manbearpig_MUDMAN888"
apikey=os.environ.get('API_KEY')
apisecret=os.environ.get('API_SECRET')

client = Client(apikey, apisecret)
exchange = ccxt.binance({
    'apiKey': apikey,
    'secret': apisecret,
    'enableRateLimit': True,
    # 'options': {'adjustForTimeDifference': True}
})
exchange.load_markets()


def orderBuy(quantity, symbol, order_price):
    try:
       # market = exchange.market(symbol)
       # response=exchange.create_order({
       #     'symbol': symbol
       #     ,'type': 'LIMIT_MAKER'
       #     ,'side':side
       #     ,'amount':exchange.amount_to_precision(symbol, quantity)
       #     ,'price':exchange.price_to_precision(symbol, order_price)
       # }
       # )
       # print(response)
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=order_price)

        #order = client.create_order(symbol=symbol, side=side, type='BUY', quantity=quantity, timeInForce='GTC', price=order_price)
        print(order)
        response=True
        #print(f"{passphrase} {symbol} Sending order {order_type} - {side} {quantity} {symbol} at {order_price}.")        
        #print(f" {passphrase} {symbol} Not Executed order {order_type} - {side} {quantity} {symbol} at {order_price}.")
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False
    return response

def orderOCO(stopLoss, quantity, symbol, order_price,timeInForce='GTC'):
    try:
        market = exchange.market(symbol)
        response = exchange.private_post_order_oco({
        'symbol': market['id'],
        'side': 'SELL',  # SELL, BUY
        'quantity': exchange.amount_to_precision(symbol, quantity),
        'price': exchange.price_to_precision(symbol, order_price),
        'stopPrice': exchange.price_to_precision(symbol, stopLoss),
        'stopLimitPrice': exchange.price_to_precision(symbol, stopLoss),  # If provided, stopLimitTimeInForce is required
        'stopLimitTimeInForce': timeInForce,  # GTC, FOK, IOC
        # 'listClientOrderId': exchange.uuid(),  # A unique Id for the entire orderList
        # 'limitClientOrderId': exchange.uuid(),  # A unique Id for the limit order
        # 'limitIcebergQty': exchangea.amount_to_precision(symbol, limit_iceberg_quantity),
        # 'stopClientOrderId': exchange.uuid()  # A unique Id for the stop loss/stop loss limit leg
        # 'stopIcebergQty': exchange.amount_to_precision(symbol, stop_iceberg_quantity),
        # 'newOrderRespType': 'ACK',  # ACK, RESULT, FULL
        })
        print(response)
       
    except Exception as e:
        print("An exception occured - {}".format(e))
        return False
    
    return response


@app.route('/')
def welcome():
    return "<h1>Questo è il mio secondo trading bot</h1>"

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
    ticker='BTC/EUR'
    #--------- funziona solo per ordini BUY -----------------
    if side != 'BUY':
        return {
            "code": "Annullato",
            "message": "Si eseguono solo ordini di acquisto."
        }
    #--------- controllo che non vi siano ordini aperti -----
    orders=client.get_open_orders(symbol='BTCEUR')
    if orders:
        return {
            "code": "Annullato",
            "message": "Ordine non evaso per la presenza di un ordine precedente aperto."
        }
    
    #--------- arrotondamenti e calcolo prezzo vendita e stopLoss
    order_price = round(data['strategy']['order_price'],2)
    stopLoss=round(data['strategy']['open'],2)
    diff_P_SL=order_price-stopLoss
    diff_P_TP=diff_P_SL*1.8
    orderOCO_price=round(order_price+diff_P_TP,2)

    #order_response = order(side, quantity, ticker, order_price, data['passphrase'])
    order_response = orderBuy(quantity,'BTCEUR', order_price)

    if order_response:
        #sleep(60)
        orderOCO_response= orderOCO(stopLoss, quantity, ticker, orderOCO_price)
        if orderOCO_response:
            return {
                "code": "success","message": "Order + OrderOCO executed."}
        else:
            print("OrderOCO Failed.")
            return {
            "code": "error","message": "OrderOCO Failed."
        }
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
