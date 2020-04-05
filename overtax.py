from decimal import Decimal

import plotly.graph_objects as go

from common import SCATTER_PARAMS, get_currency_rate, load_quotes, percent


def process_growth(fig, quotes):
    dates = sorted(quotes.keys())
    start_price = quotes[dates[0]]
    start_currency_rate = get_currency_rate(dates[0])
    start_local_price = start_price * start_currency_rate

    growth = []
    local_growth = []
    currency_rates = []

    for date in dates:
        price = quotes[date]
        currency_rate = get_currency_rate(date)
        local_price = price * currency_rate
        growth.append(percent((price - start_price) / start_price))
        local_growth.append(percent((local_price - start_local_price) / start_local_price))
        currency_rates.append(percent((currency_rate - start_currency_rate) / start_currency_rate))

    params = dict(legendgroup="growth", hovertemplate="%{y}%", **SCATTER_PARAMS)
    fig.add_trace(go.Scatter(x=dates, y=growth, name="USD", **params))
    fig.add_trace(go.Scatter(x=dates, y=local_growth, name="RUB", **params))
    fig.add_trace(go.Scatter(x=dates, y=currency_rates, name="USD/RUB", **params))


def process_period(fig, quotes, period):
    prev_month = 0
    quantity = 0

    total_cost = Decimal(0)
    total_local_cost = Decimal(0)

    dates = []
    real_taxes = []
    over_taxes = []

    for date in period:
        if date.month != prev_month:
            quantity += 1
            buy_price = quotes[date]
            total_cost += buy_price
            total_local_cost += buy_price * get_currency_rate(date)
            prev_month = date.month

        sell_price = quotes[date]
        revenue = quantity * sell_price
        local_revenue = revenue * get_currency_rate(date)

        profit = revenue - total_cost
        local_profit = local_revenue - total_local_cost

        local_tax = max(local_profit, 0) * Decimal(0.13)
        tax = local_tax / get_currency_rate(date)

        if profit > 0:
            if profit >= tax:
                real_tax, over_tax = percent(tax / profit), None
            else:
                over_tax, real_tax = percent((tax - profit) / total_cost), None
        else:
            over_tax, real_tax = percent(tax / revenue), None

        dates.append(date)
        real_taxes.append(real_tax)
        over_taxes.append(over_tax)

    fig.add_trace(go.Scatter(
        x=dates, y=real_taxes, name="{} real tax".format(period[0]),
        legendgroup="real-tax", hovertemplate="%{y}%", **SCATTER_PARAMS))

    fig.add_trace(go.Scatter(
        x=dates, y=over_taxes, name="{} over tax".format(period[0]),
        legendgroup="over-tax", hovertemplate="%{y}%", **SCATTER_PARAMS))


def main():
    stock_quotes = load_quotes("VTI.csv")

    fig = go.Figure()
    process_growth(fig, stock_quotes)

    periods = 10
    dates = sorted(stock_quotes.keys())
    period_length = len(dates) // periods

    for period_id in range(periods):
        period = dates[period_length * period_id:]
        process_period(fig, stock_quotes, period)

    fig.update_layout(title_text="Real taxes", xaxis_rangeslider_visible=True)
    fig.show()


if __name__ == "__main__":
    main()
