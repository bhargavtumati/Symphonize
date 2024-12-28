from cmath import inf
from typing import List



def maxSubArray(nums: List[int]) -> int:
    maxSum = -inf
    currentSum = 0

    for num in nums:
        currentSum = max(num,currentSum+ num)
        maxSum = max(maxSum, currentSum)
    return maxSum

nums= [-2,1,-3,4,-1,2,1,-5,4]
print(maxSubArray(nums))