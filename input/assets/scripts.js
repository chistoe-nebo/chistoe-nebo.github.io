/*
window.onerror = function (msg, url, line) {
	alert("JavaScript error: " + msg + "\nat " + url + " line " + line + ".");
}
*/

var tb_pathToImage = "/scripts/loadingAnimation.gif";

jQuery(document).ready(function($){
	if ($("#splash").length == 1) {
		$("#splash").bjqs({
			"width": "100%",
			"height": "500",
			"responsive": true,
			"animspeed": 50000,
		});
	}

	$(document).on("click", "body.home .video", function (e) {
		var code = $(this).attr("data-code");
		if (code) {
			e.preventDefault();
			$(this).replaceWith(code);
		}
	});

	if ($("body").is(".error_html")) {
		var link = "blog.chistoe-nebo.org" + window.location.pathname;
		var a = $("#content a");
		a.prop("href", "http://" + link);
		a.text(link);
	}

	if ($("body.go #map").length == 1) {
		function mrk(p) {
		  var m = L.marker([p[0], p[1]]);
		  if (p[2])
		    m.bindPopup(p[2]);

		  var icon = p[3];
		  if (p[4])
		    icon = p[4];

		  var i = L.icon({
		    iconUrl: "/assets/icons/" + icon + ".png",
		    iconSize: [32, 37],
		    iconAnchor: [15, 37]
		  });
		  m.setIcon(i);

		  return m;
		}

		function points_of_type(type) {
		  var _points = [];
		  for (var key in points) {
		    var p = points[key];
		    if (p[3] == type)
		  	_points.push(mrk(p));
		  }
		  return _points;
		}

		function get_bounds()
		{
		  var bounds = new L.LatLngBounds(
		    new L.LatLng(points[0][0], points[0][1]));
		  for (var key in points) {
		    var p = points[key];
		    var ll = new L.LatLng(p[0], p[1]);
		    bounds.extend(ll);
		  }
		  return bounds;
		}

		// lat, lon, html, category, icon
		var points = [
		   [56.1738, 28.74169, "Публичный выход к озеру Большое Олбито", "water", "beach"],
		  ,[56.26762, 28.49098, "Себежский пляж", "water", "beach"]
		  ,[56.29066, 28.58428, "Придорожный пирс в Мальково", "water", "beach"]
		  ,[56.14679, 28.57544, "Озеро Зеленец. Чистейшее, с идеально прозрачной водой.", "water", "beach"]
		  ,[56.16782, 28.6641, "Пляж на озере Осыно", "water", "beach"]

		  ,[56.17018, 28.73124, "<img src='/stay/vladimir/for_map.jpg' alt='гостевой дом' width='300' height='200'/><p>Гостевой дом <a href='/stay/vladimir/' target='_top'>Владимира и Юлии</a></p>", "building", "home"]
		  ,[56.17358, 28.7327, "<img src='/stay/igor/house_map.jpg' alt='дом' width='300' height='200'/><p>Гостевой дом <a href='/stay/igor/' target='_top'>Игоря</a></p>", "building", "home"]
		  ,[56.18356, 28.74077, "<img src='/stay/alexey/guesthouse_map.jpg' width='300' height='200'/><p>Гостевой дом <a href='/stay/alexey/' target='_top'>Алексея</a></p>", "building", "home"]
		  ,[56.17052, 28.73077, "<img src='/stay/vladimir/camping_map.jpg' width='300' height='200' alt='палаточный лагерь'/><p>Палаточный лагерь <a href='/stay/vladimir/' target='_top'>Владимира и Юлии</a></p>", "building", "tents"]

		  ,[56.18277, 28.74087, "<img src='/stay/alexey/bath_map.jpg' alt='баня' width='300' height='200'/><p>Баня <a href='/stay/alexey/' target='_top'>Алексея</a></p>", "building", "sauna"]
		  ,[56.17375, 28.73349, "Баня <a href='/stay/igor/' target='_top'>Игоря</a><br/><img src='/stay/igor/bath_map.jpg' alt='дом' width='300' height='200'/>", "building", "sauna"]
		  ,[56.28746, 28.59715, "Баня частного рыбного хозяйства, 1500 р за 4 часа, вместительность до 6 человек.", "building", "sauna"]

		  ,[56.1522, 28.67412, "Магазин в Осыно. Работает по рабочим дням с 8:00 до 15:00. Есть минимальный набор продуктов и хозяйственных товаров.", "food", "grocery"]
		  ,[56.28273, 28.48247, "Магазин «Магнит».", "food", "grocery"]
		  ,[56.27711, 28.48723, "Гостиница «Себеж», в ней есть кафе и wifi.", "food", "hotfoodcheckpoint"]

		  ,[56.27722, 28.49204, "Краеведческий музей", "building", "home"]
		  ,[56.17855, 28.7324, "<img src='/residents/anna/for_map.jpg' alt='anna' width='300' height='150'/><p><a href='/residents/anna/' target='_top'>Аня Гусева</a> проведёт мастер-класс по выпечке классического домашнего бездрожжевого хлеба.</p>", "building", "school"]

		  ,[56.28412, 28.48311, "Автостанция, сюда приезжает автобус из Санкт-Петербурга", "building", "home"]
		  ,[56.30513, 28.46958, "Ж/д вокзал, сюда приезжает поезд из Москвы", "building", "home"]
		  ,[56.1994, 28.70453, "Аннинское, развалины усадьбы Бакуниных и Корсаков", "building", "ruins"]

		];

		var map = L.map("map", {
		  fullscreenControl: true
		});
		map.fitBounds(get_bounds());

		map.addControl(new L.Control.Scale());
		map.addControl(new L.Control.Distance());

		var base_osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		  attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
		  maxZoom: 18
		});

		var base_osm_fr = new L.TileLayer('http://{s}.tile.openstreetmap.fr/osmfr-lz/{z}/{x}/{y}.png', {
		  attribution: 'Map data &copy; <a href="http://openstreetmap.fr">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
		  maxZoom: 20
		});

		var base_esri = new L.TileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		  attribution: 'Map data &copy; <a href="http://openstreetmap.fr">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
		  maxZoom: 17
		});

		var base_yandex = new L.Yandex("satellite");

		// При ctrl-клике выводим координаты точки.
		map.on("click", function (e) {
		  if (e.originalEvent.ctrlKey) {
		    alert(e.latlng);
		  }
		});

		map.on("baselayerchange", function (e) {
		  var max_zoom = e.layer.options.maxZoom;
		  if (map.getZoom() > max_zoom) {
		    map.setZoom(max_zoom);
		  }
		});

		var base_google = new L.Google();

		var ovl_buildings = L.layerGroup(points_of_type("building"));
		var ovl_water = L.layerGroup(points_of_type("water"));
		var ovl_food = L.layerGroup(points_of_type("food"));

		var baseMaps = {
		  "OpenStreetMap": base_osm,
		  "OpenStreetMap France": base_osm_fr,
		  "Google": base_google,
		  "Яндекс": base_yandex,
		  "ESRI": base_esri
		};

		var overlays = {
		  "Постройки": ovl_buildings,
		  "Вода": ovl_water,
		  "Еда": ovl_food
		};

		L.control.layers(baseMaps, overlays).addTo(map);

		// Вывод слоёв по умолчанию.
		map.addLayer(base_osm_fr);
		map.addLayer(ovl_buildings);
		map.addLayer(ovl_water);
		map.addLayer(ovl_food);
	}
});
