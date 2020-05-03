from enum import Enum
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from WordSearch import WordSearchSolver
from WordSearch import Match


testLetters = [
		['s','c','e','s'],
		['y','i','a','h'],
		['c','m','n','e'],
		['s','a','d','s']
	]

class AppState(Enum):
	Ready = 1
	Running = 2
	Paused = 3
	Finished = 5

nextState={
	AppState.Ready: AppState.Running,
	AppState.Running: AppState.Paused,
	AppState.Paused: AppState.Running,
	AppState.Finished: AppState.Ready
	}


class Speed(Enum):
	Slow=1
	Medium=2
	Fast=3

nextSpeed={
	Speed.Slow: Speed.Medium,
	Speed.Medium: Speed.Fast,
	Speed.Fast: Speed.Slow
	}

class SpeedInfo:
	def __init__(self, statusText='', fps=0):
		self.statusText=statusText
		self.fps=fps

infoFromSpeed = {
	Speed.Slow: SpeedInfo(statusText='Slow', fps=1),
	Speed.Medium: SpeedInfo(statusText='Medium', fps=10),
	Speed.Fast: SpeedInfo(statusText='High', fps=100)
	}

class ButtonInfo:
	def __init__(self, enabled=True, text=''):
		self.enabled = enabled
		self.text=text

class AppInfo:
	def __init__(self, statusText='', 
							startInfo=ButtonInfo(),
							speedInfo=ButtonInfo()):
		self.statusText=statusText
		self.startInfo=startInfo
		self.speedInfo=speedInfo

infoFromState = {
	AppState.Ready: AppInfo(statusText='Ready', 
												 startInfo=ButtonInfo(text='Start', enabled=True),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=True)),
	AppState.Running: AppInfo(statusText='Running', 
												 startInfo=ButtonInfo(text='Pause', enabled=True),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=False)),
	AppState.Paused: AppInfo(statusText='Paused', 
												 startInfo=ButtonInfo(text='Resume', enabled=True),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=True)),
	AppState.Finished: AppInfo(statusText='Done', 
												 startInfo=ButtonInfo(text='Reset', enabled=True),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=False))
	}


# BoardLayout encapsulates the playing board

class WordGrid(GridLayout):
	def __init__(self, letters=[], **kwargs):
		super().__init__(cols=4, **kwargs)
		self.PlaceStuff(letters)
		return

	def PlaceStuff(self, letters):
		self.letterLabels=[]
		for row in range(4):
			colLabels=[]
			for col in range(4):
				label = Label(text=letters[row][col], font_size=40)
				self.add_widget(label)
				colLabels.append(label)
			self.letterLabels.append(colLabels)
		return

	def ShowPath(self, match, path):
		exactMatchColor = [0.0, 1.0, 0.0, 1.0]
		prefixMatchColor = [1.0, 1.0, 0.0, 1.0]
		if match == Match.ExactMatch:
			matchColor = exactMatchColor
		else:
			matchColor = prefixMatchColor
		defaultColor = [1.0, 1.0, 1.0, 1.0]
		# restore letters to default
		for row in range(len(self.letterLabels)):
			for col in range(len(self.letterLabels[row])):
				self.letterLabels[row][col].color=defaultColor
		# draw path
		matchColor[3] = 0.1
		alphaStep = 0.9/(len(path))
		for cell in path:
			matchColor[3] += alphaStep
			self.letterLabels[cell[0]][cell[1]].color=matchColor.copy()

class BoardLayout(BoxLayout):
	def __init__(self, letters=[], **kwargs):
		super().__init__(orientation='horizontal', padding=10, **kwargs)
		self.wordList = []
		self.wordCount = 0
		self.PlaceStuff(letters)
		self.bind(pos=self.update_rect, size=self.update_rect)
		return

	def PlaceStuff(self, letters):
		with self.canvas.before:
			Color(0.2, .2, 0.2, 1)  # grey; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)

		with self.canvas:
			self.words = BoxLayout(size_hint=[.25,1])
			self.wordLabel = Label(size_hint=[1, 1], font_size=25)
			self.add_widget(self.words)
			self.words.add_widget(self.wordLabel)
			
			self.countLabel = Label(size_hint=[.25, 1], font_size=30)
			self.add_widget(self.countLabel)

			self.wordGrid = WordGrid(letters=letters, size_hint=[.5, 1])
			self.add_widget(self.wordGrid)

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size
		print('view pos {pos}, size {size}'.format(pos=self.words.pos, size=self.words.size))
		instance.wordLabel.text_size = self.words.size
		print('wordLabel pos {pos}, size {size}'.format(pos=instance.wordLabel.pos, size=instance.wordLabel.size))

	def UpdateWords(self):
		words = self.wordList
		text = ''
		for word in words:
			if text:
				text += '\n'
			text += word
		self.wordLabel.text = text
		self.wordLabel.texture_update()
		self.wordLabel.text_size = self.wordLabel.size
		print('Layout pos {pos}, size {size}'.format(pos=self.pos, size=self.size))
		print('view pos {pos}, size {size}'.format(pos=self.words.pos, size=self.words.size))
		print('wordLabel pos {pos}, size {size}'.format(pos=self.wordLabel.pos, size=self.wordLabel.size))
		self.countLabel.text = 'Words found:\n{count}'.format(count=self.wordCount)
		self.wordGrid.ShowPath(self.match, self.path)

	def ResetWords(self):
		self.wordList = []
		self.wordCount = 0
		self.UpdateWords()

	def UpdateWord(self, word, match, path):
		if match==Match.ExactMatch and word not in self.wordList:
			self.wordList.append(word)
			self.wordCount += 1
		self.match = match
		self.path = path
		self.UpdateWords()

class HeaderLayout(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(orientation='horizontal', **kwargs)
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.6, .6, 0.1, 1)  # yellow; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		textColor = [0.7,0.05, 0.7, 1]
		self.speedLabel = Label(text='Animation speed: ', color=textColor)
		self.add_widget(self.speedLabel)
		self.statusLabel = Label(text='Ready', color = textColor)
		self.add_widget(self.statusLabel)
		self.fpsLabel = Label(text='0 fps', color=textColor)
		self.add_widget(self.fpsLabel)
		
	def UpdateText(self, fps=0, statusText='Ready', speedText=''):
		self.speedLabel.text='Speed: {speed}'.format(speed=speedText)
		self.fpsLabel.text = '{fpsValue:.0f} fps'.format(fpsValue=fps)
		self.statusLabel.text = statusText

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size


class FooterLayout(BoxLayout):
	def __init__(self, 
							start_button_callback=None, 
							speed_button_callback=None, 
							**kwargs):
		super().__init__(orientation='horizontal', padding=10, **kwargs)
		self.start_button_callback=start_button_callback
		self.speed_button_callback=speed_button_callback
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.4, .1, 0.4, 1)  # purple; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		
		self.speedButton = Button()
		self.add_widget(self.speedButton)
		self.speedButton.bind(on_press=self.speed_button_callback)
		self.startButton = Button()
		self.add_widget(self.startButton)
		self.startButton.bind(on_press=self.start_button_callback)
		self.UpdateButtons()

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size

	def UpdateButtons(self, appInfo=infoFromState[AppState.Ready]):
		startInfo = appInfo.startInfo
		self.startButton.text = startInfo.text
		self.startButton.disabled = not startInfo.enabled
		speedInfo = appInfo.speedInfo
		self.speedButton.text=speedInfo.text
		self.speedButton.disabled = not speedInfo.enabled


class Rotator(App):
	def build(self):
		self.root = layout = BoxLayout(orientation = 'vertical')
		self.state = AppState.Ready
		self.clock=None
		self.solver = WordSearchSolver('studentdictionary.txt', testLetters)
		self.generator=None
		self.speed = Speed.Slow
		self.words = []
		self.count = 1

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout(testLetters)
		layout.add_widget(boardLayout)

		# footer
		self.footer = FooterLayout(size_hint=(1, .2), 
														 start_button_callback=self.StartButtonCallback,
														 speed_button_callback=self.SpeedButtonCallback)
		layout.add_widget(self.footer)

		self.UpdateUX()
		return layout

	def FrameN(self, dt):
		if self.generator is None:
			return
		if dt != 0:
			fpsValue = 1/dt
		else:
			fpsValue = 0
		if (self.state==AppState.Finished or self.state==AppState.Ready):
			return

		try:
			if self.generator is not None:
				result = next(self.generator)
			self.boardLayout.UpdateWord(result.word, result.match, result.path)
			self.UpdateUX(fps=fpsValue)
		except StopIteration:
			self.state=AppState.Finished
			self.clock.cancel()
			self.generator=None
			self.UpdateUX(fps=fpsValue)

	def UpdateUX(self, fps=0):
		state = self.state
		speed = self.speed
		appInfo = infoFromState[self.state]
		self.header.UpdateText(fps = fps, 
												 statusText=appInfo.statusText, 
												 speedText=infoFromSpeed[speed].statusText)
		self.footer.UpdateButtons(appInfo=appInfo)

	def StartClock(self):
			self.clock = Clock.schedule_interval(self.FrameN, 
																				1.0/infoFromSpeed[self.speed].fps)

	def StartButtonCallback(self, instance):
		if self.state==AppState.Ready:
			self.generator = self.solver.FindAllWords()
			self.StartClock()
		if self.state==AppState.Running:
			self.clock.cancel()
		if self.state==AppState.Paused:
			self.StartClock()
		if self.state==AppState.Finished:
			self.boardLayout.ResetWords()
		self.state = nextState[self.state]
		self.UpdateUX()

	def SpeedButtonCallback(self, instance):
		self.speed = nextSpeed[self.speed]
		self.UpdateUX()


def Main():
	Rotator().run()

if __name__ == '__main__':
	Main()


