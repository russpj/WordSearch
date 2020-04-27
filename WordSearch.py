# WordSearch.py

# Implements Boggle style word search on a grid of letters

from enum import Enum
from bisect import bisect_left

class WordSearchSolver:
	def __init__(self, dictionaryName='', letters=[], **kwargs):
		if dictionaryName:
			self.InitDictionary(dictionaryName)
		self.letters=letters
		self.numRows = len(letters)
		if self.numRows > 0:
			self.numCols = len(letters[0])
		else:
			self.numCols = 0
		self.path = []

	def InitDictionary(self, name):
		with open(name) as dictionaryFile:
			self.dictionary = dictionaryFile.read().splitlines()

	class Match(Enum):
		ExactMatch = 1
		PrefixMatch = 2
		NoMatch = 9

	def FindWord(self, word):
		index = bisect_left(self.dictionary, word)
		if index == len(self.dictionary):
			match = self.Match.NoMatch
			matchedWord = ''
		else:
			matchedWord = self.dictionary[index]
			if word == matchedWord:
				match = self.Match.ExactMatch
			elif word == matchedWord[:len(word)]:
				match = self.Match.PrefixMatch
			else:
				match = self.Match.NoMatch
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
		if match == self.Match.NoMatch:
			self.path.pop()
			return
		
		if match == self.Match.ExactMatch:
			yield word

		for cell in self.Cells(cell):
			yield from self.FindWords(cell)
		self.path.pop()
		return

	def FindAllWords(self):
		for row in range(len(self.letters)):
			for col in range(len(self.letters[row])):
				yield from self.FindWords([row, col])
