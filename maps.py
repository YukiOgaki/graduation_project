from dotenv import load_dotenv
import googlemaps
import os
import random
import requests
import time


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
        {'latitude': 12.0000000, 'longitude': 34.0000000, 'accuracy': 20.0000000000, 'source': 'GPS'}
            ※latitude=緯度  longitude=経度  accuracy=精度(メートル算出)

        accuracyが2000以上の場合、住所を手入力してその座標を返す。
        """
        try:
            # Googleマップクライアントを初期化
            result = self.gmaps.geolocate()

            if "location" in result:
                latitude = result["location"]["lat"]  # 緯度
                longitude = result["location"]["lng"]  # 経度
                accuracy = result.get("accuracy", "Unknown")  # 誤差 (メートル)

                # 信憑性が低い場合の処理(2km以上ズレている場合)
                if accuracy != "Unknown" and accuracy >= 2000:
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
                            "accuracy": 2000,  # 手入力の場合はデフォルトで2000に設定
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
                        "source": "GPS",  # GPSから取得した情報であることを示す
                    }
                    return self.current_location
            else:
                return {"error": "位置情報は利用できません"}
        except Exception as e:
            return {"error": str(e)}

    # 2、現在地から条件を追加して、地名を検索
    def search_city(self, lat: float, lng: float, radius=50000, type="sublocality"):
        """
        出力方式:
        {'name': 'Tazawako Obonai', 'coordinates': {'latitude': 39.7031375, 'longitude': 140.726863}, 'address': 'Tazawako Obonai'}

        radius: 現在地から半径50km以内の地名をランダムに選出。
        type: 地名(sublocalityで市の下まで取得可能)
        :return: dict - 選出された地名の情報またはエラーメッセージ
        """

        # 現在地の確認
        if not self.current_location:
            return {"error": "現在地が設定されていません。get_current_location()を実行してください。"}

        # Google Places APIのエンドポイント
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
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

    # 3、2の行き先1箇所から更に9箇所(計10箇所)を辞書型で格納
    def get_cities(self, location_service):
        """
        指定された location_service を使用して 10 件の地名を取得する関数。

        Args:
            location_service: 現在地および地名検索のためのサービス。

        Returns:
            list: 取得した地名のリスト（重複を許容）。
        """
        citys = []

        city = location_service.search_city(
            float(location_service.get_current_location()["latitude"]),
            float(location_service.get_current_location()["longitude"]),
        )

        while len(citys) < 10:
            citys.append(city["name"])

            time.sleep(1)  # スリープを追加

            next_city = location_service.search_city(
                float(city["coordinates"]["latitude"]),
                float(city["coordinates"]["longitude"]),
            )

            citys.append(next_city["name"])

            time.sleep(1)  # スリープを追加

            # 次のポイントの情報を取得
            city = location_service.search_city(
                float(next_city["coordinates"]["latitude"]) + 0.1,
                float(next_city["coordinates"]["longitude"]) + 0.1,
            )

        return citys


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
    print("1、現在地出力結果:", current_location)

    citys = location_service.get_cities(location_service)
    print("収集した地名:", citys)


#    # 10候補出力
#    place_names = location_service.potential_tourist_destinations(10)
#    if "error" in place_names:
#        print("エラー:", place_names["error"])
#    else:
#        print("取得された地名リスト:", place_names)
