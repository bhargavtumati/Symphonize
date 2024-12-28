def equal(arr):
    def min_operations(target):
        operations = 0
        for num in arr:
            diff = num - target
            operations += diff // 5
            diff %= 5
            operations += diff // 2
            diff %= 2
            operations += diff
        return operations

    min_chocolates = min(arr)
    min_ops = float('inf')
    
    for target in range(min_chocolates, min_chocolates - 6, -1):
        min_ops = min(min_ops, min_operations(target))
    
    return min_ops

# Example usage:
print(equal([2, 2, 3, 7]))  # Output: 2
#print(equal([10, 7, 12]))   # Output: 3