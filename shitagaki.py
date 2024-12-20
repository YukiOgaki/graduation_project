from dotenv import load_dotenv
import googlemaps
import os
import random
import requests
import time


# 1、現在地を取得
def get_current_location(api_key):
    """
    出力形式:
    {'latitude': 12.0000000, 'longitude': 34.0000000, 'accuracy': 20.0000000000, 'source': 'GPS'}
        ※latitude=緯度  longitude=経度  accuracy=精度(メートル算出)

    accuracyが2000以上の場合、住所を手入力してその座標を返す。
    """
    try:
        gmaps = googlemaps.Client(key=api_key)
        result = gmaps.geolocate()

        if "location" in result:
            name = result[0]["formatted_address"]
            latitude = result["location"]["lat"]
            longitude = result["location"]["lng"]
            accuracy = result.get("accuracy", "Unknown")

            if accuracy != "Unknown" and accuracy >= 2000:
                print("現在地を取得できません。")
                address = input("ざっくり現在地を入力してください: ")

                geocode_result = gmaps.geocode(address)
                if geocode_result:
                    name = geocode_result[0]["formatted_address"]
                    latitude = geocode_result[0]["geometry"]["location"]["lat"]
                    longitude = geocode_result[0]["geometry"]["location"]["lng"]

                    return {
                        "name": name,
                        "latitude": latitude,
                        "longitude": longitude,
                        "accuracy": 2000,
                        "source": "manual_input",
                    }
                else:
                    return {"error": "住所から座標を取得できませんでした。"}
            else:
                return {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy,
                    "source": "GPS",
                }
        else:
            return {"error": "位置情報は利用できません"}
    except Exception as e:
        return {"error": str(e)}


# 2、現在地から観光地検索
def search_city():
    places = [
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

    i = random.randint(0, len(places) - 1)  # 0~19のランダムなインデックスを生成
    return places[i]


# 3、第二の観光地算出
def potential_tourist_destinations(api_key: str, count=10):
    """
    指定された条件に基づいて、地名をplace_namesリストに格納する。

    :param count: int - 格納する地名の最大個数 (デフォルト: 10)
    :return: list - 条件に合う地名のリスト
    """
    current_location = get_current_location(api_key)
    if "error" in current_location:
        return {"error": "現在地の取得に失敗しました。"}

    initial_place = search_city(
        float(current_location["latitude"]), float(current_location["longitude"]), api_key
    )
    if "error" in initial_place:
        return {"error": "地名の取得に失敗しました。"}

    place_names = []
    current_coordinates = initial_place["coordinates"]
    current_name = initial_place["name"]

    while len(place_names) < count:
        next_place = search_city(
            float(current_coordinates["latitude"]), float(current_coordinates["longitude"]), api_key
        )
        if "error" in next_place:
            continue

        next_name = next_place["name"]

        if next_name not in place_names and next_name != current_name:
            place_names.append(next_name)
            current_coordinates = next_place["coordinates"]
            time.sleep(1)

    return place_names


def get_location_details(lat: float, lng: float, api_key: str):
    """
    指定された緯度・経度を中心に、半径50km以内の"sublocality"を検索し、
    "name", "latitude", "longitude"を返す。

    :param lat: float - 緯度
    :param lng: float - 経度
    :param api_key: str - Google Maps APIキー
    :return: dict - 検出された地名、緯度、経度の辞書またはエラーメッセージ
    """
    radius = 50000
    type = "sublocality"

    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": type,
        "key": api_key,
    }

    try:
        response = requests.get(places_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            return {"error": f"APIエラー: {data.get('status', '不明なエラー')}"}

        if data.get("results"):
            place = data["results"][0]
            return {
                "name": place["name"],
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
            }
        else:
            return {"error": "条件に合う結果が見つかりませんでした。"}

    except requests.exceptions.RequestException as e:
        return {"error": f"APIリクエストエラー: {str(e)}"}


if __name__ == "__main__":
    load_dotenv()
    google_maps_api = os.getenv("GOOGLE_MAPS_API")

    if not google_maps_api:
        raise ValueError("Google Maps API key is missing. Check your .env file.")

    current_location = get_current_location(google_maps_api)
    print("1、現在地出力結果:", current_location)

    city = search_city(
        float(current_location["latitude"]), float(current_location["longitude"]), google_maps_api
    )
    print("2、地名1出力結果:", city)

    scd_place = get_location_details(
        city["coordinates"]["latitude"], city["coordinates"]["longitude"], google_maps_api
    )
    print("3、地名2出力結果:", scd_place)

# Uncomment this section for generating potential destinations
#    place_names = potential_tourist_destinations(google_maps_api, count=10)
#    if "error" in place_names:
#        print("エラー:", place_names["error"])
#    else:
#        print("取得された地名リスト:", place_names)
