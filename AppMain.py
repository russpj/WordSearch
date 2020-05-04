from enum import Enum
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from WordSearch import WordSearchSolver
from WordSearch import Match

def InterpolateValues(valueMin, valueMax, ratio):
	return valueMin*(1-ratio) + valueMax*ratio

def InterpolateColors(colorMin, colorMax, ratio):
	color = []
	for index in range(len(colorMin)):
		color.append(InterpolateValues(colorMin[index], colorMax[index], ratio))
	return color

testLetters = [
		['s','c','e','n'],
		['y','c','i','e'],
		['a','m','n','s'],
		['s','a','d','e']
	]

computerLetters = [
	['c', 'o', 'm', 'p'],
	['e', 't', 'u', 'b'],
	['r', 'd', 'a', 'l'],
	['s', 'a', 't', 'e']
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
	Ludicrous=4

nextSpeed={
	Speed.Slow: Speed.Medium,
	Speed.Medium: Speed.Fast,
	Speed.Fast: Speed.Ludicrous,
	Speed.Ludicrous: Speed.Slow
	}

class SpeedInfo:
	def __init__(self, statusText='', fps=0):
		self.statusText=statusText
		self.fps=fps

infoFromSpeed = {
	Speed.Slow: SpeedInfo(statusText='Slow', fps=1),
	Speed.Medium: SpeedInfo(statusText='Medium', fps=10),
	Speed.Fast: SpeedInfo(statusText='High', fps=100),
	Speed.Ludicrous: SpeedInfo(statusText='Ludicrous', fps=100)
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

class RoundedRectLabel(Label):
	def __init__(self, text_color=[0.0, 0.0, 0.0, 1.0], back_color=[1.0, 1.0, 1.0, 1.0], **kwargs):
		super().__init__(color=text_color, **kwargs)
		self.back_color = back_color
		self.CreateBackground(back_color, force=True)
		self.bind(pos=self.update_rect, size=self.update_rect)
		return

	def CreateBackground(self, color=[1,1,1,1], force=False):
		if force or self.back_color != color:
			self.back_color = color
			self.canvas.before.clear()
			with self.canvas.before:
				Color(color[0], color[1], color[2], color[3])
				self.background = RoundedRectangle(size=self.size, pos=self.pos)

	def update_rect(self, instance, value):
		self.background.pos = instance.pos
		self.background.size = instance.size
		self.font_size = instance.size[1]/2
		return

	def SetColors(self, text_color=[0.0, 0.0, 0.0, 1.0],
							 back_color=[1.0, 1.0, 1.0, 1.0]):
		self.color = text_color
		self.CreateBackground(back_color)


class WordGrid(GridLayout):
	def __init__(self, letters=[], **kwargs):
		super().__init__(cols=4, spacing=[3,3],
									padding=[0,0], **kwargs)
		self.PlaceStuff(letters)
		self.bind(pos=self.update_rect, size=self.update_rect)
		return

	def update_rect(self, instance, value):
		if instance.size[0] < instance.size[1]:
			instance.padding = [0, (instance.size[1]-instance.size[0])/2]
		else:
			instance.padding = [(instance.size[0]-instance.size[1])/2, 0]

	def PlaceStuff(self, letters):
		self.letterLabels=[]
		for row in range(4):
			colLabels=[]
			for col in range(4):
				label = RoundedRectLabel(text=letters[row][col], font_size=40, 
														 text_color=[0,0,0,1], back_color=[1,1,1,1])
				self.add_widget(label)
				colLabels.append(label)
			self.letterLabels.append(colLabels)
		return

	def ShowPath(self, match, path):
		exactMatchColorMax = [0.0, 0.5, 0.0, 1.0]
		exactMatchColorMin = [0.0, 1.0, 0.0, 1.0]
		prefixMatchColorMax = [0.5, 0.5, 0.0, 1.0]
		prefixMatchColorMin = [1.0, 1.0, 0.0, 1.0]
		defaultColor = [0.0, 0.0, 0.0, 1.0]
		# restore letters to default
		for row in range(len(self.letterLabels)):
			for col in range(len(self.letterLabels[row])):
				self.letterLabels[row][col].SetColors(text_color=defaultColor, back_color=[1,1,1,1])
		# draw path
		if path:
			ratio = 0.0
			ratioStep = 1.0/len(path)
			if match == Match.ExactMatch:
				matchColorMin = exactMatchColorMin
				matchColorMax = exactMatchColorMax
			else:
				matchColorMin = prefixMatchColorMin
				matchColorMax = prefixMatchColorMax
			for cell in path:
				matchColor = InterpolateColors(matchColorMin, matchColorMax, ratio)
				self.letterLabels[cell[0]][cell[1]].SetColors(back_color=matchColor.copy(), text_color=[0,0,0,1])
				ratio += ratioStep

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
		instance.wordLabel.text_size = self.words.size
		instance.wordLabel.font_size = self.size[1]/25
		instance.countLabel.text_size = self.countLabel.size
		instance.countLabel.font_size = self.size[1]/15

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
		self.countLabel.text_size = self.countLabel.size
		self.countLabel.text = 'Words found: {count}'.format(count=self.wordCount)
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
		self.letters = computerLetters
		self.solver = WordSearchSolver('studentdictionary.txt', self.letters, useFastAlgorithm=False)
		self.generator=None
		self.speed = Speed.Slow
		self.words = []
		self.count = 1

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout(self.letters)
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
				while True:
					result = next(self.generator)
					if self.speed != Speed.Ludicrous or result.match == Match.ExactMatch:
						break

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


