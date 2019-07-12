import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.videoplayer import VideoPlayer

import NLP_module
import Static_Scene
import ModelGeneration_module
import animation_generator

class MyGrid(GridLayout):
    vedio_name=' '
    def __init__(self, **kwargs):
        self.vedio_name
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 3

        self.title= Label(text="what do you think ... ? ")
        self.inside.add_widget(self.title)
        
        self.inside.inside= GridLayout()
        self.inside.inside.rows=2
        self.description = TextInput(multiline= True)
        self.inside.inside.add_widget(self.description)

        self.inside.inside.inside= GridLayout()
        self.inside.inside.inside.cols=2
        # size_hint_max_y= 0.5
        self.visualize = Button(text= "Animate",font_size = 15)
        self.visualize.bind(on_press=self.play)
        self.inside.inside.inside.add_widget(self.visualize)
        
        self.clear = Button(text= "clear",font_size = 15)
        self.clear.bind(on_press=self.pressed)
        self.inside.inside.inside.add_widget(self.clear)

        self.inside.inside.add_widget(self.inside.inside.inside)
        self.inside.add_widget(self.inside.inside)
        self.add_widget(self.inside)

        self.player  = VideoPlayer(source= self.vedio_name,  state='stop', options={'allow_stretch': True})
        self.add_widget(self.player)

    def pressed(self, instance):
        name = self.description.text
        print("scene:", name)
        self.description.text = ""
        self.title.text = "what do you think ... ?"


    def play(self, instance):
        input_text=self.description.text
        self.logic(input_text)

    
    def logic(self,input_text):
        global vedio_name
        self.title.text= "Analysing Story ..."
        NLP_module.nlp_module(input_text)
        

        self.title.text= "Models Generation ..."
        ModelGeneration_module.model_generation()

        self.title.text= "Static Scene Visualization ..."
        loop= True
        count =0
        while(loop and count<= 50):
            count += 1
            try: 
                Static_Scene.static_positioning()
                loop =False
            except :
                print('try again')
                loop= True
        if (loop):
             print("Sorry can't handle the scene")
             self.title.text = "Sorry can't handle the scene"
        elif(not loop): 
            self.vedio_name=animation_generator.animate()
            print('rendering is done and video is',  self.vedio_name)
            self.player.state='play'
        

        return

class MyApp(App):
    def build(self):
        self.title = 'Animare'
        self.icon = 'Animare_logo.png'
        return MyGrid()


if __name__ == "__main__":
    MyApp().run()