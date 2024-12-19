# 2で一気に観光地検索の状態

from dotenv import load_dotenv
import googlemaps
import os
import requests


class LocationService:
    def __init__(self, api_key):
        """
        Initialize the LocationService with Google Maps API key.

        :param api_key: str - Google Maps API key
        """
        if not api_key:
            raise ValueError("Google Maps API key is missing.")
        self.api_key = api_key
        self.gmaps = googlemaps.Client(key=api_key)
        self.current_location = None

    # 1、現在地を取得
    def get_current_location(self):
        """
        出力形式:{'latitude': 12.0000000, 'longitude': 34.0000000, 'accuracy': 20.0000000000}
            ※latitude=緯度  longitude=経度  accuracy=精度(メートル算出)

        LocationService(google_maps_api).get_current_location()["latitude"]
        で、緯度である「12.0000000」がfloat型で出力される。
        """
        try:
            # Googleマップクライアントを初期化
            result = self.gmaps.geolocate()

            if "location" in result:
                latitude = result["location"]["lat"]  # 緯度
                longitude = result["location"]["lng"]  # 経度
                accuracy = result.get("accuracy", "Unknown")  # 誤差 (メートル)

                self.current_location = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy,
                }
                return self.current_location
            else:
                return {"error": "Location information not available"}
        except Exception as e:
            return {"error": str(e)}

    # 2、現在地から条件を追加して、観光地を検索
    def search_tourist_attraction(self, radius=250000, time=180, type="tourist_attraction"):
        """
        現在地周辺から条件をつけて観光スポットを検索。

        :param radius: int - 半径(m)内で検索 (default: 250000=250km)
        :param time: int - 移動時間の制限 (default: 180分)
        :param type: str - 検索対象 (default: "tourist_attraction") → デフォルトで観光地
        :return: list - 観光スポット一覧とエラーメッセージ
        """
        if not self.current_location:
            return {"error": "現在地が定義されていません。get_current_location()を発動させてください"}

        # Google Places APIのエンドポイント
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        # リクエストパラメータ
        params = {
            "location": f"{self.current_location['latitude']},{self.current_location['longitude']}",
            "radius": radius,  # 半径(m)
            "time": time,  # 移動時間を指定
            "type": type,  # 観光地を指定
            "key": self.api_key,
        }

        # リクエスト送信
        response = requests.get(url, params=params)
        data = response.json()

        # 結果を表示
        if data.get("status") == "OK":
            results = []
            for place in data["results"]:
                # ホテル（宿泊施設）を除外
                if "hotel" in place.get("types", []) or "lodging" in place.get("types", []):
                    continue

                # 最大15件まで取得
                if len(results) >= 15:
                    break

                # Google Distance Matrix APIで移動時間を計算
                distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                distance_params = {
                    "origins": f"{self.current_location['latitude']},{self.current_location['longitude']}",
                    "destinations": f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}",
                    "mode": "driving",  # 車モード（徒歩は自動で含まれる）
                    "key": self.api_key,
                }
                distance_response = requests.get(distance_url, params=distance_params)
                distance_data = distance_response.json()

                if distance_data.get("status") == "OK":
                    # 移動時間を取得（秒単位）
                    travel_time_seconds = (
                        distance_data["rows"][0]["elements"][0].get("duration", {}).get("value", 0)
                    )
                    travel_time_minutes = travel_time_seconds / 60  # 分単位に変換

                    # 移動時間が制限を超える場合はスキップ
                    if travel_time_minutes > time:
                        continue

                    # 半径内かどうかの確認はすでにAPIが保証

                    # 観光地情報をリストに追加
                    results.append(
                        {
                            "name": place["name"],
                            "address": place.get("vicinity", "住所情報なし"),
                            "travel_time": travel_time_minutes,  # 移動時間を記録
                        }
                    )
            return results
        else:
            return {"error": data.get("status", "Unknown error occurred")}

    # 2、現在地から条件を追加して、地名を検索
    def search_city(self, radius=250000, time=180, type="locality"):
        """
        現在地周辺から条件をつけて地名を検索。

        :param radius: int - 半径(m)内で検索 (default: 250000=250km)
        :param time: int - 移動時間の制限 (default: 180分)
        :param type: str - 検索対象 (default: "locality") → 地名検索
        :return: dict - 条件に合う地名1件またはエラーメッセージ
        """
        if not self.current_location:
            return {"error": "現在地が定義されていません。get_current_location()を実行してください。"}

        # Google Places APIのエンドポイント
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        # リクエストパラメータ
        params = {
            "location": f"{self.current_location['latitude']},{self.current_location['longitude']}",
            "radius": radius,  # 半径(m)
            "type": type,  # 地名を指定 ("locality" は都市や市町村に該当)
            "key": self.api_key,
        }

        try:
            # Google Places APIリクエスト
            response = requests.get(places_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK":
                filtered_results = []

                for place in data["results"]:
                    # 移動時間を計算する関数
                    def calculate_travel_time(mode):
                        if self.current_location is not None:
                            latitude = self.current_location["latitude"]
                            longitude = self.current_location["longitude"]
                            distance_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                            distance_params = {
                                "origins": f"{latitude, longitude}",
                                "destinations": f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}",
                                "mode": mode,
                                "key": self.api_key,
                            }
                            try:
                                distance_response = requests.get(distance_url, params=distance_params)
                                distance_response.raise_for_status()
                                distance_data = distance_response.json()

                                if (
                                    distance_data
                                    and "rows" in distance_data
                                    and len(distance_data["rows"]) > 0
                                    and "elements" in distance_data["rows"][0]
                                    and len(distance_data["rows"][0]["elements"]) > 0
                                ):
                                    travel_time_seconds = (
                                        distance_data["rows"][0]["elements"][0]
                                        .get("duration", {})
                                        .get("value", 0)
                                    )
                                    return travel_time_seconds / 60  # 分単位で返す
                                else:
                                    return None
                            except Exception as e:
                                print(f"Distance Matrix API error: {e}")
                                return None

                    # 車（driving）での移動時間を計算
                    driving_time = calculate_travel_time("driving")
                    if driving_time is None:
                        continue

                    # 電車+徒歩（transit）での移動時間を計算
                    transit_time = calculate_travel_time("transit")
                    if transit_time is None:
                        continue

                    # 早い移動手段を選択
                    if driving_time <= transit_time:
                        chosen_time = driving_time
                        transportation_mode = "driving"
                    else:
                        chosen_time = transit_time
                        transportation_mode = "transit"

                    # travel_timeが60以上かつ180以下でない場合はスキップ
                    if not (60 <= chosen_time <= time):
                        continue

                    # 条件を満たす地名を追加
                    filtered_results.append(
                        {
                            "name": place["name"],
                            "address": place.get("vicinity", "住所情報なし"),
                            "travel_time": chosen_time,  # 移動時間を記録
                            "transportation": transportation_mode,  # 使用する移動手段を記録
                        }
                    )

                # 条件を満たす結果からランダムに1件選択
                if filtered_results:
                    return random.choice(filtered_results)
                else:
                    return {"error": "条件に合う地名が見つかりませんでした。"}
            else:
                return {"error": data.get("status", "Unknown error occurred")}

        except requests.exceptions.RequestException as e:
            return {"error": f"APIリクエストエラー: {str(e)}"}


if __name__ == "__main__":
    # .env読み込み
    load_dotenv()

    # API
    google_maps_api = os.getenv("GOOGLE_MAPS_API")

    if not google_maps_api:
        raise ValueError("Google Maps API key is missing. Check your .env file.")

    # LocationServiceを初期化
    location_service = LocationService(google_maps_api)

    # 1、現在地の取得
    current_location = location_service.get_current_location()
    print("現在地:", current_location)

    # 2、観光地の検索
    if "latitude" in current_location:
        tourist_spots = location_service.search_tourist_attraction()
        print("観光地:", tourist_spots)
