from enum import Enum
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

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


class Algorithm(Enum):
	Reverse = 1
	ReverseRotation=2

nextAlgorithm={
	Algorithm.Reverse: Algorithm.ReverseRotation,
	Algorithm.ReverseRotation:Algorithm.Reverse
	}

class AlgorithmInfo:
	def __init__(self, buttonText='', algorithm=None):
		self.buttonText = buttonText
		self.algorithm = algorithm

infoFromAlgorithm = {
	Algorithm.Reverse: AlgorithmInfo('Reverse', ReverseAll),
	Algorithm.ReverseRotation: AlgorithmInfo('Rotation by Reverse', ReverseRotation)
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
							algorithmInfo=ButtonInfo(),
							speedInfo=ButtonInfo()):
		self.statusText=statusText
		self.startInfo=startInfo
		self.algorithmInfo=algorithmInfo
		self.speedInfo=speedInfo

infoFromState = {
	AppState.Ready: AppInfo(statusText='Ready with {algorithm}', 
												 startInfo=ButtonInfo(text='Start', enabled=True),
												 algorithmInfo=ButtonInfo(text='Change Algorithm', enabled=True),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=True)),
	AppState.Running: AppInfo(statusText='Running {algorithm}', 
												 startInfo=ButtonInfo(text='Pause', enabled=True),
												 algorithmInfo=ButtonInfo(text='Change Algorithm', enabled=False),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=False)),
	AppState.Paused: AppInfo(statusText='Paused {algorithm}', 
												 startInfo=ButtonInfo(text='Resume', enabled=True),
												 algorithmInfo=ButtonInfo(text='Change Algorithm', enabled=False),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=True)),
	AppState.Finished: AppInfo(statusText='Done with {algorithm}', 
												 startInfo=ButtonInfo(text='Reset', enabled=True),
												 algorithmInfo=ButtonInfo(text='Change Algorithm', enabled=False),
												 speedInfo=ButtonInfo(text='Change Speed', enabled=False))
	}


# BoardLayout encapsulates the playing board
class BoardLayout(BoxLayout):
	def __init__(self, numCells):
		super().__init__()
		self.numCells = numCells
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def InterpolateColor(self, beginColor, endColor, ratio):
		betweenColor = []
		for colorIndex in range(len(beginColor)):
			betweenColor.append(beginColor[colorIndex]*ratio + endColor[colorIndex]*(1-ratio))
		return betweenColor

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.1, .3, 0.1, 1)  # green; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		
		self.rectangles = []
		self.colorValues = []
		self.colors = []
		pos = [0,0]
		posNext = [self.rect.size[0]/self.numCells, 0]
		beginColor = [0.0, .75, .25, 1]
		endColor = [0.0, .25, .75, 1]
		with self.canvas:
			for cell in range(self.numCells):
				betweenColor = self.InterpolateColor(beginColor, endColor, float(cell)/self.numCells)
				self.colorValues.append(betweenColor)
				color = Color(betweenColor[0], betweenColor[1], betweenColor[2], betweenColor[3])
				self.colors.append(color)
				size = [posNext[0]-pos[0], self.rect.size[1]]
				rect= Rectangle(size=size, pos=pos)
				self.rectangles.append(rect)
				pos = posNext.copy()
				posNext = [self.rect.size[0]*cell/self.numCells, 0]
			
	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size

		numCells = len(instance.rectangles)
		for cell in range(numCells):
			rect = instance.rectangles[cell]
			pos = [instance.pos[0]+instance.size[0]*cell/numCells, instance.pos[1]]
			size = [instance.pos[0]+instance.size[0]*(cell+1)/numCells-pos[0], instance.size[1]]
			rect.pos = pos
			rect.size = size

	def ApplyColor(self, color, colorList):
		color.r = colorList[0]
		color.g = colorList[1]
		color.b = colorList[2]
		color.a = colorList[3]

	def UpdateColors(self, colorIndices=None):
		if colorIndices is not None:
			for index in range(len(colorIndices)):
				if index < len(self.colors):
					self.ApplyColor(self.colors[index], self.colorValues[colorIndices[index]])


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
		
	def UpdateText(self, fps=0, statusText='Ready', algorithm='', speedText=''):
		self.speedLabel.text='Animation speed: {speed}'.format(speed=speedText)
		self.fpsLabel.text = '{fpsValue:.0f} fps'.format(fpsValue=fps)
		self.statusLabel.text = statusText.format(algorithm=algorithm)

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size


class FooterLayout(BoxLayout):
	def __init__(self, 
							start_button_callback=None, 
							speed_button_callback=None, 
							algorithm_button_callback=None, 
							**kwargs):
		super().__init__(orientation='horizontal', padding=10, **kwargs)
		self.start_button_callback=start_button_callback
		self.speed_button_callback=speed_button_callback
		self.algorithm_button_callback=algorithm_button_callback
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.4, .1, 0.4, 1)  # purple; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		
		self.speedButton = Button()
		self.add_widget(self.speedButton)
		self.speedButton.bind(on_press=self.speed_button_callback)
		self.algorithmButton = Button()
		self.add_widget(self.algorithmButton)
		self.algorithmButton.bind(on_press=self.algorithm_button_callback)
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
		algorithmInfo = appInfo.algorithmInfo
		self.algorithmButton.text = algorithmInfo.text
		self.algorithmButton.disabled = not algorithmInfo.enabled


class Rotator(App):
	def build(self):
		self.root = layout = BoxLayout(orientation = 'vertical')
		self.state = AppState.Ready
		self.algorithm = Algorithm.Reverse
		self.clock=None
		self.generator=None
		self.simulationLength = 500
		self.rotationShift = 150
		self.array = list(range(self.simulationLength))
		self.speed = Speed.Slow

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout(len(self.array))
		layout.add_widget(boardLayout)

		# footer
		self.footer = FooterLayout(size_hint=(1, .2), 
														 start_button_callback=self.StartButtonCallback,
														 algorithm_button_callback=self.AlgorithmButtonCallback,
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
			result = next(self.generator)
			self.boardLayout.UpdateColors(self.array)
			self.UpdateUX(fps=fpsValue)
		except StopIteration:
			self.state=AppState.Finished
			self.clock.cancel()
			self.generator=None
			self.UpdateUX(fps=fpsValue)

	def UpdateUX(self, fps=0):
		state = self.state
		speed = self.speed
		algorithm = self.algorithm
		appInfo = infoFromState[self.state]
		self.header.UpdateText(fps = fps, 
												 statusText=appInfo.statusText, 
												 algorithm=infoFromAlgorithm[algorithm].buttonText,
												 speedText=infoFromSpeed[speed].statusText)
		self.footer.UpdateButtons(appInfo=appInfo)

	def StartClock(self):
			self.clock = Clock.schedule_interval(self.FrameN, 
																				1.0/infoFromSpeed[self.speed].fps)

	def StartButtonCallback(self, instance):
		if self.state==AppState.Ready:
			self.array = list(range(self.simulationLength))
			algorithm = infoFromAlgorithm[self.algorithm].algorithm
			self.generator=algorithm(self.array, self.rotationShift)
			self.StartClock()
		if self.state==AppState.Running:
			self.clock.cancel()
		if self.state==AppState.Paused:
			self.StartClock()
		if self.state==AppState.Finished:
			self.array = list(range(self.simulationLength))
			self.boardLayout.UpdateColors(self.array)
		self.state = nextState[self.state]
		self.UpdateUX()

	def AlgorithmButtonCallback(self, instance):
		self.algorithm = nextAlgorithm[self.algorithm]
		self.UpdateUX()

	def SpeedButtonCallback(self, instance):
		self.speed = nextSpeed[self.speed]
		self.UpdateUX()


def Main():
	Rotator().run()

if __name__ == '__main__':
	Main()


