from kivy.app import App
from kivy.uix.label import Label

class FinalTestApp(App):
    def build(self):
        return Label(text="兜底测试：如果这个都失败，就是环境问题！", font_size=25)

if __name__ == "__main__":
    FinalTestApp().run()
