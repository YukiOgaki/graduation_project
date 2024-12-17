mapboxgl.accessToken = 'pk.eyJ1Ijoic3VrZW1hcnUiLCJhIjoiY200cXozYXNzMTlpcTJpcTI2MWtlN2l6eiJ9.cZxyiZgUbFVMH3KkMPuO2Q'; // APIキー

navigator.geolocation.getCurrentPosition(successLocation, errorLocation);

function successLocation(position) {
    const userLat = position.coords.latitude;   // 緯度
    const userLng = position.coords.longitude;  // 経度

    // 地図を表示する
    const map = new mapboxgl.Map({
        container: 'map', // HTML内のdivのID
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [userLng, userLat], // 現在地を中心に表示
        zoom: 14
    });

    // ピン（マーカー）を現在地に立てる
    new mapboxgl.Marker()
        .setLngLat([userLng, userLat])
        .setPopup(new mapboxgl.Popup().setText("あなたの現在地")) // ポップアップテキスト
        .addTo(map);
}

function errorLocation() {
    alert("現在地を取得できませんでした。位置情報を許可してください。");
}

// 現在地を更新するボタン
document.getElementById("update-location").addEventListener("click", () => {
    navigator.geolocation.getCurrentPosition(successLocation, errorLocation);
});
