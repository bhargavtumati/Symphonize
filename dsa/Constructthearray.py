def countArray(n, k, x):
    mod = 1000000007
    a = [0] * n
    b = [0] * n
    
    a[0] = 1 if x == 1 else 0      #if x is also equal to 1 then this condition 
    b[0] = 0 if x == 1 else 1
    
    for i in range(1, n):
        a[i] = b[i - 1] % mod
        b[i] = (a[i - 1] * (k - 1) + b[i - 1] * (k - 2)) % mod
    
    return a[n - 1]

# Example usage:
n = 5
k = 3
x = 1
print(countArray(n, k, x))  # Output will depend on the values of n, k, and x
