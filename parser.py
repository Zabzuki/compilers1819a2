
import plex

# ... συμπληρώστε τον κώδικά σας για τον συντακτικό αναλυτή - αναγνωριστή της γλώσσας ...

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	def __init__(self):
		letter = plex.Range('azAZ')
		digit = plex.Range('09')	
		space = plex.Any(" \n\t")
		parenthesis = plex.Str('(', ')')
		id_token = letter + plex.Rep(letter|digit)
		bit = plex.Range('01')
		bits = plex.Rep1(bit)
		print_token = plex.Str('print', 'PRINT')
		space = plex.Any(" \n\t")
		operators = plex.Str('=', 'xor', 'and','or')
		self.LEXICON = plex.Lexicon([
			(space, plex.IGNORE),
			(operators, plex.TEXT),
			(bits, 'BIT_TOKEN'),
			(parenthesis, plex.TEXT),
			(print_token, 'PRINT'),
			(id_token, 'IDENTIFIER')
			])

	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """
		self.scanner = plex.Scanner(self.LEXICON, fp)
		# get the initial lookahead
		self.la, self.text = self.next_token()
		
	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		return self.scanner.read()

	def match(self, token):
		""" Consumes (matches with current lookahead) an expected token. 
		Raises ParseError if anything else is found. Acquires new lookahead. """		
		if self.la == token:
			# create the plex scanner for fp
			self.la, self.text = self.next_token()
		else:
			raise ParseError("found (")

	def parse(self, fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		# create the plex scanner for fp
		self.create_scanner(fp)
		# call parsing logic
		self.stmt_list()
		
	def stmt_list(self):
		if self.la == 'IDENTIFIER' or self.la == 'PRINT':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("waiting for IDENTIFIER or PRINT")
	
	def stmt(self):
		if self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')	
			self.match('=')
			self.expr()
		elif self.la == 'PRINT':
			self.match('PRINT')
			self.expr()
		else:
			raise ParseError("waiting for IDENTIFIER or PRINT")
	
	def expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			self.term()
			self.term_tail()
		else:
			raise ParseError("waiting for ( , IDENTIFIER , BIT_TOKEN or )")
	
	def term_tail(self):	
		if self.la == 'xor':
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("waiting for xor")
	
	def term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':	
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("waiting for ( , IDENTIFIER or )")
	
	def factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("waiting for or")
	
	def factor(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("waiting for IDENTIFIER, BIT_TOKEN or (")
	
	def atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la == 'or' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("waiting for and")
	
	def atom(self):
		if self.la == '(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
		elif self.la == 'BIT_TOKEN':
			self.match('BIT_TOKEN')
		else:
			raise ParseError("waiting for IDENTIFIER, BIT_TOKEN or (")

# the main part of prog

# create the parser object
parser = MyParser()
# open file for parsing
with open('test.txt','r') as fp:
	parser.parse(fp)