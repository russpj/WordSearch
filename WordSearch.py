# WordSearch.py

# Implements Boggle style word search on a grid of letters

from enum import Enum
from bisect import bisect_left

class WordSearchSolver:
	def __init__(self, dictionaryName='', **kwargs):
		if dictionaryName:
			self.InitDictionary(dictionaryName)

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