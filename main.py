import os, sys, time, uuid, random
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.text import LabelBase
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle

# 窗口大小设置（手机适配）
Config.set('graphics', 'width', 360)
Config.set('graphics', 'height', 640)
Config.set('graphics', 'resizable', False)


# 资源路径获取（适配你的所有文件夹）
def resource_path(relative_path):
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 自定义圆角按钮（用 ziti2.ttf 字体）
class RoundedButton(Button):
    def __init__(self, **kwargs):
        self.default_alpha = kwargs.pop('alpha', 0.3)
        # 按钮用你的 ziti2.ttf（对应注册的 Font2）
        kwargs.setdefault('font_name', 'Font2')
        kwargs.setdefault('font_size', '18sp')
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, self.default_alpha)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_state(self, instance, value):
        self.bg_color.a = 0.5 if value == 'down' else self.default_alpha


# 图片按钮（通用，适配所有图片）
class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True


# 基础屏幕类
class BaseScreen(Screen):
    pass


# 主屏幕（整合所有资源）
class MainScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = RelativeLayout()

        # 1. 背景图（用你的 startbk.png）
        self.bg_image = Image(
            source=resource_path('sources/backgrounds/startbk.png'),
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.layout.add_widget(self.bg_image)

        # 2. 标题文字 → 用你的 ziti1.ttf（Font1）
        self.title_label = Label(
            text='花园宝宝 v0.2.5',
            font_name='Font1',
            font_size='40sp',
            color=(1, 0.8, 0, 1),  # 暖黄色，适配背景
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        self.layout.add_widget(self.title_label)

        # 3. 花朵图片（初始显示flower1.png，点击切换）
        self.flower_index = 0
        self.flower_list = [
            'sources/flowers/flower1.png',
            'sources/flowers/flower2.png',
            'sources/flowers/flower3.png',
            'sources/flowers/flower4.png'
        ]
        self.flower_image = ImageButton(
            source=resource_path(self.flower_list[self.flower_index]),
            size_hint=(None, None),
            size=(200, 200),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        self.flower_image.bind(on_release=self.switch_flower)
        self.layout.add_widget(self.flower_image)

        # 4. 头像选择按钮（显示head0.png，点击切换）
        self.avatar_index = 0
        self.avatar_list = [
            'sources/avatars/head0.png',
            'sources/avatars/head1.png',
            'sources/avatars/head2.png',
            'sources/avatars/head3.png'
        ]
        self.avatar_image = ImageButton(
            source=resource_path(self.avatar_list[self.avatar_index]),
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={'x': 0.05, 'y': 0.05}
        )
        self.avatar_image.bind(on_release=self.switch_avatar)
        self.layout.add_widget(self.avatar_image)

        # 5. 切换背景按钮（用ziti2.ttf）
        self.bg_index = 0
        self.bg_list = [f'sources/backgrounds/bk{i}.jpg' for i in range(10)]
        self.change_bg_btn = RoundedButton(
            text='切换背景',
            alpha=0.5,
            size_hint=(None, None),
            size=(120, 40),
            pos_hint={'right': 0.95, 'y': 0.05}
        )
        self.change_bg_btn.bind(on_release=self.switch_bg)
        self.layout.add_widget(self.change_bg_btn)

        self.add_widget(self.layout)

    # 切换花朵图片
    def switch_flower(self, *args):
        self.flower_index = (self.flower_index + 1) % len(self.flower_list)
        self.flower_image.source = resource_path(self.flower_list[self.flower_index])

    # 切换头像
    def switch_avatar(self, *args):
        self.avatar_index = (self.avatar_index + 1) % len(self.avatar_list)
        self.avatar_image.source = resource_path(self.avatar_list[self.avatar_index])

    # 切换背景图
    def switch_bg(self, *args):
        self.bg_index = (self.bg_index + 1) % len(self.bg_list)
        self.bg_image.source = resource_path(self.bg_list[self.bg_index])


# 主应用类（注册所有资源）
class GardenBabyApp(App):
    title = "花园宝宝"
    version = "0.2.5"

    def build(self):
        # 1. 注册你的两个字体（ziti1.ttf / ziti2.ttf）
        LabelBase.register(name='Font1', fn_regular=resource_path('sources/fonts/ziti1.ttf'))
        LabelBase.register(name='Font2', fn_regular=resource_path('sources/fonts/ziti2.ttf'))

        # 2. 创建屏幕管理器
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(MainScreen(name='main'))

        # 3. 读取data和logs文件（演示用，确保能访问）
        self.read_extra_files()

        return self.sm

    # 读取data和logs文件夹的文件（确保能访问）
    def read_extra_files(self):
        # 读取data/text.txt
        data_path = resource_path('sources/data/text.txt')
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                print("Data文件内容：", f.readline())

        # 读取logs最新版本文件
        log_path = resource_path('sources/logs/beta0.2.5.txt')
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                print("最新日志：", f.readline())


if __name__ == '__main__':
    # 确保所有文件夹存在（防止报错）
    for folder in ['sources/flowers', 'sources/fonts', 'sources/avatars',
                   'sources/backgrounds', 'sources/logs', 'sources/data']:
        if not os.path.exists(folder):
            os.makedirs(folder)
    # 运行应用
    GardenBabyApp().run()