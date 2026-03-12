from kivy.app import App
from kivy.uix.label import Label

class MyApp(App):
    def build(self):
        return Label(text="打包成功！", font_size=50)

if __name__ == "__main__":
    MyApp().run()
