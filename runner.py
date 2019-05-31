
import plex


# ... συμπληρώστε τον κώδικά σας για τον συντακτικό αναλυτή - διερμηνευτή της γλώσσας ...

class ParseError(Exception):
	pass

class ParseRun(Exception):
	pass

class MyParser:
	def __init__(self):
		space = plex.Any(" \n\t")
		parenthesis = plex.Str('(', ')')
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		id_token = letter + plex.Rep(letter|digit)
		bit = plex.Range('01')
		bits = plex.Rep1(bit)
		print_token = plex.Str('print', 'PRINT')
		space = plex.Any(" \n\t")
		operators = plex.Str('=', 'xor', 'and', 'or')
		self.st = {}
		self.LEXICON = plex.Lexicon([
			(space, plex.IGNORE),
			(operators, plex.TEXT),
			(bits, 'BIT_TOKEN'),
			(parenthesis, plex.TEXT),
			(print_token, 'PRINT'),
			(id_token, 'IDENTIFIER')
			])

	def create_scanner(self,fp):
		self.scanner = plex.Scanner(self.LEXICON,fp)
		self.la,self.text=self.next_token()

	def next_token(self):
		return self.scanner.read()

	def match(self,token):
		if self.la==token:
			self.la,self.text=self.next_token()
		else:
			raise ParseError("perimenw )")

	def parse(self,fp):
		self.create_scanner(fp)
		self.stmt_list()
		
	def stmt_list(self):
		if self.la == 'IDENTIFIER' or self.la == 'PRINT':
			self.stmt()
			self.stmt_list()
		elif self.la==None:
			return
		else:
			raise ParseError("perimenw IDENTIFIER or Print")
	def stmt(self):
		if self.la == 'IDENTIFIER':
			varname = self.text
			self.match('IDENTIFIER')	
			self.match('=')
			e = self.expr()
			self.st[varname] = e
		elif self.la == 'PRINT':
			self.match('PRINT')
			e = self.expr()
			print('{:b}'.format(e))
		else:
			raise ParseError("perimenw IDENTIFIER or PRINT")
	def expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			t = self.term()
			while self.la == 'xor':
				self.match('xor')
				t2 = self.term()
				t ^= t2
			if self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
					return t
			else:
					raise ParseError("perimenw ^")
		else:
			raise ParseError("perimenw ( or IDENTIFIER or BIT_TOKEN or )")
	def term(self):
		if self.la=='(' or self.la=='IDENTIFIER' or self.la == 'BIT_TOKEN':	
			t=self.factor()
			while self.la == 'or':
				self.match('or')
				t2 = self.factor()
				t |= t2
			if self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la==')':
				return t
			else:
				print(self.la)
				raise ParseError("perimenw ( or IDENTIFIER or BIT_TOKEN or )")
		else:
			raise ParseError("perimenw * or /")
	def factor(self):
		if self.la=='(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			t=self.atom()
			while self.la == 'and':
				self.match('and')
				t2 = self.atom()
				t &= t2
			if self.la == 'xor' or self.la == 'or' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la==')':
				return t
			else:
				print(self.la)
				raise ParseError("perimenw ( or IDENTIFIER or BIT_TOKEN or )")
		else:
			raise ParseError("perimenw id,bit h (")
	def atom(self):
		if self.la=='(':
			self.match('(')
			e=self.expr()
			self.match(')')
			return e
		elif self.la=='IDENTIFIER':
			varname = self.text
			self.match('IDENTIFIER')
			if varname in self.st:
				return self.st[varname]
		elif self.la=='BIT_TOKEN':
			value=int(self.text,2)
			self.match('BIT_TOKEN')
			return value
		else:
			raise ParseError("perimenw id bit or (")
parser = MyParser()
with open('test.txt','r') as fp:
	parser.parse(fp)
