
let listings = JSON.parse(document.getElementById('listings-json').textContent);

if (!Array.isArray(listings)) {
    listings = [listings]
}

function initMap() {

    var toronto = { lat: 43.654, lng: -79.3883 };
    var map = new google.maps.Map(document.getElementById("listings-map"), {
      zoom: 10,
      center: toronto,
    });

    let qMarker = {
        url: "https://qigigi.s3.ca-central-1.amazonaws.com/Group+2q_vector+(1).svg",
        scaledSize: new google.maps.Size(30,60),
        labelOrigin: new google.maps.Point(13,16)
    }

    listings.forEach((e,i) => {
        console.log(e.geolocation)
        console.log(JSON.parse(e.geolocation))
        new google.maps.Marker({
            position: JSON.parse(e.geolocation),
            map: map,
            label: {
                text: (i+1).toString(),
                fontWeight: "bold",
            },
            icon: qMarker
        });    
    });  
}

window.initMap = initMap;
