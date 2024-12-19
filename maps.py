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
            "radius": radius,  # 半径250000m(250km)
            "time": time,  # 時間180分
            "type": "tourist_spot",  # 観光地を指定
            "key": self.api_key,
        }

        # リクエスト送信
        response = requests.get(url, params=params)
        data = response.json()

        # 結果を表示
        if data.get("status") == "OK":
            results = []
            for place in data["results"]:
                results.append(
                    {
                        "name": place["name"],
                        "address": place.get("vicinity", "住所情報なし"),
                    }
                )
            return results
        else:
            return {"error": data.get("status", "Unknown error occurred")}


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
