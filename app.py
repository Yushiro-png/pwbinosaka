from flask import Flask, render_template, request, redirect
import os
import json
import requests

app = Flask(__name__)
DATA_FILE = "/data/reservations.json"

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1466489476963500113/U1mHM6pSq7A3Q7KHRETgdWCk63U9MKM9eZOT2vH6M2xWio2kPaEXctBN63K_8E85NtL2"

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

def calculate_price(seat, category, payment):
    row = seat.split("-")[0]
    if row == "A":
        return 8000
    elif row in ["B", "C", "D", "E", "F", "G", "H"]:
        if category == "大人":
            price = 6000
        elif category == "学生":
            price = 5000
        else:
            price = 4000
    else:
        if category == "大人":
            price = 4000
        elif category == "学生":
            price = 3000
        else:
            price = 2000
    if payment == "事前振込" and row != "A":
        price -= 500

    return price

def notify_discord(seat, name, email, category, payment, price):
    message = f"""
🎫 **新しい予約が入りました！**
座席：{seat}
名前：{name}
メールアドレス:{email}
区分：{category}
支払い：{payment}
料金：{price:,}円
"""
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Discord通知失敗:", e)

def notify_discord_cancel(seat, name, email):
    message = f"""
❌ **予約がキャンセルされました**
座席：{seat}
名前：{name}
メールアドレス：{email}
"""
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Discordキャンセル通知失敗:", e)

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
        
        price = calculate_price(selected_seat, category, payment)

        reservations[selected_seat] = {
            "name": name,
            "email": email,
            "category": category,
            "payment": payment,
            "price": price
        }
        save_reservations(reservations)

        notify_discord(selected_seat, name, email, category, payment, price)
        
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

            notify_discord_cancel(seat, name, email)
            
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