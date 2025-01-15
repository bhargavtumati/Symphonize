def gridSearch(G, P):
    R, C = len(G), len(G[0])  # Dimensions of the larger grid
    r, c = len(P), len(P[0])  # Dimensions of the pattern

    for i in range(R - r + 1):  # Iterate through possible starting rows
        for j in range(C - c + 1):  # Iterate through possible starting columns
            match = True
            for x in range(r):  # Check every row of the pattern
                if G[i + x][j:j + c] != P[x]:  #i+x next row
                    match = False
                    break
                
                
            if match:
                return "YES"  # Pattern found
    return "NO"  # Pattern not found

G = [
    "7283455864",
    "6731158619",
    "8983279641",
    "5244355863",
    "1234567890"
]
P = [
    "89832",
    "52443"
]

print(gridSearch(G, P))  # Output: YES
