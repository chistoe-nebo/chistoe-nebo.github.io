window.onerror = function () {
	alert("JavaScript error.");
}

jQuery(document).ready(function($){
	$("#splash").bjqs({
		"width": "100%",
		"height": "100%",
		"responsive": true,
		"animspeed": 50000,
	});
});
