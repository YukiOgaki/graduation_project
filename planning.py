from datetime import datetime, timedelta
from dotenv import load_dotenv
from math import ceil
from maps import LocationService
from openai import OpenAI
import os

# .envの読み込み
load_dotenv()


# +--------------------------------------------------------+
# | 本格的にスケジューリングするクラス                        |
# +--------------------------------------------------------+
class TravelPlanner:
    def __init__(self, google_maps_api, openai_api_key):
        self.google_maps_api = google_maps_api
        self.client = OpenAI(api_key=openai_api_key)
        self.location_service = LocationService(api_key=self.google_maps_api)
        self.current_time = datetime.now()
        self.current_location = self.location_service.get_current_location()

    # 1、助っ人GPTを投入する関数
    def chat_gpt(self, model, system, user_message):
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        return completion.choices[0].message.content

    # 2、優先順位でソートする関数
    def prioritize_spots(self, spots):
        for spot in spots:
            car_time = (
                self.location_service.gmaps.distance_matrix(
                    origins=(self.current_location["latitude"], self.current_location["longitude"]),
                    destinations=(spot["lat"], spot["lng"]),
                    mode="driving",
                )["rows"][0]["elements"][0]
                .get("duration", {})
                .get("value", float("inf"))
                // 60
            )
            spot["staytime"] = 90
            spot["priority"] = car_time

        spots = sorted(spots, key=lambda x: (x["priority"], -x["lat"]))
        return spots

    # 3、時間を15分おきに表示する関数
    @staticmethod
    def round_up_to_nearest_quarter(hour, minute):
        minute = ceil(minute / 15) * 15
        if minute == 60:
            hour += 1
            minute = 0
        return hour, minute

    # 4、日程表通りに並べる関数
    def create_plan(self, spots):
        plan = []
        start_time = datetime(self.current_time.year, self.current_time.month, self.current_time.day, 8, 0)

        for idx, spot in enumerate(spots):
            travel_time = (
                0
                if idx == 0
                else (
                    self.location_service.gmaps.distance_matrix(
                        origins=(spots[idx - 1]["lat"], spots[idx - 1]["lng"]),
                        destinations=(spot["lat"], spot["lng"]),
                        mode="driving",
                    )["rows"][0]["elements"][0]
                    .get("duration", {})
                    .get("value", float("inf"))
                    // 60
                )
            )
            stay_time = spot["staytime"]

            end_time = start_time + timedelta(minutes=travel_time + stay_time)
            end_hour, end_minute = self.round_up_to_nearest_quarter(end_time.hour, end_time.minute)
            end_time = end_time.replace(hour=end_hour, minute=end_minute)

            plan.append(
                {
                    "time": start_time.strftime("%H:%M"),
                    "comment": self.chat_gpt(
                        "gpt-4o-mini",
                        "あなたは優秀な旅行プランナーです",
                        f"{spot['name']}を10文字前後で紹介してください。※「。」は不要",
                    ),
                    "place": self.chat_gpt(
                        "gpt-4o-mini",
                        "あなたは優秀な旅行プランナーです",
                        f"{spot['name']}の日本語名。※文章は不要。名詞のみ。",
                    ),
                    "area": "観光地",
                    "staytime": travel_time if idx > 0 else stay_time,
                    "url": spot["url"],
                }
            )

            if end_time.hour >= 20:
                break

            start_time = end_time

        return plan


if __name__ == "__main__":
    # APIキーを環境変数から取得
    google_maps_api = os.getenv("GOOGLE_MAPS_API")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # TravelPlannerの初期化
    planner = TravelPlanner(google_maps_api, openai_api_key)

    # 観光地情報を取得
    selected_city = planner.location_service.search_city()
    tourist_spots = planner.location_service.pic_tourist_spot(
        selected_city["latitude"], selected_city["longitude"]
    )

    # プランの生成
    priority_spots = planner.prioritize_spots(tourist_spots)
    travel_plan = planner.create_plan(priority_spots)
    
    # プランの出力
    for plan in travel_plan:
        print(
            f"{plan['time']}\t{plan['comment']}\t{plan['place']}\t{plan['area']}\t{plan['staytime']}\t{plan['url']}"
        )
