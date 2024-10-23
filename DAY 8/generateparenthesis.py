from typing import List



def generateParenthesis( n: int) -> List[str]:
        def generateParenthesisHelper(open, close, s, result):
            if open==close and s:
                result.append(s)
            if open>0:
                generateParenthesisHelper(open-1,close,s+"(",result)
            if close>open:
                generateParenthesisHelper(open,close-1,s+")",result)

            return
        result=[]
        generateParenthesisHelper(n,n,"",result)
        return result

print(generateParenthesis(2))