from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        if not head or not head.next:
            return
        
        Li = []
        dum = head.next
        while dum:
            Li.append(dum.val)
            dum = dum.next
        
        Fir = True
        Sec = False
        while head:
            if len(Li) > 0 and Fir:
                head.next = ListNode(Li.pop())
                head = head.next
                Fir = False
                Sec = True
            if len(Li) > 0 and Sec:
                head.next = ListNode(Li[0])
                del Li[0]
                head = head.next
                Sec = False
                Fir = True
            else:
                break

def printList(head: Optional[ListNode]) -> None:
    while head:
        print(head.val, end=" -> ")
        head = head.next
    print("None")

# Example usage:
if __name__ == "__main__":
    # Create a linked list: 1 -> 2 -> 3 -> 4
    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    
    print("Original list:")
    printList(head)
    
    # Reorder the list
    sol = Solution()
    sol.reorderList(head)
    
    print("Reordered list:")
    printList(head)
