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

 

def lex(s: str) -> list:
    return re.findall(r"\\[a-z]+|[\^\_\{\}\(\)]|[\d]+|[^\\\^\_\{\}\(\)]|[\da-z]+[^\\\^\_\{\}\(\)][\da-z]+", s, re.I)

    
#.group() to get each elem
    
class TokenIterator(object):
    def __init__(self, input):
        self.tokens = self.next_token = re.finditer(r"\\[a-z]+|[\^\_\{\}\(\)]|[\d]+|[^\\\^\_\{\}\(\)]|[\da-z]+[^\\\^\_\{\}\(\)][\da-z]+", input, re.I)
        
    def __next__(self):
        self.next_token = self.tokens
        if not self.is_empty():
            return next(self.tokens).group()
        else:
            return
    
    def is_empty(self):
        if not (next(self.tokens)):
            return True
        return False
        
    def peek(self):
        next(self.next_token)
        return next(self.next_token).group()
        

class Expr(object):
    def __init__(self, operator, args):
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
 
    def __str__(self):
        if self.op == '\\frac':
            return "Frac(%s,%s)"% tuple(map(str, self.args))
        elif self.op == '\\sqrt':
            return "Sqrt(%s)" % str(self.args[0])
        elif self.op == '\\root':
            return "Root(%s, %s)" % tuple(map(str, self.args))
        elif self.op == '\\pi':
            return 'Pi' # unicode symbol for lowercase pi
        elif self.op == '_':
            return '_(%s)' % str(self.args[0])
        elif self.op == '^':
            return '^(%s)' % str(self.args[0])
        elif self.op == 'p_':
            return '_(%s,%s)' % tuple(map(str, self.args))
        elif self.op == 'p^':
            return '^(%s,%s)' % tuple(map(str, self.args))
        elif self.is_value():
            return repr(self.op) # value
        elif self.is_concat():
            return 'Concat(' + ', '.join(map(str, self.args)) + ')'
        else:
            me = "Expr(op=(%s), args=(%s)" % (repr(self.op), repr(self.args))
            raise RuntimeError("Malformed Expr: " + me)
 
    def __repr__(self) -> str:
        return "<Repr of Expr> " + str(self)
        
 
def parse_expr(tokens: Iterator, prefix) -> Expr:
    "Parses an iterator of tokens, using next(tokens) to get the next token"
    for token in tokens:
        if not bool(prefix):  #falsey
            # token = next(tokens)
            # print (token)
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
    return parse_expr_list(iter(lex(s)))
    
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
   
    # raise NotImplementedError("Apply Super/Subscripts")
    return box
 
def frac_renderer(expr):
    L = expr.args
    num, den = map(render_box, L)
    rows = num.rows + den.rows + 1
    cols = max(num.cols, den.cols) + 2
    b = Box(rows, cols)
    # num loc
    num_startx, num_starty = (cols - num.cols)//2, 0
    num_endx, num_endy = num_startx + num.cols, num_starty + num.rows
    b[num_starty:num_endy, num_startx:num_endx] = num
    # line loc
    line = FRAC_BAR * cols
    line_y = num.rows
    b[line_y, 0:cols] = line
    # den loc
    den_startx, den_starty = (cols - den.cols)//2, rows - den.rows
    den_endx, den_endy = den_startx + den.cols, rows
    b[den_starty:den_endy, den_startx:den_endx] = den
    return b    
    
def sqrt_renderer(expr):
    L = expr.args
    val = render_box(L[0])
    rows = val.rows + 1
    cols = val.cols + val.rows
    b = Box(rows, cols)
    # val loc
    val_startx, val_starty = b.cols - val.cols, 1
    b[val_starty:, val_startx:] = val
    #top bar loc
    top_bar = SQRT_TOP * val.cols
    b[0, val_startx:] = top_bar
    #side bar loc
    for i in range(val.rows):
        x, y = i, val.rows-i
        b[y, x] = SQRT_SLASH
    #check loc  
    b[val.rows, 0] = SQRT_BASE
    return b
    

   
def root_renderer(expr):
    raise NotImplementedError()
   
def pi_renderer(expr):
    return Box.from_str(PI)
   
def concat_renderer(expr):
    L = expr.args
    rend_L = list(map(render_box, L))
    rows, cols, depth, baseline = 0, 0, 0, 0
    for i in rend_L:
        if i.rows > rows:
            rows = i.rows
        cols += i.cols
        # depth += i.depth
        # baseline += i.baseline
    b = Box(rows, cols)
    x_loc = 0
    for elem in rend_L:
        x_lim = x_loc + elem.cols
        b[0:elem.rows, x_loc:x_lim] = elem
        x_loc = x_lim
    return b
   
def value_renderer(expr):
    return Box.from_str(expr.op)
    
