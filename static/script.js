let map;  // Google Mapsの地図オブジェクト
let userLat, userLng;  // 現在地の緯度と経度を保存

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

            // マーカーを現在地に表示
            new google.maps.Marker({
                position: userLocation,
                map: map,
                title: "あなたの現在地",
            });
        })
        .catch(error => {
            console.error('エラー:', error);
            alert("現在地を取得できませんでした。");
        });
}

// 周辺施設を探すボタンをクリックした時に呼び出される
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

// 初回地図の表示
initializeMap();

// 周辺施設を探すボタンにイベントリスナーを追加
document.getElementById("facility-button").addEventListener("click", findNearbyFacilities);
