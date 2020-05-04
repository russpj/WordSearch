﻿# Tests.py

# A test driver for WordSearch, using only console output

from copy import deepcopy
from WordSearch import WordSearchSolver
from WordSearch import Match

letters = [
		['a','d','r','e'],
		['e','i','e','s'],
		['n','r','t','h'],
		['s','g','u','o']
	]

testLetters = [
		['s','c','e','s'],
		['y','i','a','h'],
		['c','m','n','e'],
		['s','a','d','s']
	]

foxLetters = [
		['o','x','o','x'],
		['x','o','x','o'],
		['o','x','o','x'],
		['x','o','x','o']
	]


def PrintGrid(letters):
	for row in letters:
		print(row)

def ShowSearchResult(solver, word):
	print('Looking up {word}: {result}'.format(result=solver.FindWord(word), word=word))

def RunTest(letters, expected=0, sort=False, useFastAlgorithm=True):
	print()
	print('Running test for')
	PrintGrid(letters)
	solver = WordSearchSolver('studentdictionary.txt', letters, useFastAlgorithm=useFastAlgorithm)
	foundWords = []
	for foundWord in solver.FindAllWords():
		word = foundWord.word
		if not useFastAlgorithm:
			# print ('{word} {match}'.format(word=word, match=foundWord.match))
			if foundWord.match==Match.ExactMatch:
				print(word)
		if foundWord.match==Match.ExactMatch and  word not in foundWords:
			foundWords.append(word)
			if not sort and useFastAlgorithm:
				print(word)

	if sort and useFastAlgorithm:
		foundWords.sort()
		for word in foundWords:
			print(word)
	
	print ('Found {found} words, expected {expected}.'.format(found=len(foundWords), expected=expected))

def RunFoxesTest():
	for row in range(4):
		for col in range(4):
			letters = deepcopy(foxLetters)
			letters[row][col] = 'f'
			RunTest(letters, 2)

def Main():
	print('Running tests')
	testSolver = WordSearchSolver('studentdictionary.txt', foxLetters)
	print('First word is {word}.'.format(word=testSolver.dictionary[0]))
	ShowSearchResult(testSolver, 'pet')
	ShowSearchResult(testSolver, 'pre')
	ShowSearchResult(testSolver, 'a')
	ShowSearchResult(testSolver, 'zzzzzz')
	ShowSearchResult(testSolver, '')
	print()

	RunTest(letters)
	RunTest(testLetters, 265, True)
	RunFoxesTest()

	RunTest(testLetters, useFastAlgorithm=False)


if __name__ == '__main__':
	Main()


