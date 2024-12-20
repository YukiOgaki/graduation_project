from dotenv import load_dotenv
import googlemaps
import os
import random
import requests
import time


# +--------------------------------------------------------+
# | グーグルマップを使って、様々な「場所」を算出するクラス      |
# +--------------------------------------------------------+
class LocationService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Google Maps API keyが正しくありません")
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
                            "source": "手入力",  # 情報のソースを追加
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
    def search_city(self):
        # 半径50km以上(300kmぐらいまで)検索可能になれば、自動で。
        citys = [
            {"name": "Tazawako Obonai", "latitude": 39.7135346, "longitude": 140.4736874},
            {"name": "Hanawa", "latitude": 40.214867, "longitude": 140.7649121},
            {"name": "Daisen", "latitude": 39.5446615, "longitude": 140.1546033},
            {"name": "Akita", "latitude": 39.5896563, "longitude": 139.9704755},
            {"name": "Oga", "latitude": 39.8838945, "longitude": 139.8379237},
            {"name": "Hachinohe", "latitude": 40.5254727, "longitude": 141.5286749},
            {"name": "Hirosaki", "latitude": 40.2421014, "longitude": 140.1214415},
            {"name": "Tsugaru", "latitude": 39.6793795, "longitude": 140.6229451},
            {"name": "Imabetsumachi", "latitude": 41.0764024, "longitude": 140.3476161},
            {"name": "Aomori", "latitude": 40.3576612, "longitude": 140.347923},
            {"name": "Mutsu", "latitude": 40.5825387, "longitude": 139.9009561},
            {"name": "Kuji", "latitude": 39.9352726, "longitude": 141.153966},
            {"name": "Sakari", "latitude": 41.0527299, "longitude": 138.4667735},
            {"name": "Hiraizumi", "latitude": 41.0040091, "longitude": 138.3084818},
            {"name": "Kesennuma", "latitude": 39.4085878, "longitude": 140.6927502},
            {"name": "Kurihara", "latitude": 38.9498575, "longitude": 140.3519789},
            {"name": "Sendai", "latitude": 38.5840713, "longitude": 140.9246896},
            {"name": "Ishinomaki", "latitude": 39.1680046, "longitude": 139.8700756},
            {"name": "Shinjo", "latitude": 38.9331872, "longitude": 139.9074409},
            {"name": "Yamagata", "latitude": 38.1726488, "longitude": 140.3299929},
        ]

        i = random.randint(0, len(citys) - 1)  # 0~19のランダムなインデックスを生成
        return citys[i]

    # 3、検索した地名周辺の観光地を探す
    def pic_tourist_spot(self, lat, lng):
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius=50000&type=tourist_attraction"
            f"&key={self.api_key}"
        )

        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            tourist_spots = []
            for result in results:
                name = result.get("name")
                address = result.get("vicinity")
                lat = result["geometry"]["location"].get("lat")
                lng = result["geometry"]["location"].get("lng")
                op_times = "Unknown"

                # 営業時間を取得
                if "opening_hours" in result and "weekday_text" in result["opening_hours"]:
                    op_times = ", ".join(result["opening_hours"]["weekday_text"])

                # 除外条件: "ホテル" と "レストラン"
                if (
                    "ホテル" not in name
                    and "レストラン" not in name
                    and "宿" not in name
                    and "旅館" not in name
                ):
                    tourist_spots.append(
                        {
                            "name": name,
                            "address": address,
                            "op_times": op_times,
                            "lat": lat,
                            "lng": lng,
                        }
                    )

                # 10箇所まで取得したら終了
                if len(tourist_spots) >= 10:
                    break

            return tourist_spots
        else:
            print("Error fetching tourist spots:", response.status_code, response.text)
            return []


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

    # 2、現在地から3時間以内で行ける町
    selected_city = location_service.search_city()
    print(
        f"地名 : {selected_city['name']} 緯度 : {selected_city['latitude']} 経度 : {selected_city['longitude']}"
    )

    # 3、上記2周辺の観光地
    tourist_spots = location_service.pic_tourist_spot(selected_city["latitude"], selected_city["longitude"])
    print(tourist_spots)
