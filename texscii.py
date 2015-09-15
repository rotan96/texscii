from collections.abc import Iterator
import numpy as np
import re
import abc
 
# dict of command to number of arguments
commands = {
    r'\frac': 2,
    r'\sqrt': 1,
    r'\root': 2,
    r'\pi': 0,
    r'_': 1,
    r'^': 1
}

SQRT_TOP = '_'
SQRT_BASE = '\u221a'
SQRT_SLASH = '\u2571'
# SQRT_SLASH = '/'
FRAC_BAR = '\u2500'
PI = '\u03c0'

 

# def lex(s: str) -> list:
#     return re.findall(r"\\[a-z]+|[\^\_\{\}\(\)]|[\d]+|[^\\\^\_\{\}\(\)]|[\da-z]+[^\\\^\_\{\}\(\)][\da-z]+", s, re.I)

    
#.group() to get each elem
    
class TokenIterator(object):
    def __init__(self, input):
        self.tokens = self.next_token = re.findall(r"\\[a-z]+|[\^\_\{\}\(\)]|[\d]+|[^\\\^\_\{\}\(\)]|[\da-z]+[^\\\^\_\{\}\(\)][\da-z]+", s, re.I)
        
    def __next__(self):
        return next(self.tokens).group()
    
    def is_empty(self):
        return
        
    def peek(self):
        return
        

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
 
 
def parse_expr(tokens: Iterator, prefix) -> Expr:
    "Parses an iterator of tokens, using next(tokens) to get the next token"
    if not bool(prefix):  #falsey
        token = next(tokens)
        print (token)
        if token == "{":
            return parse_expr_list(tokens)
        elif token == "}":
            return None
        elif token == r"\pi":
            return Expr('\\pi', [])
        elif token == r"\sqrt":
            return Expr('\\sqrt', [parse_expr(tokens, prefix)])
        elif token == r"_":
            return Expr('_', [parse_expr(tokens, prefix)])
        elif token == r"^":
            return Expr('^', [parse_expr(tokens, prefix)])
        elif token == r"\frac":
            return Expr('\\frac', [parse_expr(tokens, prefix),parse_expr(tokens, prefix)])
        elif token == r"\root":
            return Expr('\\root', [parse_expr(tokens, prefix),parse_expr(tokens, prefix)])
        else:
            if token in commands.keys() or token.startswith('\\'):
                raise ValueError("A command cannot be a Value")
            return Expr(token, [])
    else:  #changes ^ and _ to not be infixed
        if prefix[0] == r"_":
            return Expr('p_', prefix[1:])
        elif prefix[0] == r"^":
            return Expr('p^', prefix[1:])

        
            
def parse_expr_list(tokens: Iterator) -> Expr:
    exprList = []
    expression = parse_expr(tokens, [])
    while expression != None:
        if expression.op == "^" or expression.op == "_":
            expression = parse_expr(tokens, [expression.op, exprList.pop(), expression.args[0]])
        exprList.append(expression)
        expression = parse_expr(tokens, [])
    for e in exprList:
        if not isinstance(e, Expr):
            raise TypeError("I can only concatenate Expr instances") 
    return Expr('', exprList)
    # raise NotImplementedError("You have to implement this function!")

# if <cond>: raise SyntaxError('thing happened')
 
def parse(s: str) -> Expr:
    "Completed, do not modify"
    return parse_expr_list(iter(lex(s + '}')))
    
class Box(np.ndarray):
    FILL_CHAR = ' '
    def __new__(cls, rows=0, cols=0, clear=True, baseline=-1):
        # """If clear, then initializes box with FILL_CHAR.
# Keep in mind that baseline is measured from top of array \
# negative indices are measured from bottom and automatically \
# converted to positive indices.
# Refer to https://en.wikibooks.org/wiki/LaTeX/Boxes for explanation of \
# lengths."""
        obj = np.empty((rows, cols), dtype=np.unicode_).view(cls)
        if baseline < 0:
            obj.baseline = rows + baseline
        else:
            obj.baseline = baseline
        obj.height = obj.baseline
        obj.depth = rows - obj.baseline
        obj.width = obj.cols = cols
        obj.rows = rows
        return obj
 
    def __init__(self, rows=0, cols=0, clear=True, baseline=-1):
        if clear:
            self[:, :] = self.FILL_CHAR
 
    def __str__(self):
        return '\n'.join(
            ''.join(line) for line in self
        )
 
    @classmethod
    def from_str(cls, s):
        b = cls(rows=1, cols=len(s), clear=False)
        b[0, :] = tuple(s)
        return b
   
def render(expr):
    return str(render_box(expr))
 
def render_box(expr):
    if expr.op == r'\frac':
        box = frac_renderer(expr)
    elif expr.op == r'\sqrt':
        box = sqrt_renderer(expr)
    elif expr.op == r'\root':
        box = root_renderer(expr)
    elif expr.op == r'\pi':
        box = pi_renderer(expr)
    elif expr.op == r'':
        box = concat_renderer(expr)
    else:
        box = value_renderer(expr)
   
    raise NotImplementedError("Apply Super/Subscripts")
    return box
 
def frac_renderer(expr):
    raise NotImplementedError()
 
def sqrt_renderer(expr):
    raise NotImplementedError()
   
def root_renderer(expr):
    raise NotImplementedError()
   
def pi_renderer(expr):
    raise NotImplementedError()
   
def concat_renderer(expr):
    raise NotImplementedError()
   
def value_renderer(expr):
    raise NotImplementedError()
    
