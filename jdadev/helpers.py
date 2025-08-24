from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

class EquityReportRow:
    def __init__(self, equity_obj, transaction_fees):
        self.equity = equity_obj
        self.fees = transaction_fees
        print(f"7 helper transaction_fees: {transaction_fees}")

        # ---- Basic equity data ----
        self.stock = equity_obj.stocks.ticker if equity_obj.stocks else "N/A"
        self.avg_weighted_cost = Decimal(str(equity_obj.avg_weighted_cost or 0))
        self.market_price = Decimal(str(equity_obj.daily_value or 0))
        self.target_price = Decimal(str(getattr(equity_obj.stocks, 'target_value', 0) or 0))
        self.nbr_of_stocks = int(equity_obj.nbr_of_stocks or 0)

        # ---- Fee processing helper ----
        def to_decimal(x):
            """Convert to Decimal and handle various input formats"""
            try:
                if x is None:
                    return Decimal("0")
                return Decimal(str(x))
            except (ValueError, TypeError, InvalidOperation):
                return Decimal("0")

        def to_percentage(x):
            """Convert fee to percentage (fraction of 1)"""
            d = to_decimal(x)
            if d > 1:  # If stored as percentage like 18, convert to 0.18
                return d / Decimal("100")
            return d

        # ---- Individual fee components (as percentages/fractions) ----
        self.tps_rate = to_percentage(getattr(self.fees, 'tps', 0))
        self.commission_sgi_rate = to_percentage(getattr(self.fees, 'commission_sgi', 0))
        self.commission_brvm_rate = to_percentage(getattr(self.fees, 'commission_brvm', 0))
        self.commission_dc_br_rate = to_percentage(getattr(self.fees, 'commission_dc_br', 0))

        # ---- FIXED: Correct commission calculation ----
        # Country SGI = Commission SGI * (1 + TPS) - this is the SGI commission with TPS applied
        self.country_sgi_rate = self.commission_sgi_rate * (Decimal("1") + self.tps_rate)

        # Total commission rate should be additive, not multiplicative for different fee types
        self.total_commission_rate = (
                self.country_sgi_rate +
                self.commission_brvm_rate +
                self.commission_dc_br_rate
        )

        # Sanity check: cap commission rate
        if self.total_commission_rate < 0:
            self.total_commission_rate = Decimal("0")
        elif self.total_commission_rate >= 1:  # 100% commission doesn't make sense
            self.total_commission_rate = Decimal("0.50")  # Cap at 50%

        # ---- FIXED: Gains/Losses calculations ----
        # Current gain/loss per share
        self.gain_or_loss = (self.market_price - self.avg_weighted_cost).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Potential gain/loss if target price is reached
        self.potential_gain_or_loss = (self.target_price - self.market_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # ---- FIXED: Selling price calculation ----
        # Net selling price per share after all commissions
        self.selling_price = (
                self.market_price * (Decimal("1") - self.total_commission_rate)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # ---- FIXED: Loss threshold handling ----
        # These should represent percentage thresholds (e.g., 0.20 for 20% loss)
        self.actual_loss_threshold = to_percentage(getattr(self.fees, 'actual_loss', 0))
        self.potential_loss_threshold = to_percentage(getattr(self.fees, 'potential_loss', 0))

        # ---- FIXED: Decision logic ----
        self.decision = "KEEP"
        self.sale_amount = Decimal("0.00")

        # Additional calculated fields for better decision making
        self.total_current_value = self.market_price * Decimal(str(self.nbr_of_stocks))
        self.total_purchase_value = self.avg_weighted_cost * Decimal(str(self.nbr_of_stocks))
        self.total_gain_loss = self.total_current_value - self.total_purchase_value

        if self.nbr_of_stocks > 0:
            # ---- Condition 1: Actual loss threshold ----
            condition_actual = False
            if self.avg_weighted_cost > 0:
                # Calculate actual loss percentage: (purchase_price - current_price) / purchase_price
                actual_loss_pct = (self.avg_weighted_cost - self.market_price) / self.avg_weighted_cost
                if actual_loss_pct >= self.actual_loss_threshold:
                    condition_actual = True

            # ---- Condition 2: Potential upside too low ----
            condition_potential = False
            if self.market_price > 0:
                # Calculate potential gain percentage: (target_price - current_price) / current_price
                potential_gain_pct = (self.target_price - self.market_price) / self.market_price
                # If potential gain is less than the minimum required threshold, consider selling
                if potential_gain_pct <= self.potential_loss_threshold:
                    condition_potential = True

            # ---- Decision making ----
            if condition_actual or condition_potential:
                self.decision = "SELL"
                # Calculate net sale amount after commissions
                gross_sale_amount = self.market_price * Decimal(str(self.nbr_of_stocks))
                self.sale_amount = (
                        gross_sale_amount * (Decimal("1") - self.total_commission_rate)
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                #print(f"self.sale_amount: {self.sale_amount}")
            else:
                # Additional logic for more nuanced decisions
                if self.gain_or_loss > 0:
                    gain_pct = self.gain_or_loss / self.avg_weighted_cost if self.avg_weighted_cost > 0 else Decimal("0")
                    if gain_pct >= Decimal("0.20"):  # 20% or more gain
                        self.decision = "CONSIDER_SELL"  # Take profits
                    elif gain_pct >= Decimal("0.10"):  # 10-20% gain
                        self.decision = "KEEP" #HOLD
                    else:
                        self.decision = "KEEP"
                else:
                    # For losses, be more conservative
                    loss_pct = abs(self.gain_or_loss) / self.avg_weighted_cost if self.avg_weighted_cost > 0 else Decimal("0")
                    if loss_pct >= Decimal("0.15"):  # 15% or more loss
                        self.decision = "REVIEW"  # Review position
                    else:
                        self.decision = "KEEP"

        # ---- Additional metrics for reporting ----
        self.gain_loss_percentage = Decimal("0")
        if self.avg_weighted_cost > 0:
            self.gain_loss_percentage = (
                    self.gain_or_loss / self.avg_weighted_cost * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        self.potential_gain_loss_percentage = Decimal("0")
        if self.market_price > 0:
            self.potential_gain_loss_percentage = (
                    self.potential_gain_or_loss / self.market_price * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def to_dict(self):
        """Convert to dictionary for easy template rendering"""
        return {
            'stock_symbol': self.stock,
            'average_weighted_cost': self.avg_weighted_cost,
            'market_price': self.market_price,
            'gain_loss': self.gain_or_loss,
            'gain_loss_percentage': self.gain_loss_percentage,
            'target_price': self.target_price,
            'potential_gain_loss': self.potential_gain_or_loss,
            'potential_gain_loss_percentage': self.potential_gain_loss_percentage,
            'selling_price': self.selling_price,
            'number_of_shares': self.nbr_of_stocks,
            'decision': self.decision,
            'sale_amount': self.sale_amount,
            'total_current_value': self.total_current_value,
            'total_purchase_value': self.total_purchase_value,
            'total_gain_loss': self.total_gain_loss,
            'commission_rate': self.total_commission_rate * Decimal("100"),  # As percentage
        }

    def __str__(self):
        return f"{self.stock}: {self.decision} - Gain/Loss: ${self.gain_or_loss} ({self.gain_loss_percentage}%)"


# # Example usage in your view:
# def generate_equity_report(client, transaction_fees):
#     """Generate equity report using the fixed EquityReportRow class"""
#     equity_positions = ClientEquityAndRightsModel.objects.filter(
#         client=client
#     ).select_related('stocks')
#
#     report_rows = []
#     for equity in equity_positions:
#         row = EquityReportRow(equity, transaction_fees)
#         report_rows.append(row.to_dict())
#
#     # Calculate summary statistics
#     total_portfolio_value = sum(Decimal(str(row['total_current_value'])) for row in report_rows)
#     total_gain_loss = sum(Decimal(str(row['total_gain_loss'])) for row in report_rows)
#
#     return {
#         'positions': report_rows,
#         'summary': {
#             'total_portfolio_value': total_portfolio_value,
#             'total_gain_loss': total_gain_loss,
#             'total_positions': len(report_rows),
#             'sell_recommendations': len([r for r in report_rows if r['decision'] == 'SELL']),
#             'hold_recommendations': len([r for r in report_rows if r['decision'] in ['HOLD', 'KEEP']]),
#         }
#     }