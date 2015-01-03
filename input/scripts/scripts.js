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

	$(document).on("click", "body#home .video", function (e) {
		var code = $(this).attr("data-code");
		if (code) {
			e.preventDefault();
			$(this).replaceWith(code);
		}
	});
});
