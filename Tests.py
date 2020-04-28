﻿# Tests.py

# A test driver for WordSearch, using only console output

from WordSearch import WordSearchSolver

letters = [
		['a','d','r','e'],
		['e','i','e','s'],
		['n','r','t','h'],
		['s','g','u','o']
	]

lettersTest = [
		['s','c','e','s'],
		['y','i','a','h'],
		['c','m','n','e'],
		['s','a','d','s']
	]


def PrintGrid(letters):
	for row in letters:
		print(row)

def ShowSearchResult(solver, word):
	print('Looking up {word}: {result}'.format(result=solver.FindWord(word), word=word))


def Main():
	print('Running tests')
	testSolver = WordSearchSolver('studentdictionary.txt', letters,9)
	print('First word is {word}.'.format(word=testSolver.dictionary[0]))
	ShowSearchResult(testSolver, 'pet')
	ShowSearchResult(testSolver, 'pre')
	ShowSearchResult(testSolver, 'a')
	ShowSearchResult(testSolver, 'zzzzzz')
	ShowSearchResult(testSolver, '')
	print()
	PrintGrid(letters)

	print('Looking for words')
	foundWords = []
	for word in testSolver.FindAllWords():
		if word not in foundWords:
			print (word)
			foundWords.append(word)
	print('Found {number} words.'.format(number=len(foundWords)))

	testSolver = WordSearchSolver('studentdictionary.txt', lettersTest, 3)
	foundWords = []
	for word in testSolver.FindAllWords():
		if word not in foundWords:
			foundWords.append(word)
	foundWords.sort()
	for word in foundWords:
		print (word)
	print ('Found {found} words, expected 265.'.format(found=len(foundWords)))

if __name__ == '__main__':
	Main()


