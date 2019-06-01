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
		self.st = {}
		
	def create_scanner(self,fp):
		self.scanner = plex.Scanner(self.Lexicon, fp)
		self.la, self.text = self.next_token()	

	def next_token(self):
		return self.scanner.read()		

	def match(self,token):
		if self.la==token:
			self.la,self.text = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	def parse(self,fp):
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
		if self.la == 'id':
			varname = self.text
			self.match('id')
			self.match('=')
			self.st[varname] = self.expr()
		elif self.la == 'print':
			self.match('print')
			print('{:b}'.format(self.expr()))
		else:
			raise ParseError("{} wasn't an 'id' or 'print' token!".format(self.la))

	def expr(self):
		if self.la in ('(', 'id', 'BIT_TOKEN'):
			t = self.term()
			while self.la == 'xor':
				self.match('xor')
				t2 = self.term()
				t ^= t2
			if self.la in ('id', 'print', ')', None):
				return t
			raise ParseError("{} wasn't an 'id', 'print', ')' or 'None' token!".format(self.la))
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))

	def term(self):
		if self.la in ('(', 'id', 'BIT_TOKEN'):
			f = self.factor()
			while self.la == 'or':
				self.match('or')
				f2 = self.factor()
				f |= f2
			if self.la in ('xor', 'id', 'print', ')', None):
				return f
			raise ParseError("{} wasn't an 'xor', 'id', 'print', ')' or 'None' token!".format(self.la))
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))

	def factor(self):
		if self.la in ('(', 'id', 'BIT_TOKEN'):
			a = self.atom()
			while self.la == 'and':
				self.match('and')
				a2 = self.atom()
				a &= a2
			if self.la in ('or', 'xor', 'id', 'print', ')', None):
				return a
			raise ParseError("{} wasn't an 'or' ,'xor', 'id', 'print', ')' or 'None' token!".format(self.la))
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'b_num' token!".format(self.la))

	def atom(self):
		if self.la == '(':
			self.match('(')
			e = self.expr()
			self.match(')')
			return e
		elif self.la == 'id':
			varname = self.text
			self.match('id')
			if varname in self.st:
				return self.st[varname]
			raise ParseError("{} was not in in self.ST expected!".format(varname))
		elif self.la == 'BIT_TOKEN':
			binary_value = int(self.text, 2)
			self.match('BIT_TOKEN')
			return binary_value
		else:
			raise ParseError("{} wasn't an '(', 'id' or 'BIT_TOKEN' token!".format(self.la))

parser = MyParser()
with open("test.txt") as fp:
	parser.parse(fp)