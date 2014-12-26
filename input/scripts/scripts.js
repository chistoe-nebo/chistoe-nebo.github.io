window.onerror = function (msg, url, line) {
	alert("JavaScript error: " + msg + "\nat " + url + " line " + line + ".");
}

jQuery(document).ready(function($){
	if ($("#splash").length == 1) {
		$("#splash").bjqs({
			"width": "100%",
			"height": "500",
			"responsive": true,
			"animspeed": 50000,
		});
	}

	$(document).on("click", "body#home .video", function (e) {
		e.preventDefault();
		var code = $(this).attr("data-code");
		$(this).replaceWith(code);
	});
});
