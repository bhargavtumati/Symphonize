def biggerIsGreater(w):
    # Convert the string to a list of characters
    lst = list(w)
    
    # Step 1: Find the rightmost character which is smaller than its next character
    i = len(lst) - 2
    while i >= 0 and lst[i] >= lst[i + 1]:
        i -= 1
    
    # If no such character is found, return "no answer"
    if i == -1:
        return "no answer"
    
    # Step 2: Find the smallest character on the right of the found character which is larger than the found character
    j = len(lst) - 1
    while lst[j] <= lst[i]:
        j -= 1
    
    # Step 3: Swap the found characters
    lst[i], lst[j] = lst[j], lst[i]
    
    # Step 4: Reverse the sequence after the original position of the first character
    lst = lst[:i + 1] + lst[i + 1:][::-1]
    
    # Convert the list back to a string and return
    return ''.join(lst)



w="xildrrhpca"
print(biggerIsGreater(w));