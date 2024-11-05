def getWays(n, c):
    # Create a list to store the number of ways to get each amount
    dp = [0] * (n + 1)
    dp[0] = 1  # There's one way to get 0 amount: using no coins

    # Iterate over each coin
    for coin in c:
        for amount in range(coin, n + 1):
            dp[amount] += dp[amount - coin]

    return dp[n]

# Example usage:
n = 4
c = [1, 2, 3]
print(getWays(n, c))  # Output: 4
