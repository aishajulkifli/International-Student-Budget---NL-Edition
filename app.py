from sklearn.linear_model import LinearRegression
import numpy as np

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

def predict_survival_days(balance, expenses):
    """
    Predict how many days the remaining balance can last
    using Linear Regression.
    """

    if len(expenses) < 2:
        return None

    daily_totals = {}

    for expense in expenses:
        date = expense["date"]
        amount = expense["amount"]

        if date not in daily_totals:
            daily_totals[date] = 0

        daily_totals[date] += amount

    daily_spending = list(daily_totals.values())

    if len(daily_spending) < 2:
        return None

    X = np.array(daily_spending).reshape(-1, 1)

    y = []

    for spend in daily_spending:
        if spend > 0:
            y.append(balance / spend)
        else:
            y.append(0)

    model = LinearRegression()
    model.fit(X, y)

    avg_spending = np.mean(daily_spending)

    prediction = model.predict([[avg_spending]])

    return max(0, round(prediction[0]))


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

    # Calculate totals
    total_spent = sum(
        e["amount"] for e in month_data["expenses"]
    )

    balance = month_data["income"] - total_spent

    converted = round(
        balance * rates.get(currency, 1),
        2
    )

    # 🤖 AI Survival Predictor
    survival_prediction = predict_survival_days(
        balance,
        month_data["expenses"]
    )

    # 🤖 AI Budget Coach
    advice = "Keep tracking your spending!"

    food_total = 0

    for expense in month_data["expenses"]:
        category = expense["category"].lower()

        if category == "food":
            food_total += expense["amount"]

    if month_data["income"] > 0:

        food_percentage = (
            food_total / month_data["income"]
        ) * 100

        if food_percentage > 30:
            advice = (
                "You spend a large portion of your income on food. "
                "Consider meal planning to save money."
            )

        elif balance < 100:
            advice = (
                "Your balance is running low. "
                "Try reducing non-essential expenses."
            )

    return render_template(
        "dashboard.html",
        month=current_month,
        income=month_data["income"],
        expenses=month_data["expenses"],
        balance=balance,
        converted=converted,
        currency=currency,
        survival_prediction=survival_prediction,
        advice=advice
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)