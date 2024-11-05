
#Recurcive Digit Sum (Hacker Rank)

def superDigit(n, k):
    # Write your code here
    
    Li=list(str(n))
    sumi=0
    for c in Li:
        sumi+=int(c)
    sumi*=k
    while sumi>10:
        Li=list(str(sumi))
        sumi=0
        for c in Li:
             sumi+=int(c)
    return sumi

n=4757362
k=10000
print(superDigit(n,k))