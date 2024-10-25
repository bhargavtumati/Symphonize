def climbingLeaderboard(ranked, player):
    # Remove duplicates and sort in descending order
    ranked = sorted(set(ranked), reverse=True)
    ranks = []
    
    for score in player:
        low, high = 0, len(ranked)
        
        # Binary search to find the rank
        while low < high:
            mid = (low + high) // 2
            if ranked[mid] > score:
                low = mid + 1
            else:
                high = mid
        
        ranks.append(low + 1)
    
    return ranks

# Example usage
ranked = [100, 90, 90, 80, 75, 60]
player = [50, 65, 77, 90, 102]
print(climbingLeaderboard(ranked, player))  # Output: [6, 5, 4, 2, 1]
