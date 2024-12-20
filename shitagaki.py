import random

basho = []

while len(basho) < 10:  # リストの長さが10になるまで繰り返す
    # 1~20の範囲内でランダムに数字を選出
    number = random.randint(1, 20)

    # リストに重複がない場合のみ追加
    if number not in basho:
        basho.append(number)

# 結果を表示
print("basho:", basho)





def potential_tourist_destinations(count=10):
    """
    指定範囲内で重複しないランダムな数字を生成する関数。

    :param count: int - 生成する数字の個数
    :param start: int - 範囲の開始値 (デフォルト: 1)
    :param end: int - 範囲の終了値 (デフォルト: 20)
    :return: list - 重複しないランダムな数字のリスト
    """
    basho = []

    while len(basho) < count:
        potential_tourist_destinations = location_service.search_city()
        if potential_tourist_destinations not in basho:
            basho.append(potential_tourist_destinations)

    return basho
