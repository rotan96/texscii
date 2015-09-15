from collections.abc import Iterator
import re
 
# dict of command to number of arguments
commands = {
    r'\frac': 2,
    r'\sqrt': 1,
    r'\root': 2,
    r'\pi': 0,
    r'_': 1,
    r'^': 1
}
 

def lex(s: str) -> list:
    return re.findall(r"\\[a-z]+|[\^\_\{\}\(\)]|[^\\\^\_\{\}\(\)]|[\da-z]+[^\\\^\_\{\}\(\)][\da-z]+|[\da-z]+", s, re.I)


class Expr(object):
    def __init__(self, operator: str, args: list):
        self.op = self.value = operator
        self.args = args
       
        if type(operator) != str:
            raise TypeError('The first argument to Expr must be a str')
           
        if type(args) != list:
            errmsg = 'The second argument to Expr must be a list of Expr s'
            raise TypeError(errmsg)
           
        for a in args:
            if not isinstance(a, Expr):
                msg = 'The second argument to Expr must be a list of Expr s'
                raise TypeError(msg)
       
    def is_value(self):
        return not self.args
       
    def is_concat(self):
        return not self.op and self.args
 
    def __str__(self) -> str:
        if self.op == '\\frac':
            return "(%s)/(%s)"% tuple(map(str, self.args))
        elif self.op == '\\sqrt':
            return "sqrt(%s)" % str(self.args[0])
        elif self.op == '\\root':
            return "(%s) root of (%s)" % tuple(map(str, self.args))
        elif self.op == '\\pi':
            return '\u03c0' # unicode symbol for lowercase pi
        elif self.op == '_':
            return '_ (%s)' % str(self.args[0])
        elif self.op == '^':
            return '^ (%s)' % str(self.args[0])
        elif self.op == 'p_':
            return '_(%s)(%s)' % tuple(map(str, self.args))
        elif self.op == 'p^':
            return '^(%s)(%s)' % tuple(map(str, self.args))
        elif self.is_value():
            return self.op # value
        elif self.is_concat():
            return '{(' + ') & ('.join(map(str, self.args)) + ')}'
        else:
            me = "Expr(op=(%s), args=(%s)" % (repr(self.op), repr(self.args))
            raise RuntimeError("Malformed Expr: " + me)
 
    def __repr__(self) -> str:
        return "<Expr> " + str(self)
 
 
def parse_expr(tokens: Iterator, prefix=[]) -> Expr:
    "Parses an iterator of tokens, using next(tokens) to get the next token"
    if not bool(prefix):  #falsey
        token = next(tokens)
        if token == "{":
            return parse_expr_list(tokens)
        elif token == "}":
            return None
        elif token == r"\pi":
            return Expr('\\pi', [])
        elif token == r"\sqrt":
            return Expr('\\sqrt', [parse_expr(tokens)])
        elif token == r"_":
            return Expr('_', [parse_expr(tokens)])
        elif token == r"^":
            return Expr('^', [parse_expr(tokens)])
        elif token == r"\frac":
            return Expr('\\frac', [parse_expr(tokens),parse_expr(tokens)])
        elif token == r"\root":
            return Expr('\\root', [parse_expr(tokens),parse_expr(tokens)])
        else:
            if token in commands.keys() or token.startswith('\\'):
                raise ValueError("A command cannot be a Value")
            return Expr(token, [])
    else:  #changes ^ and _ to not be infixed
        if prefix[0] == r"_":
            return Expr('p_', prefix[1:])
        elif prefix[0] == r"^":
            return Expr('p^', prefix[1:])

        
            
def parse_expr_list(tokens: Iterator): #-> Expr:
    exprList = []
    expression = parse_expr(tokens)
    while expression != None:
        if expression.op == "^" or expression.op == "_":
            expression = parse_expr(tokens, [expression.op, exprList.pop(), expression.args[0]])
        exprList.append(expression)
        expression = parse_expr(tokens)
    for e in exprList:
        if not isinstance(e, Expr):
            raise TypeError("I can only concatenate Expr instances") 
    return Expr('', exprList)
    # raise NotImplementedError("You have to implement this function!")

 
def parse(s: str): #-> Expr:
    "Completed, do not modify"
    return parse_expr_list(iter(lex(s + '}')))