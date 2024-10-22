def cost(B):
    n = len(B)
    if n == 0:
        return 0

    dp = [[0, 0] for _ in range(n)]

    for i in range(1, n):                                       
        dp[i][0] = max(dp[i-1][0], dp[i-1][1] + abs(B[i-1] - 1))                    #max(0,0)
        dp[i][1] = max(dp[i-1][0] + abs(1 - B[i]), dp[i-1][1] + abs(B[i] - B[i-1]))    #max(0+0,0+1)

    return max(dp[n-1][0], dp[n-1][1])

# Example usage:
print(cost([1, 2, 3]))  # Output: 2
#print(cost([10, 1, 10, 1, 10]))  # Output: 36

"""
1) State Definition: dp[i][0] and dp[i][1] represent the maximum cost up to the i-th element when B[i] is 1 or A[i], respectively.
2) Transition: We calculate the maximum cost for each state by considering the previous states and the absolute differences.
3) Initialization: The first element has no previous element, so both states start at 0.
4) Result: The final result is the maximum value between the two states at the last element.
"""
