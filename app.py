from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        income = float(request.form.get("income", 0))
        rent = float(request.form.get("rent", 0))
        groceries = float(request.form.get("groceries", 0))
        transport = float(request.form.get("transport", 0))
        insurance = float(request.form.get("insurance", 0))

        total_expenses = rent + groceries + transport + insurance
        balance = income - total_expenses

        warning = ""

        # 🚨 Rule 1: Over Budget
        if total_expenses > income:
            warning += "⚠️ You are spending more than you earn! "

        # 🚨 Rule 2: Rent Risk
        if income > 0 and rent > 0.6 * income:
            warning += "⚠️ Rent is too high! "

        # 🚨 Rule 3: Food Risk
        if total_expenses > 0 and groceries > 0.4 * total_expenses:
            warning += "⚠️ Groceries spending too high! "

        result = {
            "balance": round(balance, 2),
            "warning": warning
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)