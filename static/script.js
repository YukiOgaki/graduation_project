mapboxgl.accessToken = mapboxAccessToken;

let map;       // 地図オブジェクトを格納する変数
let marker;    // マーカーオブジェクトを格納する変数

// 現在地を取得して地図を表示する関数
function initializeMap() {
    navigator.geolocation.getCurrentPosition(successLocation, errorLocation);
}

function successLocation(position) {
    const userLat = position.coords.latitude;   // 緯度
    const userLng = position.coords.longitude;  // 経度

    // 地図を初期化または更新する
    if (!map) {
        // 地図がまだ存在しない場合、新しく作成
        map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [userLng, userLat],
            zoom: 14
        });

        // マーカーを現在地に表示
        marker = new mapboxgl.Marker()
            .setLngLat([userLng, userLat])
            .setPopup(new mapboxgl.Popup().setText("あなたの現在地"))
            .addTo(map);

        // 地図右上に「現在地を更新する」ボタンを追加
        addUpdateButtonToMap();
    } else {
        // 既存の地図があれば、位置を更新
        map.flyTo({
            center: [userLng, userLat],
            essential: true
        });

        // マーカーの位置を更新
        marker.setLngLat([userLng, userLat]);
    }
}

function errorLocation() {
    alert("現在地を取得できませんでした。位置情報を許可してください。");
}

// 地図右上にボタンを追加する関数
function addUpdateButtonToMap() {
    const updateButton = document.createElement("button");
    updateButton.innerText = "現在地を更新する";
    updateButton.style.padding = "10px";
    updateButton.style.cursor = "pointer";
    updateButton.style.backgroundColor = "#007BFF";
    updateButton.style.color = "white";
    updateButton.style.border = "none";
    updateButton.style.borderRadius = "5px";
    updateButton.style.fontSize = "14px";

    // ボタンがクリックされたときの動作
    updateButton.addEventListener("click", () => {
        navigator.geolocation.getCurrentPosition(successLocation, errorLocation);
    });

    // Mapboxのコントロールとして右上に追加
    const customControl = {
        onAdd: function () {
            const container = document.createElement("div");
            container.className = "mapboxgl-ctrl";
            container.appendChild(updateButton);
            return container;
        },
        onRemove: function () { }
    };

    map.addControl(customControl, "top-right");
}

// 初回地図の表示
initializeMap();
