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
    def potential_tourist_destinations(self, count=10):
        """
        指定された条件に基づいて、地名をplace_namesリストに格納する。

        :param count: int - 格納する地名の個数 (デフォルト: 10)
        :return: list - 条件に合う地名のリスト
        """
        # 現在地を取得
        current_location = self.get_current_location()
        if "error" in current_location:
            return {"error": "現在地の取得に失敗しました。"}

        # 現在地の地名を取得
        initial_place = self.search_city(current_location["latitude"], current_location["longitude"])
        if "error" in initial_place:
            return {"error": "地名の取得に失敗しました。"}

        # 初期化
        place_names = []
        current_coordinates = initial_place["coordinates"]
        current_name = initial_place["name"]

        while len(place_names) < count:
            # 次の地名を取得
            next_place = self.search_city(current_coordinates["latitude"], current_coordinates["longitude"])
            if "error" in next_place:
                continue

            next_name = next_place["name"]

            # 条件チェック: 重複しない、現在地の地名を含めない
            if next_name not in place_names and next_name != current_name:
                place_names.append(next_name)
                # 次の地点の座標を設定
                current_coordinates = next_place["coordinates"]

        return place_names


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
    print("座標:", current_location)

    # 2、地名の検索
    city = location_service.search_city(
        location_service.get_current_location()["latitude"],
        location_service.get_current_location()["longitude"],
    )
    if "error" in city:
        print("エラー:", city["error"])
    else:
        print("選出された地名:")
        print(f"名前: {city['name']}")
        print(f"座標: {city['coordinates']}")

    # 10候補出力
    place_names = location_service.potential_tourist_destinations(10)
    if "error" in place_names:
        print("エラー:", place_names["error"])
    else:
        print("取得された地名リスト:", place_names)
