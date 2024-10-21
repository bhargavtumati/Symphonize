def queensAttack(n, k, r_q, c_q, obstacles):
    # Directions: (row change, column change)
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # vertical and horizontal
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # diagonals
    ]
    
    # Convert obstacles list to a set of tuples for faster lookup
    obstacle_set = set((r, c) for r, c in obstacles)
    
    attackable_squares = 0
    
    # Check each direction
    for dr, dc in directions:
        current_row, current_col = r_q, c_q
        
        while True:
            current_row += dr
            current_col += dc
            
            # Check if the new position is out of bounds
            if current_row < 1 or current_row > n or current_col < 1 or current_col > n:
                break
            
            # Check if the new position is an obstacle
            if (current_row, current_col) in obstacle_set:
                break
            
            # If neither, it's an attackable square
            attackable_squares += 1
    
    return attackable_squares

r_q,c_q=4187, 5068
obstacles=[]
n=100000
k=0
print(queensAttack(n,k,r_q,c_q,obstacles))