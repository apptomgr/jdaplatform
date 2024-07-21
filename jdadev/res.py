def adjust_bond_value(ln, bn, mu):
    max_total_value = 0.20 * ln

    # Ensure bn + mu does not exceed 20% of ln
    if bn + mu > max_total_value:
        bn = max_total_value - mu

    return bn, mu

# Example usage
ln = 21965043  # Initial liquidity value
bn = 10396681   # Initial bond value
mu = 174578    # Initial mutual fund value

adjusted_bn, adjusted_mu = adjust_bond_value(ln, bn, mu)
print("Adjusted Bond Value:", adjusted_bn)
print("Adjusted Mutual Fund Value:", adjusted_mu)