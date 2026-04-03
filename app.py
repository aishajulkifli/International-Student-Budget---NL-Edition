from flask import Flask, render_template, request, redirect, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = "data.json"

# 💱 Currency rates
rates = {
    "EUR": 1,
    "MYR": 5.1,
    "USD": 1.1,
    "INR": 90,
    "AED": 4.0,
    "TRY": 35,
    "NGN": 1500,
    "CZK": 25,
    "UAH": 42,
    "ANG": 1.95
}

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/", methods=["GET", "POST"])
def login():
    data = load_data()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in data["users"]:
            if data["users"][username]["password"] == password:
                session["user"] = username
                return redirect("/dashboard")
        else:
            data["users"][username] = {
                "password": password,
                "months": {},
                "currency": "EUR"
            }
            save_data(data)
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    data = load_data()
    user = session["user"]

    current_month = datetime.now().strftime("%B %Y")

    if current_month not in data["users"][user]["months"]:
        data["users"][user]["months"][current_month] = {
            "income": 0,
            "expenses": []
        }

    month_data = data["users"][user]["months"][current_month]

    # Default currency
    currency = data["users"][user].get("currency", "EUR")

    if request.method == "POST":

        # Change currency
        if "currency" in request.form:
            currency = request.form["currency"]
            data["users"][user]["currency"] = currency

        # Set income
        if "income" in request.form:
            month_data["income"] = float(request.form["income"])

        # Add expense
        if "amount" in request.form:
            expense = {
                "date": request.form["date"],
                "category": request.form["category"],
                "amount": float(request.form["amount"])
            }
            month_data["expenses"].append(expense)

        save_data(data)

    total_spent = sum(e["amount"] for e in month_data["expenses"])
    balance = month_data["income"] - total_spent

    converted = round(balance * rates.get(currency, 1), 2)

    return render_template(
        "dashboard.html",
        month=current_month,
        income=month_data["income"],
        expenses=month_data["expenses"],
        balance=balance,
        converted=converted,
        currency=currency
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)