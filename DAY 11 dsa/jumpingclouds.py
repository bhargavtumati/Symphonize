def jumpingOnClouds(c):
    # Write your code here
    i=0
    j=0
    count=0
    while i<len(c) and j<len(c):
       if (i+2)<len(c) and c[i+2]==0:
           count+=1
           i+=2
       elif (i+1)<len(c) and c[i+1]==0:
           count+=1
           i+=1
       j+=1
    if i==len(c)-1:
        return count
    else:
        -1 

c=[0, 1,0,0,0,0]
print(jumpingOnClouds(c))