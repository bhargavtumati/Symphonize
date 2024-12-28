import math


def encryption(s):
    # Write your code here
    
    s.replace(" ", "")
    rowlength=math.sqrt(len(s))
    slength=len(s)
    root=math.sqrt(len(s))
    
    if str(rowlength).endswith(".0"):
        rowlength=colleng=int(rowlength)
    elif rowlength>int(rowlength):
        colleng=int(rowlength)+1
        rowlength=int(rowlength)
    words=[]
    for i in range(colleng):
        
        words.append(s[:colleng])

        if len(s)>colleng:
            s=s[colleng:]
        else :
            if words[-1] != s:
                words.append(s)
            break

        
    
    encrypt=""
    i=0
    while i <= colleng:
       for word in words:
          if len(word)>i:
              encrypt+=word[i]
       encrypt+=" "  
       i+=1   
    return encrypt

s="haveaniceday"  
j="wclwfoznbmyycxvaxagjhtexdkwjqhlojykopldsxesbbnezqmixfpujbssrbfhlgubvfhpfliimvmnny"          
print(encryption(s))