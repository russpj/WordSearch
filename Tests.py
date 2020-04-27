# Tests.py

# A test driver for WordSearch, using only console output

from WordSearch import WordSearchSolver

def ShowSearchResult(solver, word):
	print('Looking up {word}: {result}'.format(result=solver.FindWord(word), word=word))


def Main():
	print('Running tests')
	testSolver = WordSearchSolver('studentdictionary.txt')
	print('First word is {word}.'.format(word=testSolver.dictionary[0]))
	ShowSearchResult(testSolver, 'pet')
	ShowSearchResult(testSolver, 'pre')
	ShowSearchResult(testSolver, 'a')
	ShowSearchResult(testSolver, 'zzzzzz')
	ShowSearchResult(testSolver, '')

if __name__ == '__main__':
	Main()


