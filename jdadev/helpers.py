from decimal import Decimal

class EquityReportRow:
    def __init__(self, equity_obj, transaction_fees):
        self.equity = equity_obj
        self.fees = transaction_fees

        # Pull fields from equity model
        self.stock = equity_obj.stocks.ticker if equity_obj.stocks else "N/A"
        self.avg_weighted_cost = equity_obj.avg_weighted_cost or Decimal("0.00")
        self.market_price = equity_obj.daily_value or Decimal("0.00")
        #self.gain_or_loss = (equity_obj.avg_weighted_cost - equity_obj.daily_value) or Decimal("0.00")
        self.target_price = equity_obj.stocks.target_value if equity_obj.stocks and equity_obj.stocks.target_value else Decimal("0.00")

        self.nbr_of_stocks = equity_obj.nbr_of_stocks or 0

        # Pull transaction fee components
        self.tps = self.fees.tps or Decimal("0.00")
        self.commission_sgi = self.fees.commission_sgi or Decimal("0.00")
        self.commission_brvm = self.fees.commission_brvm or Decimal("0.00")
        self.commission_dc_br = self.fees.commission_dc_br or Decimal("0.00")

        # Derived calculations
        self.country_sgi = (1 + self.tps) * self.commission_sgi
        self.total_commission = self.country_sgi + self.commission_brvm + self.commission_dc_br
        self.gain_or_loss = self.market_price - self.avg_weighted_cost
        self.potential_gain_or_loss = self.target_price - self.market_price
        self.selling_price = self.market_price * (1 - self.total_commission)
        self.sale_amount = self.selling_price * self.nbr_of_stocks
        self.decision = "SELL" if self.potential_gain_or_loss <= 0 else "KEEP"
