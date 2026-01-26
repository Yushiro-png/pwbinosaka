from flask import Flask, render_template, request, redirect
import os
import json

app = Flask(__name__)
DATA_FILE = "reservations.json"

# ==== ユーティリティ ====
def load_reservations():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_reservations(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==== メインページ（予約） ====
@app.route("/", methods=["GET", "POST"])
def index():
    reservations = load_reservations()
    all_seats = [f"A{i}" for i in range(1, 21)]
    available_seats = [s for s in all_seats if s not in reservations]

    if request.method == "POST":
        seat = request.form["seat"]
        name = request.form["name"]
        email = request.form["email"]

        if seat in reservations:
            return "この座席はすでに予約されています。"

        reservations[seat] = {"name": name, "email": email}
        save_reservations(reservations)
        return redirect("/success")

    return render_template("index.html", seats=available_seats)

# ==== 予約成功 ====
@app.route("/success")
def success():
    return render_template("success.html")

# ==== キャンセルページ ====
@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    message = ""
    if request.method == "POST":
        seat = request.form["seat"]
        name = request.form["name"]
        email = request.form["email"]
        reservations = load_reservations()

        if seat in reservations and reservations[seat]["name"] == name and reservations[seat]["email"] == email:
            del reservations[seat]
            save_reservations(reservations)
            return redirect("/cancel_success")
        else:
            message = "一致する予約が見つかりませんでした。"

    return render_template("cancel.html", message=message)

# ==== キャンセル成功 ====
@app.route("/cancel_success")
def cancel_success():
    return render_template("cancel_success.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
