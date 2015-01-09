jQuery(document).ready(function($){
	$(document).on("click", "body.home .video", function (e) {
		var code = $(this).attr("data-code");
		if (code) {
			e.preventDefault();
			$(this).replaceWith(code);
		}
	});
});
