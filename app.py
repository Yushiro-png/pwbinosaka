from flask import Flask, render_template, request, redirect
import os
import json

app = Flask(__name__)
DATA_FILE = "/data/reservations.json"

def load_reservations():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_reservations(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_seat_list():
    seats = []
    for row in "ABCDEFGHJKLM":
        if row == "A":
            seat_range = range(6, 18)
        elif row == "B":
            seat_range = range(6, 18)
        else:
            seat_range = range(1, 23)
        for seat in seat_range:
            seats.append(f"{row}-{seat}")
    return seats

@app.route("/", methods=["GET", "POST"])
def index():
    reservations = load_reservations()
    all_seats = generate_seat_list()
    available_seats = [s for s in all_seats if s not in reservations]

    if request.method == "POST":
        selected_seat = request.form["seat"]
        name = request.form["name"]
        email = request.form["email"]
        category = request.form["category"]
        payment = request.form["payment"]

        if selected_seat in reservations:
            return f"{selected_seat} はすでに予約されています。戻って再選択してください。"

        reservations[selected_seat] = {
            "name": name,
            "email": email,
            "category": category,
            "payment": payment
        }
        save_reservations(reservations)
        return redirect("/success")

    return render_template("index.html", seats=available_seats)

@app.route("/success")
def success():
    return render_template("success.html")

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

@app.route("/cancel_success")
def cancel_success():
    return render_template("cancel_success.html")

@app.route("/admin")
def admin():
    reservations = load_reservations()
    return render_template("admin.html", reservations=reservations)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)