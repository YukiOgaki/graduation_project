from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
import os
from planning import TravelPlanner

# .envファイルを読み込む
load_dotenv()

# 必要なAPIキーを読み込み
google_maps_api = os.getenv("GOOGLE_MAPS_API")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Flaskアプリケーション初期化
app = Flask(__name__)
planner = TravelPlanner(google_maps_api, openai_api_key)


@app.route("/")
def index():
    """Google Mapsを表示するメインページ"""
    return render_template("index.html", google_maps=google_maps_api)


@app.route("/create", methods=["GET", "POST"])
def create():
    """旅行計画を生成するページ"""
    if request.method == "POST":
        # 候補地を取得
        selected_city = planner.location_service.search_city()

        # 観光地を取得
        tourist_spots = planner.location_service.pic_tourist_spot(
            selected_city["latitude"], selected_city["longitude"]
        )

        # プランを生成
        priority_spots = planner.prioritize_spots(tourist_spots)
        travel_plan = planner.create_plan(priority_spots)

        # 生成した計画をテンプレートに渡す
        return render_template("create.html", travel_plan=travel_plan)
    return redirect(url_for("index"))


@app.route("/tpcreate", methods=["POST"])
def tpcreate():
    """観光地候補を表示するページ"""
    data = request.get_json()
    current_lat = data["lat"]
    current_lng = data["lng"]

    # 条件に合う観光地を取得
    results = planner.location_service.pic_tourist_spot(current_lat, current_lng)

    if results:
        return jsonify({"status": "success", "results": results})
    else:
        return jsonify({"status": "fail", "results": []})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
