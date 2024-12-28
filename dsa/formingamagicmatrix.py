def formingMagicSquare(s):
    # All possible 3x3 magic squares
    magic_squares = [
        [8, 1, 6, 3, 5, 7, 4, 9, 2],
        [6, 1, 8, 7, 5, 3, 2, 9, 4],
        [4, 9, 2, 3, 5, 7, 8, 1, 6],
        [2, 9, 4, 7, 5, 3, 6, 1, 8],
        [8, 3, 4, 1, 5, 9, 6, 7, 2],
        [4, 3, 8, 9, 5, 1, 2, 7, 6],
        [6, 7, 2, 1, 5, 9, 8, 3, 4],
        [2, 7, 6, 9, 5, 1, 4, 3, 8]
    ]
    
    # Flatten the input square
    s_flat = [num for row in s for num in row]
    
    # Calculate the minimum cost to convert s to any magic square
    min_cost = float('inf')
    for magic in magic_squares:
        cost = sum(abs(s_flat[i] - magic[i]) for i in range(9))
        min_cost = min(min_cost, cost)
    
    return min_cost

# Example usage
s = [
    [4, 8, 2],
    [4, 5, 7],
    [6, 1, 6]
]
print(formingMagicSquare(s))  # Output: 4
