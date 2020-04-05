from datetime import datetime, timedelta
from decimal import Decimal

SCATTER_PARAMS = {"line": {"width": 1}}


def percent(value):
    return round(value * 100, 1)


def load_quotes(path):
    quotes = {}

    for line in open(path):
        line = line.strip()
        if not line:
            continue

        date, quote = line.split(",")
        quotes[_parse_date(date)] = Decimal(quote)

    return quotes


def get_currency_rate(date):
    return get_quote(_CURRENCY_RATES, date)


def get_quote(quotes, date):
    checked = False

    while True:
        try:
            return quotes[date]
        except KeyError:
            if not checked:
                min_date = sorted(quotes)[0]
                if date < min_date:
                    raise Exception("There are no quotes for {}".format(date))
                checked = True

            date = date - timedelta(days=1)


def _parse_date(date):
    try:
        date = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        date = datetime.strptime(date, "%Y-%m-%d")

    return date.date()


# http 'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01.01.2000&date_req2=31/12/2020&VAL_NM_RQ=R01235' | sed 's/,/./g' | sed -r 's#<Record Date="([^"]+)" Id="R01235"><Nominal>1</Nominal><Value>([^<]+)</Value></Record>#\1,\2\n#g' > usd.csv
_CURRENCY_RATES = load_quotes("usd.csv")
