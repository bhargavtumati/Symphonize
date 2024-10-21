#!/bin/python3



#
# Complete the 'highestValuePalindrome' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING s
#  2. INTEGER n
#  3. INTEGER k
#

def highestValuePalindrome(s, n, k):
    # Write your code here
    Li=[]
    for i in range(len(s)):
        Li.append(s[i])
    if len(Li)==1:
        return "9";
    changes=[0]*len(Li);
    if Li!=Li[::-1]:
        for i in range(int(len(Li)/2)+1):
            if Li[i]!=Li[n-i-1]:
                changes
    for i in range(int(len(Li)/2)+1):
        if k>1:
           
           if Li[i]!='9':
               Li[i]='9'
               k-=1
           if Li[n-i-1]!='9':
              Li[n-i-1]='9'
              k-=1

        elif k==1:
            if Li[i]!=Li[n-i-1]:
               maxi=max(int(Li[i]),int(Li[n-i-1]))
               Li[i]=str(maxi)
               Li[n-i-1]=str(maxi)
               k-=1
            if i==(n-i-1):
                maxi=9
                Li[i]=str(maxi)
                k-=1
    s=''.join(Li)
    if s==s[::-1]:
        return s
    else:
        print(s)
        return "-1"
                
            
            
    
    

if __name__ == '__main__':

    s="932239"
    n=6
    k=2
    result = highestValuePalindrome(s, n, k)

    print(result)
