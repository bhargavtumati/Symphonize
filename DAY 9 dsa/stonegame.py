from typing import List


class Solution:
    def stoneGame(self, piles: List[int]) -> bool:

        Alice=0        #There are an even number of piles arranged in a row
        Bob=0           # The total number of stones across all the piles is odd, so there are no ties.
        for i in range(int(len(piles)/2)):
            if i%2==0:
              Alice+= max(piles[i],piles[int(len(piles)/2)-1-i])
            
              
            else:
                Bob+= max(piles[i],piles[int(len(piles)/2)-1-i])
               
        Alice+=piles[i]
        
        if Alice > Bob:
         return True
         
        else:
         return False
        


if __name__=="__main__":
    s=Solution()
    piles=[5,3,4,5,8,9,7,2]
    print(s.stoneGame(piles))