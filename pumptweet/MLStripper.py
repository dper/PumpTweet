# coding=utf-8

from html.parser import HTMLParser

# Class for stripping HTML from text.
class MLStripper(HTMLParser):

	def __init__(self):
		super().__init__()
		self.reset()
		self.fed = []

	def handle_data(self, d):
		self.fed.append(d)

	def get_data(self):
		return ''.join(self.fed)

# Replaces HTML entities with actual characters.
def replace_entities(html):
	unifiable = [
		('&amp;', '&'), 
		('&nbsp;', ' '),
		('&#39;', "'"),
		('&quot;', "'"),
		('&ndash;', '-'),
		('&mdash;', u'–'),
		('&rarr;', u'→'),
		('&larr;', u'←'),
		('&lrarr;', u'↔'),
		('&ldquo;', '"'),
		('&rdquo;', '"'),
	]

	for (entity, char) in unifiable:
		html = html.replace(entity, char)

	return html

# Strips tags from HTML, returning regular text.
def strip_tags(html):
	html = replace_entities(html)

	# Converts HTML characters back to unicode.
	# This keeps them from being stripped later.
	parser = HTMLParser()
	html = parser.unescape(html)

	s = MLStripper()
	s.feed(html)
	return s.get_data()
	#return s.read(html)
