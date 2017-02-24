jQuery(document).ready(function($){
	if ($("body").is(".error_html")) {
		var link = "blog.chistoe-nebo.org" + window.location.pathname;
		var a = $("#content a");
		a.prop("href", "http://" + link);
		a.text(link);
	}
});
