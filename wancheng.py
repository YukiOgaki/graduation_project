# 一応メモ程度に残しておきます

    # 2、現在地から条件を追加して、地名を検索
    def search_city(self, lat: float, lng: float, radius=500000, type="sublocality"):
        """
        出力方式:
        {'name': 'Tazawako Obonai', 'coordinates': {'latitude': 39.7031375, 'longitude': 140.726863}, 'address': 'Tazawako Obonai'}

        radius: 現在地から半径500km以内の地名をランダムに選出。
        type: 地名(sublocalityで市の下まで取得可能)
        :return: dict - 選出された地名の情報またはエラーメッセージ
        """

        # 現在地の確認
        if not self.current_location:
            return {"error": "現在地が設定されていません。get_current_location()を実行してください。"}

        # Google Places APIのエンドポイント
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        max_radius = 50000  # 最大半径は50km

        try:
            results = []

            # 半径を分割して検索
            for i in range(0, radius, max_radius):
                params = {
                    "location": f"{lat},{lng}",
                    "radius": max_radius,
                    "type": type,
                    "key": self.api_key,
                }

                response = requests.get(places_url, params=params)
                response.raise_for_status()  # HTTPエラーがある場合は例外を発生
                data = response.json()

                if data.get("status") != "OK":
                    return {"error": data.get("status", "Unknown error occurred")}

                if data.get("results"):
                    results.extend(data["results"])

            # 統合された結果からランダムに1件選出
            if results:
                place = random.choice(results)
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


