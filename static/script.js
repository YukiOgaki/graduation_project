let map;  // Google Mapsの地図オブジェクト

// 現在地を取得して地図を表示する関数
function initializeMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successLocation, errorLocation);
    } else {
        alert("このブラウザでは位置情報を取得できません。");
    }
}

function successLocation(position) {
    const userLat = position.coords.latitude;   // 緯度
    const userLng = position.coords.longitude;  // 経度

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
}

function errorLocation() {
    alert("現在地を取得できませんでした。位置情報を許可してください。");
}

// 初回地図の表示
initializeMap();
