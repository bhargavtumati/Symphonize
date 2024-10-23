from typing import Optional


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class Solution:
    def kthLargestLevelSum(self, root: Optional[Node], k: int) -> int:

        def bfs(root,sumar):
             if not root:
                return
             queue=[]
             queue.append(root)
             while queue:
                level_size = len(queue)
                sum=0
                while level_size>0:
                   sum+=queue[0].val
                   node=queue[0]
                   del(queue[0])
                   if node.left:
                        queue.append(node.left)
                   if node.right:
                        queue.append(node.right)
                   level_size-=1
                sumar.append(sum)
             return sumar
        sumar=bfs(root,[])
        sumar.sort()
        if len(sumar)>=k:
           return sumar[-k]
        return -1 

if __name__ == '__main__':
    s=Solution()
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    print(s.kthLargestLevelSum(root,2))