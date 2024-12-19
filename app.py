from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import os
import requests
from random import choice  # ランダム選択のために追加

# .envファイルを読み込む
load_dotenv()

# 【初期設定】-----------------------------------------
app = Flask(__name__)

# API
google_maps_api = os.getenv("GOOGLE_MAPS_API")


# ----------------------------------------------------


# Google Maps APIを使って移動時間を取得する関数
def calculate_travel_time(origin_lat, origin_lng, dest_lat, dest_lng, mode):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": mode,
        "key": google_maps_api,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            if data["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
                return float("inf")
            return int(data["rows"][0]["elements"][0]["duration"]["value"] / 60)
        except (IndexError, KeyError):
            return float("inf")
    else:
        return float("inf")


# 条件に合う観光地を取得する関数
def get_suitable_destinations(current_lat, current_lng):
    destinations = [
        {"name": "観光地A", "lat": 35.6895, "lng": 139.6917},
        {"name": "観光地B", "lat": 35.0116, "lng": 135.7681},
    ]

    suitable_destinations = []
    for destination in destinations:
        car_time = calculate_travel_time(
            current_lat, current_lng, destination["lat"], destination["lng"], "driving"
        )
        train_time = calculate_travel_time(
            current_lat, current_lng, destination["lat"], destination["lng"], "transit"
        )

        total_car_time = car_time + 10  # 徒歩時間を仮で10分加算
        total_train_time = train_time + 10

        if total_car_time <= 180:
            suitable_destinations.append(
                {"name": destination["name"], "time": total_car_time, "method": "車 + 徒歩"}
            )
        elif total_train_time <= 180:
            suitable_destinations.append(
                {"name": destination["name"], "time": total_train_time, "method": "電車 + 徒歩"}
            )

    return suitable_destinations


# 地図に現在地を表示するページ
@app.route("/")
def index():
    google_maps = google_maps_api
    return render_template("index.html", google_maps=google_maps)


# 旅行計画作成ページ
@app.route("/create")
def create():
    return render_template("create.html")


# tpcreateページ
@app.route("/tpcreate", methods=["GET", "POST"])
def tpcreate():
    if request.method == "POST":
        data = request.get_json()
        current_lat = data["lat"]
        current_lng = data["lng"]

        # 条件に合う観光地を取得
        results = get_suitable_destinations(current_lat, current_lng)

        # 結果をセッションまたはキャッシュに保存する場合も考慮可能
        return jsonify({"status": "success"})
    else:
        # GETリクエスト時に観光地を1つランダムで選択
        destinations = get_suitable_destinations(35.6895, 139.6917)  # 仮に東京を現在地として使用
        random_destination = choice(destinations) if destinations else None

        # 選択された観光地をテンプレートに渡す
        return render_template("tpcreate.html", results=[random_destination] if random_destination else [])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
