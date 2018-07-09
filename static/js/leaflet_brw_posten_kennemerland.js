var mymap = L.map('mapid').setView([52.385658, 4.825745], 9);

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

L.marker([52.535879, 4.717302], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Uitgeest")
    .bindPopup("<b>Post Uitgeest</b><br /><a href=\"https://brandweeruitgeest.nl\">Website</a>");

L.marker([52.50961, 4.67538], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Heemskerk")
    .bindPopup("<b>Post Heemskerk</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/heemskerk\">Website</a>");

L.marker([52.483131, 4.667215], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Beverwijk-oost")
    .bindPopup("<b>Post Beverwijk-oost</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/beverwijk-o\">Website</a>");

L.marker([52.492435, 4.649856], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Beverwijk-west")
    .bindPopup("<b>Post Beverwijk-west</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/beverwijk-w\">Website</a>");

L.marker([52.459831, 4.650441], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Velsen-Zuid")
    .bindPopup("<b>Post Velsen-Zuid</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/velsen\">Website</a>");

L.marker([52.452188, 4.600192], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post IJmuiden")
    .bindPopup("<b>Post IJmuiden</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/velsen\">Website</a>");

L.marker([52.413791, 4.683893], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Spaarndam")
    .bindPopup("<b>Post Spaarndam</b><br /><a href=\"http://www.brandweer-spaarndam.nl\">Website</a>");

L.marker([52.385901, 4.616328], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Haarlem-west")
    .bindPopup("<b>Post Haarlem-west</b><br /><a href=\"https://www.brandweer.nl/kennemerland/posten/haarlem-w\">Website</a>");


L.marker([52.364273, 4.658858], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Haarlem-oost")
    .bindPopup("<b>Post Haarlem-oost</b><br /><a href=\"https://www.brandweerhaarlemoost.nl\">Website</a>");


L.marker([52.375475, 4.545435], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Zandvoort-noord")
    .bindPopup("<b>Post Zandvoort-noord</b><br /><a href=\"https://www.brandweer-zandvoort.nl\">Website</a>");


L.marker([52.37104, 4.527333], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Zandvoort-centrum")
    .bindPopup("<b>Post Zandvoort-centrum</b><br /><a href=\"https://www.brandweer-zandvoort.nl\">Website</a>");


L.marker([52.316584, 4.674734], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Hoofddorp")
    .bindPopup("<b>Post Hoofddorp</b><br /><a href=\"https://brandweerhoofddorp.wordpress.com\">Website</a>");


L.marker([52.263197, 4.64741], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Nieuw-Vennep")
    .bindPopup("<b>Post Nieuw-Vennep</b><br /><a href=\"https://brandweerhoofddorp.wordpress.com\">Website</a>");


L.marker([52.319753, 4.600235], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Bennebroek")
    .bindPopup("<b>Post Bennebroek</b><br /><a href=\"http://www.brandweerbennebroek.nl\">Website</a>");


L.marker([52.38096, 4.754012], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Halfweg-Zwanenburg")
    .bindPopup("<b>Post Halfweg-Zwanenburg</b><br /><a href=\"http://vrkhz.nl\">Website</a>");


L.marker([52.340041, 4.774431], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Badhoevedorp")
    .bindPopup("<b>Post Badhoevedorp</b><br /><a href=\"https://www.brandweer-badhoevedorp.nl\">Website</a>");


L.marker([52.259511, 4.570954], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Lisserbroek")
    .bindPopup("<b>Post Lisserbroek</b><br /><a href=\"http://www.brandweerlisserbroek.nl\">Website</a>");


L.marker([52.258321, 4.717139], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Rijsenhout")
    .bindPopup("<b>Post Rijsenhout</b><br /><a href=\"https://brandweerrijsenhout.wordpress.com\">Website</a>");


L.marker([52.346373, 4.628769], {icon: brandweerIcon}).addTo(mymap)
    .bindTooltip("Post Heemstede")
    .bindPopup("<b>Post Heemstede</b><br /><a href=\"http://www.brandweerheemstede.nl\">Website</a>");
    
var popup = L.popup();
