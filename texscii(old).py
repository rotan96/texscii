#input: sin^{3}(\frac{1}{3}\pi)=\frac{3}{8}\sqrt{3}
#list: ["sin","^",["3"],"(","\frac",["1"],["3"],"\pi",")=","\frac",["3"],["8"],"\sqrt",["3"]]

#input: \frac{\sqrt{5}}{x^7}^{4}
#list: ["\frac",["\sqrt",["5"]],["x","^",["7"]],"^",["4"]]

#r"string" for raw string

# data Shrub a = Twig | Leaf a | Branch (Shrub a) (Shrub a)
# data Expr a = Value a | Sqrt (Expr a) | Frac (Expr a) (Expr a)


#π


class Expr:
    def __init__(self, type, *args):
        self.type = type
        self.args = args
        
    def __str__(self):
        if not self.type:
            return '[%s]' % ', '.join(map(str, self.args))
        if not self.args:
            return "<%s>" % self.type
        if len(self.args) == 1:
            return "Expr(%s, %s)"% (repr(self.type), str(self.args[0]))
        return "Expr(%s, [%s])" % (repr(self.type), ', '.join(map(str, self.args)))
        
    def __repr__(self):
        return str(self)
        
def fraction(numden):
    num, den = numden
    return "FRACTION", num, den
    
def sqrt(operand):
    # √
    return "SQRT", operand
    
def sup(power):
    return "CARAT", power
        
def lexer(s):
    l = []
    while len(s) != 0:
        if s[0] == "\\":
            i = 1
            while i < len(s) and s[i].isalpha():
                i += 1
            l.append(s[0:i])
            s = s[i:]
        else:
            l.append(s[0])
            s = s[1:]
    return l
    
def findArgs(ex,l):
    sum = 0
    for i in range(l.index(ex) + 1,len(l)):
        if l[i] == "{":
            sum += 1
        elif l[i] == "}":
            sum -= 1
        if sum == 0:
            return ["".join(l[l.index(ex) + 2:i])]  #makes sure outside brackets aren't included
            
def removeArg(l):
    #removes first argument
    openInd, closeInd = 0, 0
    for i in range(len(l)):
        if l[i] == "{":
            openInd = i
        elif l[i] == "}":
            closeInd = i
            # print openInd, closeInd,  l[:openInd] + l[closeInd + 1:]
            return l[:openInd] + l[closeInd + 1:]
            
def getArgs(l):
    exprList = []
    argNumber = {"\\frac":2, "\\sqrt":1, "\\root":2, "^":1}  #num of arguments
    for i in range(len(l)):
        if "\\" in l[i] or "^" in l[i] or "_" in l[i]:
            arguments = findArgs(l[i], l[i:])
            if argNumber[l[i]] == 2:
                newL = removeArg(l[i:])
                arguments += findArgs(l[i], newL)
            exprList.append(Expr(l[i], *arguments))
    return exprList
            
def writeAscii(exprList):
    asciiList = []
    for expr in exprList:
        # print("HI", expr.type, expr.type == "\\frac")
        print(expr.args)
        if expr.type == "\\frac":
            print(fraction(expr.args))
        elif expr.type == "\sqrt":
            print(sqrt(expr.args))

def __main__():
    inp = input("Input:" )
    inputList = lexer(inp)
    exprList = getArgs(inputList)
    print(exprList)
    writeAscii(exprList)


    
__main__()
        