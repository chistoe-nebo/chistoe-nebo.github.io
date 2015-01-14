<?php

if (!empty($_POST["email"])) {
    mail("nebo-guest+subscribe@googlegroups.com",
         "subscribe: chistoe-nebo.info",
         "{$_POST["email"]} wants to subscribe",
         "From: {$_POST["email"]}\r\nCc: hex+nebo-guest@umonkey.net\r\n");

    header("303 See Other");
    header("Location: http://www.chistoe-nebo.info/news/thanks/");
    die("Thanks!");
}

header("400 Bad Request");
header("Content-Type: text/plain");
die("What?");
