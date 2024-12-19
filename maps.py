from dotenv import load_dotenv
import googlemaps
import os
import random
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
        現在地を取得する関数。

        出力形式:
        {'latitude': 12.0000000, 'longitude': 34.0000000, 'accuracy': 20.0000000000}
            ※latitude=緯度  longitude=経度  accuracy=精度(メートル算出)

        accuracyが1000以上の場合、住所を手入力してその座標を返す。
        """
        try:
            # Googleマップクライアントを初期化
            result = self.gmaps.geolocate()

            if "location" in result:
                latitude = result["location"]["lat"]  # 緯度
                longitude = result["location"]["lng"]  # 経度
                accuracy = result.get("accuracy", "Unknown")  # 誤差 (メートル)

                # 信憑性が低い場合の処理
                if accuracy != "Unknown" and accuracy >= 1000:
                    print("現在地を取得できません。")
                    address = input("ざっくり現在地を入力してください: ")

                    # Google Maps Geocoding APIで住所を座標に変換
                    geocode_result = self.gmaps.geocode(address)
                    if geocode_result:
                        latitude = geocode_result[0]["geometry"]["location"]["lat"]
                        longitude = geocode_result[0]["geometry"]["location"]["lng"]

                        # 手入力された住所の情報を設定
                        self.current_location = {
                            "latitude": latitude,
                            "longitude": longitude,
                            "accuracy": 1000,  # 手入力の場合はデフォルトで1000に設定
                            "source": "manual_input",  # 情報のソースを追加
                        }
                        return self.current_location
                    else:
                        return {"error": "住所から座標を取得できませんでした。"}
                else:
                    # 正常に現在地を返す
                    self.current_location = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "accuracy": accuracy,
                        "source": "gps",  # GPSから取得した情報であることを示す
                    }
                    return self.current_location
            else:
                return {"error": "位置情報は利用できません"}
        except Exception as e:
            return {"error": str(e)}

    # 2、現在地から条件を追加して、地名を検索
    def search_city(self, radius=500000, type="sublocality"):
        """
        radius: 現在地から半径500km以内の地名をランダムに選出。
        type: 地名(sublocalityで市の下まで取得可能)
        :return: dict - 選出された地名の情報またはエラーメッセージ
        """

        # 現在地の確認
        if not self.current_location:
            return {"error": "現在地が設定されていません。get_current_location()を実行してください。"}

        # Google Places APIのエンドポイント
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{self.current_location['latitude']},{self.current_location['longitude']}",
            "radius": radius,
            "type": type,
            "key": self.api_key,
        }

        try:
            # Places APIリクエスト
            response = requests.get(places_url, params=params)
            response.raise_for_status()  # HTTPエラーがある場合は例外を発生
            data = response.json()

            if data.get("status") != "OK":
                return {"error": data.get("status", "Unknown error occurred")}

            # 候補からランダムに1件選出
            if data.get("results"):
                place = random.choice(data["results"])
                return {
                    "name": place["name"],  # 地名
                    "coordinates": {
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"],
                    },
                    "address": place.get("vicinity", "住所情報なし"),
                }
            else:
                return {"error": "条件に合う地名が見つかりませんでした。"}

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

    # 2、地名の検索
    city = location_service.search_city()
    if "error" in city:
        print("エラー:", city["error"])
    else:
        print("選出された地名:")
        print(f"名前: {city['name']}")
        print(f"座標: {city['coordinates']}")
        print(f"住所: {city['address']}")
