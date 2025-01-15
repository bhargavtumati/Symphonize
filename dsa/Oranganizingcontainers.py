def organizingContainers(containers):
    # Calculate row sums and column sums
    row_sums = [sum(container) for container in containers]
    col_sums = [sum(containers[i][j] for i in range(len(containers))) for j in range(len(containers[0]))]
    
    # Sort both row sums and column sums
    row_sums.sort()
    col_sums.sort()
    
    # Check if sorted row sums match sorted column sums
    if row_sums == col_sums:
        return "Possible"
    else:
        return "Impossible"



containers=[[1,1,1],[1,1,1],[1,1,1]]
print(organizingContainers(containers))