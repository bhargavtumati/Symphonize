def substrings(n):
    MOD = 1000000007
    total_sum = 0
    factor = 1
    
    for i in range(len(n) - 1, -1, -1):
        total_sum = (total_sum + int(n[i]) * factor * (i + 1)) % MOD
        factor = (factor * 10 + 1) % MOD
    
    return total_sum

# Example usage:
n = "248"
print(substrings(n))  # Output will be the sum of all substrings modulo 1000000007
