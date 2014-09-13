# encoding=utf-8

"""
Вывод графика присутствия волонтёров
"""


import datetime


__all__ = ["schedule"]


def load_data(fn):
    raw_data = open(fn, "rb").read().strip().decode("utf-8")
    return [line.split()
        for line in raw_data.splitlines()
        if not line.startswith("#")]


def get_schedule(start, end, reserve):
    dates = {}

    while start <= end:
        month = int(start.strftime("%m"))

        if month not in dates:
            dates[month] = []

        start_str = start.strftime("%Y-%m-%d")

        count = 0
        for r in reserve:
            if start_str >= r[0] and start_str <= r[1]:
                count += len(r) - 2

        dates[month].append(count)

        start += datetime.timedelta(1)

    return dates


def parse_date(d):
    return datetime.datetime.strptime(d, "%Y-%m-%d").date()


def format_schedule(schedule):
    months = [u"Январь", u"Февраль", u"Март", u"Апрель", u"Май", u"Июнь",
        u"Июль", u"Август", u"Сентябрь", u"Октябрь", u"Ноябрь", u"Декабрь"]

    schedule = {k: v
        for k, v in schedule.items()
        if sum(v)}

    max_days = max([len(v)
        for k, v in schedule.items()])

    html = u"<table class='schedule'>"
    html += u"<thead>"
    html += u"<tr><th/>"
    for day in range(max_days):
        html += u"<th>%u</th>" % (day + 1)
    html += u"</tr></thead><tbody>"

    for m, days in sorted(schedule.items()):
        html += u"<tr><th>%s</th>" % months[m - 1]

        for day in days:
            if day:
                html += u"<td class='v%u'>%u</td>" % (day, day)
            else:
                html += u"<td/>"

        left = max_days - len(days)
        while left:
            html += u"<td/>"
            left -= 1

        html += u"</tr>"

    html += u"</tbody></table>\n"

    return html


def update_schedule(html):
    fn = "output/volunteer/index.html"

    src = open(fn, "rb").read()
    dst = src.replace("<!-- schedule -->", html.encode("utf-8"))
    open(fn, "wb").write(dst)

    print "info   : updated %s with a schedule" % fn


def schedule(start_date, end_date):
    reserves = load_data("input/volunteer/history.txt")

    schedule = get_schedule(
        parse_date(start_date),
        parse_date(end_date),
        reserves)

    html = format_schedule(schedule)

    update_schedule(html)


if __name__ == "__main__":
    schedule("2014-01-01", "2014-12-31")
