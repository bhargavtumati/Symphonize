def arrayManipulation(n, queries):
    # Initialize the difference array with zeros
    diff = [0] * (n + 1)
    
    # Apply the range updates
    for c in queries:
        start, end, value = c
        diff[start - 1] += value
        if end < n:
            diff[end] -= value
    
    # Compute the prefix sum and find the maximum value
    max_value = 0
    current_value = 0
    for i in range(n):
        current_value += diff[i]
        if current_value > max_value:
            max_value = current_value
    
    return max_value


queries=[[1,5,3],[4,8,7],[6,9,1]]
n=10
print(arrayManipulation(n,queries))