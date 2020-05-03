# WordSearch.py

# Implements Boggle style word search on a grid of letters

from enum import Enum
from bisect import bisect_left


class Match(Enum):
	ExactMatch = 1
	PrefixMatch = 2
	NoMatch = 9


class FoundWord:
	def __init__(self, word='', match=Match.NoMatch, path=[], **kwargs):
		self.word = word
		self.match = match
		self.path = path
		return


class WordSearchSolver:
	def __init__(self, dictionaryName='', letters=[], minSize=3, **kwargs):
		if dictionaryName:
			self.InitDictionary(dictionaryName)
		self.letters=letters
		self.numRows = len(letters)
		if self.numRows > 0:
			self.numCols = len(letters[0])
		else:
			self.numCols = 0
		self.path = []
		self.minSize = minSize

	def InitDictionary(self, name):
		with open(name) as dictionaryFile:
			self.dictionary = dictionaryFile.read().splitlines()

	def FindWord(self, word):
		index = bisect_left(self.dictionary, word)
		if index == len(self.dictionary):
			match = Match.NoMatch
			matchedWord = ''
		else:
			matchedWord = self.dictionary[index]
			if word == matchedWord:
				match = Match.ExactMatch
			elif word == matchedWord[:len(word)]:
				match = Match.PrefixMatch
			else:
				match = Match.NoMatch
		return match, matchedWord

	def WordFromPath(self):
		word = ''
		for cell in self.path:
			word+=(self.letters[cell[0]][cell[1]])
		return word

	def InRange(self, cell):
		row = cell[0]
		col = cell[1]
		return (row >= 0 and row < self.numRows and col >=0 and col < self.numCols)

	def Cells(self, cell):
		row = cell[0]
		col = cell[1]
		for drow in range(-1, 2):
			for dcol in range(-1, 2):
				yield [row+drow, col+dcol]

	def FindWords(self, cell):
		if not self.InRange(cell):
			return
		if cell in self.path:
			return
		self.path.append(cell)
		word = self.WordFromPath()
		match, matchWord = self.FindWord(word)

		if match != Match.NoMatch:
			if match == Match.ExactMatch and len(word) >= self.minSize:
				yield FoundWord(word=word, match=match, path=self.path)

			for cell in self.Cells(cell):
				yield from self.FindWords(cell)
		
		self.path.pop()
		return

	def FindAllWords(self):
		for row in range(len(self.letters)):
			for col in range(len(self.letters[row])):
				yield from self.FindWords([row, col])
