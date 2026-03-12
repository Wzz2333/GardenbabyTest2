# 🔴 极简测试代码（保证100%能跑）
from kivy.app import App
from kivy.uix.label import Label

class MainApp(App):
    def build(self):
        # 显示文字，证明打包成功
        return Label(text="打包成功！🎉", font_size=40, color=(1,1,1,1))

if __name__ == "__main__":
    MainApp().run()
