var this_js_script = $('script[src*=leaflet_single]'); // or better regexp to get the file name..

var latitude = this_js_script.attr('data-latitude');   
if (typeof latitude === "undefined" ) {
   var latitude = '52.535879';
}

var longitude = this_js_script.attr('data-longitude');   
if (typeof longitude === "undefined" ) {
   var longitude = '4.717302';
}

var mymap = L.map('mapid', {zoomControl: false}).setView([latitude, longitude], 16);

var brandweerIcon = L.icon({
    iconUrl: 'https://brandweeruitgeest.nl/img/map-logo-icon.png',

    iconSize:     [32, 32], // size of the icon
    popupAnchor:  [0, -16], // point from which the popup should open relative to the iconAnchor
    iconAnchor:   [16, 16] // point of the icon which will correspond to marker's location
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mymap);

L.marker([latitude, longitude], {icon: brandweerIcon}).addTo(mymap);