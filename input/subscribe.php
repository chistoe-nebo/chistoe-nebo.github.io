<?php

if (!empty($_POST["email"])) {
    mail("hex+nebo-guest@umonkey.net",
         "subscribe: chistoe-nebo.info",
         "{$_POST["email"]} wants to subscribe",
         "From: {$_POST["email"]}\r\n");

    header("300 See Other");
    header("Location: http://www.chistoe-nebo.info/news/thanks/");
    die("Thanks!");
}

header("400 Bad Request");
header("Content-Type: text/plain");
die("What?");
