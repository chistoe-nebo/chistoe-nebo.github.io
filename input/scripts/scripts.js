window.onerror = function (msg, url, line) {
	alert("JavaScript error: " + msg + "\nat " + url + " line " + line + ".");
}

jQuery(document).ready(function($){
	if ($("#splash").length == 1) {
		$("#splash").bjqs({
			"width": "100%",
			"height": "100%",
			"responsive": true,
			"animspeed": 50000,
		});
	}
});
