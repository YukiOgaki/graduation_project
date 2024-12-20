from dotenv import load_dotenv
import requests
import os


def get_current_location(api_key):
    """
    Google Maps APIを使用して現在地の緯度と経度を取得する。

    Args:
        api_key (str): Google Cloud Platformから取得したAPIキー。

    Returns:
        dict: 緯度と経度を含む辞書、またはエラーの場合はエラーメッセージ。
    """
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"

    try:
        response = requests.post(url, json={})
        response.raise_for_status()

        location_data = response.json()
        location = location_data.get("location", {})
        accuracy = location_data.get("accuracy", None)

        # 信憑性が低い場合の処理(2km以上ズレている場合)
        if accuracy != "Unknown" and accuracy >= 2000:
            print("現在地を取得できません。")
            address = input("ざっくり現在地を入力してください: ")
            return {"latitude": None, "longitude": None, "accuracy": accuracy, "address": address}

        return {
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "accuracy": accuracy,
            "address": "Location determined automatically",
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# 使用例
if __name__ == "__main__":
    # .env読み込み
    load_dotenv()

    # API
    api_key = os.getenv("GOOGLE_MAPS_API")
    location = get_current_location(api_key)

    if "error" in location:
        print(f"エラーが発生しました: {location['error']}")
    else:
        if location["latitude"] is not None and location["longitude"] is not None:
            print(
                f"現在地: 緯度 {location['latitude']}, 経度 {location['longitude']} (精度: {location['accuracy']}m)"
            )
        print(f"地名: {location['address']}")
