def nonDivisibleSubset(k, s):
    # Create a list to count the frequency of remainders
    remainder_count = [0] * k
    
    # Count the frequency of each remainder
    for num in s:
        remainder_count[num % k] += 1
    
    # Initialize the subset size
    subset_size = min(remainder_count[0], 1)
    
    # Iterate over the possible remainders
    for i in range(1, (k // 2) + 1):
        if i != k - i:
            subset_size += max(remainder_count[i], remainder_count[k - i])
        else:
            subset_size += 1
    
    return subset_size

# Example usage
k = 3
s = [1, 7, 2, 4]
print(nonDivisibleSubset(k, s))  # Output: 3
