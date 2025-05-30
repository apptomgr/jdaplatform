from decimal import Decimal

class EquityReportRow:
    def __init__(self, equity_obj, transaction_fees):
        self.equity = equity_obj
        self.fees = transaction_fees

        # Pull fields from equity model
        self.stock = equity_obj.stocks.ticker if equity_obj.stocks else "N/A"
        self.avg_weighted_cost = equity_obj.avg_weighted_cost or Decimal("0.00")
        self.market_price = equity_obj.daily_value or Decimal("0.00")
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
        self.gain_or_loss = self.avg_weighted_cost - self.market_price
        self.potential_gain_or_loss = self.target_price - self.market_price

        # Calculate actual loss and potential loss values for the decision formula
        self.actual_loss = self.fees.actual_loss if hasattr(self.fees, 'actual_loss') and self.fees.actual_loss else Decimal("0.00")
        self.potential_loss = self.fees.potential_loss if hasattr(self.fees, 'potential_loss') and self.fees.potential_loss else Decimal("0.00")

        # Determine selling price
        self.selling_price = self.market_price * (1 - self.total_commission)

        # Implement the decision logic from the formula
        self.decision = "KEEP"  # Default to KEEP

        # Only proceed with decision logic if we have shares
        if self.nbr_of_stocks > 0:
            condition1 = False
            condition2 = False

            # Condition 1: Market price vs weighted cost
            if self.avg_weighted_cost > 0:
                ratio1 = self.market_price / self.avg_weighted_cost
                if ratio1 <= (1 - self.actual_loss):
                    condition1 = True

            # Condition 2: Target price vs market price
            if self.market_price > 0:
                ratio3 = self.target_price / self.market_price
                if ratio3 <= (1 - self.potential_loss):
                    condition2 = True

            # Final decision
            if condition1 or condition2:
                self.decision = "SELL"
            # Calculate sale amount based on decision
            if self.decision == "SELL":
                self.sale_amount = self.selling_price * self.nbr_of_stocks
            else:  # KEEP
                self.sale_amount = Decimal("0.00")


        # if self.nbr_of_stocks > 0:
        #     condition1 = False
        #     condition2 = False
        #
        #     # Check if (Stock Market Price/Weighted Average Cost<=(1-Actual Loss) AND Stock Target Price/Client Stock Shares<1)
        #     if self.avg_weighted_cost > 0:  # Prevent division by zero
        #         ratio1 = self.market_price / self.avg_weighted_cost
        #         if ratio1 <= (1 - self.actual_loss):
        #             if self.nbr_of_stocks > 0:  # Extra check for division by zero
        #                 ratio2 = self.target_price / self.nbr_of_stocks
        #                 if ratio2 < 1:
        #                     condition1 = True
        #
        #     # Check if (Stock Target Price/Stock Market Price<=(1-Potential Loss))
        #     if self.market_price > 0:  # Prevent division by zero
        #         ratio3 = self.target_price / self.market_price
        #         if ratio3 <= (1 - self.potential_loss):
        #             condition2 = True
        #
        #     # If either condition is true, decision is SELL
        #     if condition1 or condition2:
        #         self.decision = "SELL"
        #
        # # Calculate sale amount based on decision
        # if self.decision == "SELL":
        #     self.sale_amount = self.selling_price * self.nbr_of_stocks
        # else:  # KEEP
        #     self.sale_amount = Decimal("0.00")