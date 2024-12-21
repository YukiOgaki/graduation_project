from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import os
import requests
from random import choice
from datetime import datetime, timedelta
from math import ceil
from maps import LocationService
from openai import OpenAI
from planning import TravelPlanner


# -----------------------------------------+
# 初期設定                                  |
# -----------------------------------------+
# .envファイルを読み込む
load_dotenv()

# 必要なAPIキーを読み込み
google_maps_api = os.getenv("GOOGLE_MAPS_API")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openai_api_key = os.getenv("OPENAI_API_KEY")


# 初期化
app = Flask(__name__)
planner = TravelPlanner(google_maps_api, openai_api_key)

# 外部関数を定義しておく
selected_city = planner.location_service.search_city()  # 候補地をくるくるドン！
tourist_spots = planner.location_service.pic_tourist_spot(
    selected_city["latitude"], selected_city["longitude"]
)  # くるくるドン！の周り観光地

# プランの生成
priority_spots = planner.prioritize_spots(tourist_spots)  # 優先順位順
travel_plan = planner.create_plan(priority_spots)   # 最終形態


if __name__ == "__main__":
    for plan in travel_plan:
        print(f"{plan['time']}\t{plan['comment']}\t{plan['place']}\t{plan['area']}\t{plan['staytime']}")

