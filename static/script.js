let map;  // Google Mapsの地図オブジェクト
let userLat, userLng;  // 現在地の緯度と経度を保存
let markers = [];  // 地図上のマーカーを管理

// 現在地を取得して地図を表示する関数
function initializeMap() {
    fetch('/api/current_location')
        .then(response => {
            if (!response.ok) {
                throw new Error('現在地を取得できませんでした');
            }
            return response.json();
        })
        .then(data => {
            userLat = data.latitude;
            userLng = data.longitude;

            const userLocation = { lat: userLat, lng: userLng };

            // Google Mapsを表示
            map = new google.maps.Map(document.getElementById("map"), {
                center: userLocation,
                zoom: 14,
            });

            // 現在地にマーカーを立てる
            addMarker(userLocation, "あなたの現在地");

            // 検索ボックスを追加
            addSearchBox();

            // 地図をクリックした時にピンを立てるイベント
            map.addListener("click", (event) => {
                const clickedLocation = { lat: event.latLng.lat(), lng: event.latLng.lng() };
                addMarker(clickedLocation, "ピンを追加しました");
            });
        })
        .catch(error => {
            console.error('エラー:', error);
            alert("現在地を取得できませんでした。");
        });
}

// マーカーを追加する関数
function addMarker(location, title) {
    const marker = new google.maps.Marker({
        position: location,
        map: map,
        title: title,
    });
    markers.push(marker);
}

// 検索ボックスを追加する関数
function addSearchBox() {
    // 地名検索用の入力ボックスを作成
    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'search-box';
    input.placeholder = 'Googleマップを検索する...';
    input.style.width = '300px';
    input.style.padding = '5px';

    // Google Mapsのカスタムコントロールに検索ボックスを追加
    const searchBoxContainer = document.createElement('div');
    searchBoxContainer.style.margin = '10px';
    searchBoxContainer.style.padding = '5px';
    searchBoxContainer.style.backgroundColor = 'white';
    searchBoxContainer.style.border = '1px solid #ccc';
    searchBoxContainer.style.borderRadius = '3px';
    searchBoxContainer.appendChild(input);

    map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchBoxContainer);

    // Places API の検索ボックスを利用
    const searchBox = new google.maps.places.SearchBox(input);

    // 地図の範囲が変更された時、検索ボックスの範囲を更新
    map.addListener("bounds_changed", () => {
        searchBox.setBounds(map.getBounds());
    });

    // 検索結果を取得
    searchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places.length === 0) {
            return;
        }

        // 現在のマーカーを削除
        markers.forEach(marker => marker.setMap(null));
        markers = [];

        // 検索結果を地図上に表示
        places.forEach(place => {
            if (!place.geometry || !place.geometry.location) {
                console.error("検索結果に位置情報が含まれていません:", place);
                return;
            }

            // 新しいマーカーを追加
            addMarker(place.geometry.location, place.name);

            // 地図の中心を検索結果の位置に移動
            map.setCenter(place.geometry.location);
            map.setZoom(14);
        });
    });
}

// 初回地図の表示
initializeMap();

// 周辺施設を探すボタンにイベントリスナーを追加
document.getElementById("facility-button").addEventListener("click", findNearbyFacilities);

// 周辺施設を探す関数（元のコードのまま維持）
function findNearbyFacilities() {
    if (userLat && userLng) {
        fetch('/tpcreate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ lat: userLat, lng: userLng })
        })
        .then(response => {
            if (response.ok) {
                // POSTが成功した場合、/tpcreateページへリダイレクト
                window.location.href = '/tpcreate';
            } else {
                console.error('サーバーからのエラー:', response.statusText);
            }
        })
        .catch(error => console.error('エラーが発生しました:', error));
    } else {
        alert("現在地を取得してからお試しください。");
    }
}
