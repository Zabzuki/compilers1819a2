import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	def __init__(self):
		space = plex.Any(' \n\t')
		open_paren = plex.Str('(')
		close_paren = plex.Str(')')
		letter = plex.Range("Azaz")
		digit  = plex.Range("09")
		id_token = letter + plex.Rep(letter|digit)
		binary = plex.Range("01")
		bits = plex.Rep1(binary)
		AND = plex.Str('and')
		OR = plex.Str('or')
		XOR = plex.Str('xor')
		equal = plex.Str('=')
		keyword = plex.Str('print')
		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		self.Lexicon = plex.Lexicon([(space, plex.IGNORE),
									(equal, '='),
									(XOR, 'xor'),
									(AND, 'and'),
									(OR, 'or'),
									(open_paren, '('),
									(close_paren, ')'),
									(keyword, 'print'),
									(id_token, 'id'),
									(bits, 'BIT_TOKEN')
									])
				
	def create_scanner(self,fp):
		self.scanner = plex.Scanner(self.Lexicon, fp)
		self.la, self.text = self.next_token()
		
	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		return self.scanner.read()		

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		if self.la==token:
			self.la,self.text = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		self.create_scanner(fp)
		self.stmt_list()
	
	def stmt_list(self):
		if self.la in ("id", "print"):
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("{} wasn't an 'id', 'print' or 'None' token!".format(self.la))

	def stmt(self):
		if self.la == "id":
			self.match("id")
			self.match("=")
			self.expr()
		elif self.la == "print":
			self.match("print")
			self.expr()
		else:
			raise ParseError("{} wasn't an 'id' or 'print' token!".format(self.la))
	
	def expr(self):
		if self.la in ("(","id", "BIT_TOKEN"):
			self.term()
			self.term_tail()
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))
		
	def term_tail(self):
		if self.la == "xor": 
			self.match("xor")
			self.term()
			self.term_tail()
		elif self.la in ("id", "print", ")", None):
			return
		else:
			raise ParseError("{} wasn't an 'xor', 'id', 'print' or ')' token!".format(self.la))
	
	def term(self):
		if self.la in ("(","id", "BIT_TOKEN"):
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))
		
	def factor_tail(self):
		if self.la == "or":
			self.match("or")
			self.factor()
			self.factor_tail()
		elif self.la in ("xor", "id", "print", ")", None):
				return
		else:
			raise ParseError("{} wasn't an 'xor', 'id', 'print' or ')' token!".format(self.la))

	def factor(self):
		if self.la in ("(", "id", "BIT_TOKEN"):
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))

					
	def atom_tail(self):
		if self.la == "and":
			self.match("and")
			self.atom()
			self.atom_tail()
		elif self.la in ("xor", "or", "print", "id", ")", None):
			return
		else:
			raise ParseError("{} was not what i expected!".format(self.la))

	def atom(self):
		if self.la == "(":
			self.match("(")
			self.expr()
			self.match(")")
		elif self.la == ("id"):
			self.match("id")
		elif self.la == ("BIT_TOKEN"):
			self.match("BIT_TOKEN")
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))
	
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("test.txt") as fp:
    parser.parse(fp)
