mapboxgl.accessToken = mapboxAccessToken;

navigator.geolocation.getCurrentPosition(successLocation, errorLocation);

function successLocation(position) {
    const userLat = position.coords.latitude;
    const userLng = position.coords.longitude;

    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [userLng, userLat],
        zoom: 14
    });

    new mapboxgl.Marker()
        .setLngLat([userLng, userLat])
        .setPopup(new mapboxgl.Popup().setText("あなたの現在地"))
        .addTo(map);
}

function errorLocation() {
    alert("現在地を取得できませんでした。位置情報を許可してください。");
}

document.getElementById("update-location").addEventListener("click", () => {
    navigator.geolocation.getCurrentPosition(successLocation, errorLocation);
});
