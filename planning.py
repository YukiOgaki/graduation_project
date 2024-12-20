from datetime import datetime, timedelta
from math import ceil
from maps import LocationService
from dotenv import load_dotenv
import os
import openai

# .envの読み込み
load_dotenv()

# 必要なAPIキーを読み込み
google_maps_api = os.getenv("GOOGLE_MAPS_API")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# LocationServiceを初期化
location_service = LocationService(api_key=google_maps_api)

# 現在の時間を取得
current_time = datetime.now()

# 現在地を取得
current_location = location_service.get_current_location()

# 観光地情報を取得
selected_city = location_service.search_city()
tourist_spots = location_service.pic_tourist_spot(selected_city["latitude"], selected_city["longitude"])


# 優先順位でソートする関数
def prioritize_spots(spots, current_location):
    for spot in spots:
        # 車での移動時間を計算（分単位）
        car_time = (
            location_service.gmaps.distance_matrix(
                origins=(current_location["latitude"], current_location["longitude"]),
                destinations=(spot["lat"], spot["lng"]),
                mode="driving",
            )["rows"][0]["elements"][0]
            .get("duration", {})
            .get("value", float("inf"))
            // 60
        )

        # 滞在時間を仮で設定 (平均90分)
        spot["staytime"] = 90
        spot["priority"] = car_time  # 車移動時間を優先順位に設定

    # 車移動時間順、人気度（仮にlat降順とする）でソート
    spots = sorted(spots, key=lambda x: (x["priority"], -x["lat"]))
    return spots


prioritys = prioritize_spots(tourist_spots, current_location)


# 日程表を作成
def round_up_to_nearest_quarter(hour, minute):
    # 分を15分単位で繰り上げ
    minute = ceil(minute / 15) * 15
    if minute == 60:
        hour += 1
        minute = 0
    return hour, minute


def create_plan(priority):
    plan = []
    start_time = datetime(current_time.year, current_time.month, current_time.day, 8, 0)  # 朝8時出発

    for idx, spot in enumerate(priority):
        if idx == 0:
            travel_time = 0  # 初回は移動時間なし
        else:
            travel_time = (
                location_service.gmaps.distance_matrix(
                    origins=(priority[idx - 1]["lat"], priority[idx - 1]["lng"]),
                    destinations=(spot["lat"], spot["lng"]),
                    mode="driving",
                )["rows"][0]["elements"][0]
                .get("duration", {})
                .get("value", float("inf"))
                // 60
            )

        stay_time = spot["staytime"]

        # 計算して時間を追加
        end_time = start_time + timedelta(minutes=travel_time + stay_time)
        end_hour, end_minute = round_up_to_nearest_quarter(end_time.hour, end_time.minute)
        end_time = end_time.replace(hour=end_hour, minute=end_minute)

        # プランに追加
        plan.append(
            {
                "time": start_time.strftime("%H:%M"),
                "comment": "車で移動" if idx > 0 else "出発！車で移動",
                "place": spot["name"],
                "area": "観光地",
                "staytime": travel_time if idx > 0 else stay_time,
            }
        )

        # 終了時間が20:00を超えたら終了
        if end_time.hour >= 20:
            break

        start_time = end_time

    return plan


plans = create_plan(prioritys)

print(f"優先順位でソート:{prioritys}")
print(f"旅行プラン:{plans}")
