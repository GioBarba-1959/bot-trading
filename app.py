from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

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
