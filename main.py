from kivy.config import Config
Config.set("graphics", "multisamples", "0")
import sys
import os

# 获取资源路径（兼容 PyInstaller 打包后的环境）
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
# 设置 Kivy 窗口的初始大小，以模拟常见的手机屏幕分辨率 (例如 360x640)
# 这在电脑上调试时非常有用，可以让你预览应用在手机上的实际布局
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
# 禁止窗口手动调整大小，以更好地模拟手机固定屏幕的特性 (可选)
# Config.set('graphics', 'resizable', False)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.text import LabelBase
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
import time
import uuid
import random

# 字体注册将在App.build()方法中执行

class SystemSpinnerOption(SpinnerOption):
    """自定义 Spinner 选项，统一使用系统字体"""
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'SystemFont')
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 0.8) # 让下拉菜单背景深一点方便看清
        self.color = (0, 0, 0, 1) # 默认黑字

class ImageButton(ButtonBehavior, Image):
    """自定义图片按钮，保持长宽比并允许拉伸"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True

class PoetryButton(ButtonBehavior, BoxLayout):
    """专门用于显示古诗的点击区域"""
    pass

class RoundedButton(Button):
    """自定义圆角半透明按钮"""
    def __init__(self, **kwargs):
        # 获取透明度，默认为 0.3
        alpha = kwargs.pop('alpha', 0.3)
        # 默认使用中文字体
        # The 'alpha' value was local and not stored, causing the button's transparency
        # to reset to a hardcoded value (0.3) after being pressed. 
        # We store it as an instance variable to correctly restore it.
        self.default_alpha = kwargs.pop('alpha', 0.3)
        # 默认使用中文字体
        kwargs.setdefault('font_name', 'SystemFont')
        super().__init__(**kwargs)
        # 移除按钮默认的背景图
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # 让原始背景完全透明
        
        with self.canvas.before:
            # 绘制自定义的圆角矩形
            self.bg_color_instruction = Color(1, 1, 1, alpha)
            self.bg_rect_instruction = RoundedRectangle(pos=self.pos, size=self.size, radius=[15,])
        
        # 绑定位置和大小变化
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.bg_rect_instruction.pos = self.pos
        self.bg_rect_instruction.size = self.size

    def on_state(self, instance, value):
        """处理点击时的颜色反馈"""
        if value == 'down':
            self.bg_color_instruction.a = 0.5  # 按下时变深一点
        else:
            self.bg_color_instruction.a = 0.3  # 恢复

class BaseScreen(Screen):
    """所有屏幕的基类，用于统一处理样式更新"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 子屏幕不再独立绘制背景，而是保持透明，露出根布局的背景

class GardenScreen(BaseScreen):
    """"“花园”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 花园界面不再使用自己的背景图片，而是使用根布局的背景
        # 根布局的背景会在update_styles方法中设置为bk9.jpg
        self.label = Label(text='花园', font_name='SystemFont', font_size='50sp')
        self.add_widget(self.label)

class MainScreen(BaseScreen):
    """“主界面”屏幕，包含打卡功能和随机古诗"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 使用RelativeLayout作为根布局，以便精确定位时间显示
        self.layout = RelativeLayout()
        
        # 时间显示区，放在黄金比例位置（约 0.618）
        self.time_layout = BoxLayout(orientation='vertical', size_hint=(0.8, None), height='100dp', spacing='10dp', opacity=0)
        # 使用 Button 作为时间标签，以便添加点击事件
        self.time_label = Button(text='', font_name='SystemFont', font_size='60sp', halign='center', valign='middle',
                               background_normal='', background_color=(0, 0, 0, 0), size_hint=(1, 1))
        self.time_label.bind(on_release=self.show_pending_tasks)
        self.time_layout.add_widget(self.time_label)
        # 将时间布局添加到根布局，放在黄金比例位置
        self.layout.add_widget(self.time_layout)
        # 绑定大小变化事件，确保时间布局始终在黄金比例位置
        self.bind(size=self._update_time_position)
        
        # 主内容布局
        self.content_layout = BoxLayout(orientation='vertical', spacing='10dp', padding=20, size_hint=(1, 1))
        
        # 2. 任务展示区
        self.task_info_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='150dp', spacing='10dp')
        self.task_name_label = Label(text='', font_name='SystemFont', font_size='24sp', bold=True)
        self.task_detail_label = Label(text='', font_name='SystemFont', font_size='18sp', line_height=1.2)
        self.start_task_button = RoundedButton(text='开始任务', font_name='SystemFont', size_hint_y=None, height='40dp', alpha=0.3)
        self.start_task_button.bind(on_release=self.start_task_from_main)
        self.task_info_layout.add_widget(self.task_name_label)
        self.task_info_layout.add_widget(self.task_detail_label)
        self.task_info_layout.add_widget(self.start_task_button)
        self.content_layout.add_widget(self.task_info_layout)

        # 2.5 花朵和诗句展示区
        flower_poetry_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='200dp', spacing='10dp')
        
        # 左侧诗句（竖排）
        self.poetry_left = Button(text='', font_name='PoetryFont', font_size='16sp', halign='center', valign='middle', size_hint=(0.2, 1),
                                background_normal='', background_color=(0,0,0,0))
        self.poetry_left.bind(size=self.poetry_left.setter('text_size'))
        flower_poetry_layout.add_widget(self.poetry_left)
        
        # 花朵展示区 (居中展示花朵形态)
        self.flower_image = ImageButton(source=resource_path('sources/flowers/flower1.png'), size_hint=(None, None), size=('200dp', '200dp'),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
        flower_poetry_layout.add_widget(self.flower_image)
        
        # 右侧诗句（竖排）
        self.poetry_right = Button(text='', font_name='PoetryFont', font_size='16sp', halign='center', valign='middle', size_hint=(0.2, 1),
                                 background_normal='', background_color=(0,0,0,0))
        self.poetry_right.bind(size=self.poetry_right.setter('text_size'))
        flower_poetry_layout.add_widget(self.poetry_right)
        
        # 绑定点击事件
        self.poetry_left.bind(on_release=self.change_poetry)
        self.poetry_right.bind(on_release=self.change_poetry)
        self.flower_image.bind(on_release=self.change_poetry)
        
        self.content_layout.add_widget(flower_poetry_layout)
        
        # 2.6 步骤展示区 (可滑动)
        self.steps_scroll_view = ScrollView(size_hint_y=None, height='120dp')
        self.steps_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='5dp')
        self.steps_layout.bind(minimum_height=self.steps_layout.setter('height'))
        self.steps_scroll_view.add_widget(self.steps_layout)
        self.content_layout.add_widget(self.steps_scroll_view)
        
        # 2.7 任务提醒区
        self.reminder_label = Label(text='', font_name='SystemFont', font_size='16sp', color=(1, 0, 0, 1), halign='center')
        self.content_layout.add_widget(self.reminder_label)
        
        # 占位符，用于调整布局
        self.content_layout.add_widget(Label(size_hint_y=1))
        
        # 将内容布局添加到根布局
        self.layout.add_widget(self.content_layout)
        
        self.add_widget(self.layout)
        
        # 定时器
        self.update_clock = None
    
    def _update_time_position(self, instance, value):
        """更新时间布局的位置到指定位置"""
        # 调整时间布局的 y 位置，使其底部位于屏幕的 75% 高度处
        y_pos = self.height * 0.75
        # 设置时间布局的位置，保持原来的左边距
        self.time_layout.pos = (self.width * 0.1, y_pos)
    
    def show_pending_tasks(self, *args):
        """显示所有未完成的任务"""
        app = App.get_running_app()
        # 检查是否有活跃任务
        if app.active_task_id:
            return  # 如果有活跃任务，不显示弹窗
        
        # 获取所有未完成的任务
        pending_tasks = app.tasks
        
        if not pending_tasks:
            # 如果没有未完成的任务，显示提示
            content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
            content.add_widget(Label(text='没有未完成的任务', font_name='SystemFont', font_size='18sp', halign='center'))
            close_btn = RoundedButton(text='关闭', font_name='SystemFont', size_hint_y=None, height='50dp')
            content.add_widget(close_btn)
        else:
            # 创建滚动视图，用于显示任务列表
            scroll_view = ScrollView(size_hint=(1, 1))
            task_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp', padding='10dp')
            task_layout.bind(minimum_height=task_layout.setter('height'))
            
            # 添加每个未完成的任务
            for task in pending_tasks:
                task_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[10, 5, 10, 5])
                # 添加背景颜色 - 使用更深的颜色确保可见
                with task_box.canvas.before:
                    Color(0.2, 0.2, 0.2, 0.3)
                    rect = Rectangle(pos=task_box.pos, size=task_box.size)
                # 绑定大小和位置变化，更新背景
                task_box.bind(pos=lambda instance, value: setattr(rect, 'pos', instance.pos))
                task_box.bind(size=lambda instance, value: setattr(rect, 'size', instance.size))
                
                # 任务名称 - 使用固定高度
                task_name = Label(text=task['name'], font_name='SystemFont', font_size='16sp', halign='left', bold=True, 
                                 size_hint_y=None, height='35dp', valign='middle', padding=[5, 0, 0, 0])
                
                # 任务时长
                task_detail = Label(text=f"时长：{task['duration']}{task.get('duration_unit', '分钟')}", 
                                   font_name='SystemFont', font_size='13sp', halign='left', 
                                   size_hint_y=None, height='25dp', valign='top', padding=[5, 0, 0, 0])
                
                # 开始任务按钮
                start_btn = RoundedButton(text='开始任务', font_name='SystemFont', size_hint_y=None, height='30dp', alpha=0.3)
                # 绑定开始任务的事件
                start_btn.bind(on_release=lambda x, task=task, btn=start_btn: self.start_task_from_popup(task, btn))
                
                task_box.add_widget(task_name)
                task_box.add_widget(task_detail)
                task_box.add_widget(start_btn)
                task_layout.add_widget(task_box)
            
            scroll_view.add_widget(task_layout)
            
            content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
            title_label = Label(text='未完成的任务', font_name='SystemFont', font_size='20sp', halign='center', bold=True, size_hint_y=None, height='40dp')
            content.add_widget(title_label)
            content.add_widget(scroll_view)
            close_btn = RoundedButton(text='关闭', font_name='SystemFont', size_hint_y=None, height='50dp')
            content.add_widget(close_btn)
        
        # 创建并显示弹窗
        popup = Popup(title='任务列表', content=content, size_hint=(0.8, 0.7),
                     title_font='SystemFont', title_align='center')
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def start_task_from_popup(self, task, btn=None):
        """从弹窗开始任务"""
        app = App.get_running_app()
        
        # 检查是否已经有活跃任务
        if app.active_task_id and app.active_task_id != task['id']:
            # 已经有其他任务在运行，先关闭任务列表弹窗
            from kivy.uix.popup import Popup
            if hasattr(App.get_running_app().root, 'children'):
                for widget in App.get_running_app().root.children[:]:
                    if isinstance(widget, Popup):
                        widget.dismiss()
            
            # 延迟显示提示弹窗
            Clock.schedule_once(lambda dt: self.show_cannot_start_popup(), 0.1)
            return
        
        # 设置为活跃任务
        app.active_task_id = task['id']
        # 只有当任务还未开始时，才设置开始时间
        if 'start_time' not in task and task.get('duration'):
            # 记录任务开始时间
            task['start_time'] = time.time()
            # 计算任务结束时间
            duration = int(task['duration'])
            unit = task.get('duration_unit', '分钟')
            if unit == '小时':
                duration *= 60
            elif unit == '天':
                duration *= 1440
            task['end_time'] = task['start_time'] + duration * 60  # 转换为秒
        # 保存任务数据
        app.save_task_data()
        # 更新主界面
        self.update_active_task()
        # 更新按钮文本
        if btn:
            btn.text = '任务已开始'
            btn.alpha = 0.5
        # 关闭弹窗
        from kivy.uix.popup import Popup
        # 获取当前打开的弹窗并关闭
        if hasattr(App.get_running_app().root, 'children'):
            for widget in App.get_running_app().root.children[:]:
                if isinstance(widget, Popup):
                    widget.dismiss()
    
    def show_cannot_start_popup(self):
        """显示不能同时开始两个任务的提示弹窗"""
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        content.add_widget(Label(text='有正在进行的任务', 
                                font_name='SystemFont', font_size='18sp', halign='center'))
        close_btn = RoundedButton(text='确定', font_name='SystemFont', size_hint_y=None, height='40dp')
        content.add_widget(close_btn)
        popup = Popup(title='提示', content=content, size_hint=(0.8, 0.4),
                     title_font='SystemFont', title_align='center')
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def on_enter(self, *args):
        """进入页面时随机显示一句古诗并更新任务信息"""
        self.change_poetry()
        self.update_active_task()
        # 启动定时器，每秒更新一次
        if self.update_clock is None:
            self.update_clock = Clock.schedule_interval(self.update_countdown, 1)

    def on_leave(self, *args):
        """离开页面时停止定时器"""
        if self.update_clock is not None:
            Clock.unschedule(self.update_clock)
            self.update_clock = None

    def start_task_from_main(self, *args):
        """从主界面开始任务"""
        app = App.get_running_app()
        active_id = app.active_task_id
        
        if active_id:
            task = next((t for t in app.tasks if t['id'] == active_id), None)
            if task and task.get('duration'):
                # 记录任务开始时间
                task['start_time'] = time.time()
                # 计算任务结束时间
                duration = int(task['duration'])
                unit = task.get('duration_unit', '分钟')
                if unit == '小时':
                    duration *= 60
                elif unit == '天':
                    duration *= 1440
                task['end_time'] = task['start_time'] + duration * 60  # 转换为秒
                # 保存任务数据
                app.save_task_data()
                # 更新主界面
                self.update_active_task()

    def end_task_from_main(self, *args):
        """从主界面结束任务"""
        app = App.get_running_app()
        active_id = app.active_task_id
        
        if active_id:
            task = next((t for t in app.tasks if t['id'] == active_id), None)
            if task:
                # 移除任务的开始和结束时间
                if 'start_time' in task:
                    del task['start_time']
                if 'end_time' in task:
                    del task['end_time']
                # 保存任务数据
                app.save_task_data()
                # 更新主界面
                self.update_active_task()

    def update_countdown(self, dt):
        """更新倒计时显示和检查任务是否超时"""
        app = App.get_running_app()
        active_id = app.active_task_id
        
        if active_id:
            # 有任务时，隐藏时间显示
            self.time_layout.opacity = 0
            task = next((t for t in app.tasks if t['id'] == active_id), None)
            if task and 'start_time' in task:
                # 更新任务信息
                self.update_active_task()
                
                # 检查任务是否超时
                current_time = time.time()
                if current_time > task['end_time']:
                    # 显示超时提醒
                    self.reminder_label.text = '任务已超时，请尽快完成！'
                else:
                    # 检查是否接近超时（剩余时间小于10分钟）
                    remaining_time = task['end_time'] - current_time
                    if remaining_time < 10 * 60:  # 10分钟
                        self.reminder_label.text = '任务即将超时，请尽快完成！'
                    else:
                        self.reminder_label.text = ''
            else:
                self.reminder_label.text = ''
        else:
            # 没有任务时，显示时间
            self.time_layout.opacity = 1
            # 更新时间显示
            current_time = time.time()
            time_str = time.strftime('%H:%M:%S', time.localtime(current_time))
            self.time_label.text = time_str
            self.reminder_label.text = ''

    def update_active_task(self):
        """更新当前显示的任务信息"""
        app = App.get_running_app()
        active_id = app.active_task_id
        
        # 清空步骤布局
        self.steps_layout.clear_widgets()
        
        if active_id:
            # 查找任务
            task = next((t for t in app.tasks if t['id'] == active_id), None)
            if task:
                self.task_name_label.text = task['name']
                unit = task.get('duration_unit', '分钟')
                
                # 更新任务详情显示
                steps = task.get('steps', [])
                remaining_steps = sum(1 for step in steps if not step.get('completed', False))
                
                # 检查任务是否已开始
                if 'start_time' in task:
                    # 计算剩余时间
                    current_time = time.time()
                    remaining_time = max(0, task['end_time'] - current_time)
                    minutes, seconds = divmod(int(remaining_time), 60)
                    hours, minutes = divmod(minutes, 60)
                    
                    # 格式化剩余时间
                    if hours > 0:
                        time_str = f"{hours}小时{minutes}分钟"
                    else:
                        time_str = f"{minutes}分{seconds}秒"
                    
                    # 格式化开始时间
                    start_time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(task['start_time']))
                    
                    # 更新任务详情，将倒计时和开始时间另起一行
                    self.task_detail_label.text = f"时长：{task['duration']}{unit} | 剩余步骤：{remaining_steps}步\n剩余时间：{time_str}\n开始时间：{start_time_str}"
                else:
                    self.task_detail_label.text = f"时长：{task['duration']}{unit} | 剩余步骤：{remaining_steps}步"
                
                self.task_info_layout.opacity = 1
                
                # 根据任务是否已经开始来显示或隐藏开始任务按钮
                if 'start_time' in task:
                    self.start_task_button.opacity = 0
                else:
                    self.start_task_button.text = '开始任务'
                    self.start_task_button.opacity = 1
                    self.start_task_button.bind(on_release=self.start_task_from_main)
                
                # 显示步骤列表
                for i, step in enumerate(steps):
                    self.add_step_item(step, i)
                
                # 更新花朵形态
                try:
                    total_steps = len(steps)
                    if total_steps <= 0:
                        total_steps = 1 # 防止除以0
                    
                    # 计算进度比例 (已完成步骤 / 总步骤)
                    completed_steps = sum(1 for step in steps if step.get('completed', False))
                    progress_ratio = completed_steps / total_steps
                    
                    if progress_ratio < 0.25:
                        self.flower_image.source = resource_path('sources/flowers/flower1.png')
                    elif progress_ratio < 0.5:
                        self.flower_image.source = resource_path('sources/flowers/flower2.png')
                    elif progress_ratio < 0.75:
                        self.flower_image.source = resource_path('sources/flowers/flower3.png')
                    else:
                        self.flower_image.source = resource_path('sources/flowers/flower4.png')
                    
                    self.flower_image.opacity = 1
                    self.steps_scroll_view.opacity = 1
                except (ValueError, TypeError):
                    self.flower_image.opacity = 0
                    self.steps_scroll_view.opacity = 0
                
                return
        
        # 如果没有活跃任务，隐藏该区域和花朵
        self.task_name_label.text = ""
        self.task_detail_label.text = ""
        self.task_info_layout.opacity = 0
        self.flower_image.opacity = 0
        self.steps_scroll_view.opacity = 0
        self.flower_image.source = resource_path('sources/flowers/flower1.png') # 重置默认值

    def add_step_item(self, step, index):
        """添加步骤项"""
        step_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp', spacing='10dp')
        
        # 步骤名称
        app = App.get_running_app()
        step_label = Label(text=step['name'], font_name='SystemFont', font_size='16sp', halign='left', valign='middle', color=app.font_color)
        step_label.bind(size=step_label.setter('text_size'))
        step_row.add_widget(step_label)
        
        # 完成状态按钮
        status_btn = RoundedButton(
            text='✓' if step.get('completed', False) else '□', 
            font_name='SystemFont', 
            font_size='16sp',
            size_hint_x=None, 
            width='40dp',
            alpha=0.3
        )
        status_btn.bind(on_press=lambda x, idx=index: self.toggle_step_completion(idx))
        step_row.add_widget(status_btn)
        
        self.steps_layout.add_widget(step_row)

    def toggle_step_completion(self, index):
        """切换步骤完成状态"""
        app = App.get_running_app()
        active_id = app.active_task_id
        if not active_id:
            return

        task = next((t for t in app.tasks if t['id'] == active_id), None)
        if not task:
            return

        steps = task.get('steps', [])
        if 0 <= index < len(steps):
            # 切换完成状态
            steps[index]['completed'] = not steps[index]['completed']
            
            # 更新任务的 frequency 字段（剩余步骤数）
            remaining_steps = sum(1 for step in steps if not step.get('completed', False))
            task['frequency'] = str(remaining_steps)
            
            # 检查是否所有步骤都完成了
            if remaining_steps == 0:
                self.complete_task(task)
            
            # 保存数据并更新界面
            app.save_task_data()
            self.update_active_task()

    def change_poetry(self, *args):
        """随机切换一句古诗并分左右竖排显示"""
        app = App.get_running_app()
        if app.poems:
            poem = random.choice(app.poems)
            # 处理常见的中英文标点符号进行分割
            delimiters = ['，', '。', ',', '.', '；', ';']
            found = False
            for punc in delimiters:
                if punc in poem:
                    parts = poem.split(punc, 1) # 只分割一次
                    if len(parts) >= 2 and parts[0] and parts[1]:
                        # 左侧竖排显示
                        left_text = '\n'.join(list(parts[0].strip() + punc))
                        self.poetry_left.text = left_text
                        # 右侧竖排显示
                        right_text = '\n'.join(list(parts[1].strip()))
                        self.poetry_right.text = right_text
                        found = True
                        break
            
            if not found:
                # 如果诗句无法分割，只显示在左侧
                left_text = '\n'.join(list(poem))
                self.poetry_left.text = left_text
                self.poetry_right.text = ""

    def complete_task(self, task):
        """处理任务完成的逻辑"""
        app = App.get_running_app()
        
        # 1. 从活跃任务列表移除
        app.tasks = [t for t in app.tasks if t['id'] != task['id']]
        
        # 2. 添加到已完成列表
        task['completed_at'] = time.time()
        app.completed_tasks.append(task)
        
        # 3. 取消主界面显示
        app.active_task_id = ''
        app.save_task_data()
        self.update_active_task()
        
        # 4. 弹出祝贺窗口
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        content.add_widget(Label(text='恭喜！该任务已完成！', font_name='SystemFont', font_size='20sp'))
        close_btn = RoundedButton(text='关闭', font_name='SystemFont', size_hint_y=None, height='50dp')
        content.add_widget(close_btn)
        
        popup = Popup(title='任务完成', content=content, size_hint=(0.8, 0.4),
                     title_font='SystemFont', title_align='center')
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

class ProfileScreen(BaseScreen):
    """“我的”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = RelativeLayout()
        
        # 1. 右上角设置按钮
        settings_button = RoundedButton(text='设置', font_name='SystemFont', size_hint=(None, None), size=('100dp', '50dp'), 
                                  pos_hint={'top': 1, 'right': 1})
        settings_button.bind(on_press=lambda x: App.get_running_app().change_screen('settings', direction='left'))
        self.layout.add_widget(settings_button)
        
        # 2. 中间区域 (头像 + 用户名) - 上移位置
        center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=('200dp', '230dp'), 
                                 pos_hint={'center_x': 0.5, 'top': 0.9}, spacing='5dp')
        
        # 头像组件
        app = App.get_running_app()
        self.avatar_image = ImageButton(source=app.avatar_path, size_hint=(None, None), size=('130dp', '130dp'),
                                       pos_hint={'center_x': 0.5})
        self.avatar_image.bind(on_release=app.open_avatar_popup)
        center_layout.add_widget(self.avatar_image)
        
        # 用户名组件
        self.username_label = Button(text=app.username, font_name='SystemFont', font_size='22sp', size_hint=(1, None), height='40dp',
                                    background_normal='', background_color=(0,0,0,0), color=app.font_color)
        self.username_label.bind(on_release=app.open_username_popup)
        center_layout.add_widget(self.username_label)
        
        self.layout.add_widget(center_layout)

        # 3. 任务管理入口
        task_mgmt_btn = RoundedButton(text='任务管理', font_name='SystemFont', font_size='20sp',
                                  size_hint=(None, None), size=('200dp', '60dp'),
                                  pos_hint={'center_x': 0.5, 'top': 0.4})
        task_mgmt_btn.bind(on_press=lambda x: App.get_running_app().change_screen('task_mgmt', direction='left'))
        self.layout.add_widget(task_mgmt_btn)
        
        # 4. 更新日志按钮
        update_log_btn = RoundedButton(text='更新日志', font_name='SystemFont', font_size='20sp',
                                  size_hint=(None, None), size=('200dp', '60dp'),
                                  pos_hint={'center_x': 0.5, 'top': 0.3})
        update_log_btn.bind(on_press=lambda x: App.get_running_app().change_screen('update_log', direction='left'))
        self.layout.add_widget(update_log_btn)
        
        self.add_widget(self.layout)

class TaskManagementScreen(BaseScreen):
    """“任务管理”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding='15dp', spacing='15dp')
        
        # 1. 标题栏
        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text='任务管理', font_name='SystemFont', font_size='22sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        
        # 历史任务按钮
        history_btn = RoundedButton(text='历史', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                  pos_hint={'center_y': 0.5, 'right': 1})
        history_btn.bind(on_release=lambda x: App.get_running_app().change_screen('history', direction='left'))
        header.add_widget(history_btn)

        back_btn = RoundedButton(text='返回', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                pos_hint={'center_y': 0.5, 'x': 0})
        back_btn.bind(on_release=lambda x: App.get_running_app().change_screen('profile', direction='right'))
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # 2. 任务列表容器
        self.scroll_view = ScrollView()
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp')
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.scroll_view.add_widget(self.task_list)
        self.layout.add_widget(self.scroll_view)
        
        # 3. 创建新任务按钮 (始终在最下面)
        self.create_btn = RoundedButton(text='创建新任务', font_name='SystemFont', size_hint_y=None, height='60dp')
        self.create_btn.bind(on_release=self.go_to_edit)
        self.layout.add_widget(self.create_btn)
        
        self.add_widget(self.layout)

    def on_enter(self, *args):
        """进入页面时加载任务列表"""
        self.refresh_tasks()

    def refresh_tasks(self):
        """刷新任务列表显示"""
        self.task_list.clear_widgets()
        app = App.get_running_app()
        
        # 按创建时间排序
        sorted_tasks = sorted(app.tasks, key=lambda x: x.get('created_at', 0))
        
        for task in sorted_tasks:
            # 每一项任务的容器
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp', spacing='10dp')
            
            # 任务信息按钮 (点击也可进入编辑)
            unit = task.get('duration_unit', '分钟')
            info_btn = RoundedButton(text=f"{task['name']} ({task['duration']}{unit})", font_name='SystemFont', alpha=0.2)
            info_btn.bind(on_release=lambda x, t=task: self.go_to_edit(task=t))
            item.add_widget(info_btn)
            
            # 三个点菜单按钮
            menu_btn = RoundedButton(text='...', font_name='SystemFont', size_hint_x=None, width='50dp', alpha=0.2)
            menu_btn.bind(on_release=lambda x, t=task: self.open_task_menu(t))
            item.add_widget(menu_btn)
            
            self.task_list.add_widget(item)
        
        # 刷新新创建组件的样式（如字体颜色）
        app.update_styles()

    def go_to_edit(self, *args, task=None):
        """显示任务详情或导航到编辑屏幕"""
        if not task:
            # 没有任务参数，导航到编辑屏幕创建新任务
            app = App.get_running_app()
            edit_screen = app.screen_manager.get_screen('edit_task')
            edit_screen.load_task()  # 不带参数表示新建任务
            app.change_screen('edit_task', direction='left')
            return
        
        # 创建任务详情弹窗
        content = BoxLayout(orientation='vertical', padding='15dp', spacing='10dp')
        
        # 任务名称
        name_label = Label(text=f"任务名称：{task['name']}", font_name='SystemFont', font_size='20sp', halign='left')
        content.add_widget(name_label)
        
        # 任务时长
        unit = task.get('duration_unit', '分钟')
        duration_label = Label(text=f"任务时长：{task['duration']}{unit}", font_name='SystemFont', font_size='18sp', halign='left')
        content.add_widget(duration_label)
        
        # 开始时间
        if 'start_time' in task:
            start_time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(task['start_time']))
            start_label = Label(text=f"开始时间：{start_time_str}", font_name='SystemFont', font_size='18sp', halign='left')
            content.add_widget(start_label)
            
            # 剩余时长
            current_time = time.time()
            remaining_time = max(0, task['end_time'] - current_time)
            minutes, seconds = divmod(int(remaining_time), 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                time_str = f"{hours}小时{minutes}分钟"
            else:
                time_str = f"{minutes}分{seconds}秒"
            remaining_label = Label(text=f"剩余时长：{time_str}", font_name='SystemFont', font_size='18sp', halign='left')
            content.add_widget(remaining_label)
        
        # 步骤信息
        steps = task.get('steps', [])
        total_steps = len(steps)
        remaining_steps = sum(1 for step in steps if not step.get('completed', False))
        steps_label = Label(text=f"全部步骤：{total_steps}步 | 剩余步骤：{remaining_steps}步", font_name='SystemFont', font_size='18sp', halign='left')
        content.add_widget(steps_label)
        
        # 步骤列表
        steps_title = Label(text="步骤列表：", font_name='SystemFont', font_size='16sp', halign='left', bold=True)
        content.add_widget(steps_title)
        
        steps_layout = BoxLayout(orientation='vertical', spacing='5dp')
        for i, step in enumerate(steps):
            step_label = Label(text=f"{i+1}. {step['name']} {'✓' if step.get('completed', False) else '□'}", font_name='SystemFont', font_size='16sp', halign='left')
            steps_layout.add_widget(step_label)
        content.add_widget(steps_layout)
        
        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', spacing='10dp', size_hint_y=None, height='50dp')
        edit_btn = RoundedButton(text='编辑任务', font_name='SystemFont')
        close_btn = RoundedButton(text='关闭', font_name='SystemFont')
        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)
        
        # 创建弹窗
        popup = Popup(title='任务详情', content=content, size_hint=(0.8, 0.7),
                     title_font='SystemFont', title_align='center')
        
        # 绑定按钮事件
        def edit_task(*args):
            popup.dismiss()
            app = App.get_running_app()
            edit_screen = app.screen_manager.get_screen('edit_task')
            edit_screen.load_task(task)
            app.change_screen('edit_task', direction='left')
        
        edit_btn.bind(on_release=edit_task)
        close_btn.bind(on_release=popup.dismiss)
        
        popup.open()

    def open_task_menu(self, task):
        """打开任务操作菜单"""
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        popup = Popup(title=f"任务：{task['name']}", content=content, size_hint=(0.8, 0.4),
                     title_font='SystemFont')
        
        app = App.get_running_app()
        
        # 选项1：在主界面显示 或 取消显示
        if app.active_task_id == task['id']:
            cancel_show_btn = RoundedButton(text='取消显示', font_name='SystemFont')
            cancel_show_btn.bind(on_release=lambda x: self.set_active_task('', popup))
            content.add_widget(cancel_show_btn)
        else:
            show_btn = RoundedButton(text='在主界面显示', font_name='SystemFont')
            show_btn.bind(on_release=lambda x: self.set_active_task(task['id'], popup))
            content.add_widget(show_btn)
        
        # 选项2：开始任务
        if 'start_time' not in task:
            start_btn = RoundedButton(text='开始任务', font_name='SystemFont')
            start_btn.bind(on_release=lambda x: self.start_task(task, popup))
            content.add_widget(start_btn)
        else:
            # 选项2：结束任务
            end_btn = RoundedButton(text='结束任务', font_name='SystemFont')
            end_btn.bind(on_release=lambda x: self.end_task(task, popup))
            content.add_widget(end_btn)
        
        # 选项3：删除任务
        delete_btn = RoundedButton(text='删除任务', font_name='SystemFont')
        delete_btn.bind(on_release=lambda x: self.delete_task(task['id'], popup))
        content.add_widget(delete_btn)
        
        popup.open()

    def set_active_task(self, task_id, popup):
        app = App.get_running_app()
        app.active_task_id = task_id
        app.save_task_data()
        popup.dismiss()

    def start_task(self, task, popup):
        """开始任务，启动倒计时"""
        app = App.get_running_app()
        # 记录任务开始时间
        task['start_time'] = time.time()
        # 计算任务结束时间
        duration = int(task['duration'])
        unit = task.get('duration_unit', '分钟')
        if unit == '小时':
            duration *= 60
        elif unit == '天':
            duration *= 1440
        task['end_time'] = task['start_time'] + duration * 60  # 转换为秒
        # 保存任务数据
        app.save_task_data()
        # 关闭弹窗
        popup.dismiss()
        # 如果任务在主界面显示，更新主界面
        if app.active_task_id == task['id']:
            main_screen = app.screen_manager.get_screen('main')
            main_screen.update_active_task()

    def end_task(self, task, popup):
        """结束任务，提前终止倒计时并删除任务"""
        app = App.get_running_app()
        # 从任务列表中删除任务
        app.tasks = [t for t in app.tasks if t['id'] != task['id']]
        # 如果任务在主界面显示，取消显示
        if app.active_task_id == task['id']:
            app.active_task_id = ''
        # 保存任务数据
        app.save_task_data()
        # 关闭弹窗
        popup.dismiss()
        # 刷新任务列表
        self.refresh_tasks()
        # 如果任务在主界面显示，更新主界面
        if app.active_task_id == task['id']:
            main_screen = app.screen_manager.get_screen('main')
            main_screen.update_active_task()

    def delete_task(self, task_id, popup):
        app = App.get_running_app()
        app.tasks = [t for t in app.tasks if t['id'] != task_id]
        if app.active_task_id == task_id:
            app.active_task_id = ''
        app.save_task_data()
        popup.dismiss()
        self.refresh_tasks()

class EditTaskScreen(BaseScreen):
    """“编辑任务”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_id = None # None 表示新建
        
        self.layout = BoxLayout(orientation='vertical', padding='20dp', spacing='15dp')
        
        # 1. 标题栏
        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text='编辑任务', font_name='SystemFont', font_size='22sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        back_btn = RoundedButton(text='取消', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                pos_hint={'center_y': 0.5, 'x': 0})
        back_btn.bind(on_release=lambda x: App.get_running_app().change_screen('task_mgmt', direction='right'))
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # 2. 输入区域 (统一标签宽度 80dp)
        label_w = '80dp'

        # 2.1 任务名称
        name_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
        name_box.add_widget(Label(text='任务名称', font_name='SystemFont', size_hint_x=None, width=label_w))
        self.name_input = TextInput(multiline=False, font_name='SystemFont', font_size='18sp',
                                    background_color=(1, 1, 1, 0.3), cursor_color=(0, 0, 0, 1))
        name_box.add_widget(self.name_input)
        self.layout.add_widget(name_box)

        # 2.2 任务时长 (移到底部)
        duration_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
        duration_box.add_widget(Label(text='任务时长', font_name='SystemFont', size_hint_x=None, width=label_w))
        self.duration_input = TextInput(multiline=False, font_name='SystemFont', font_size='18sp',
                                        background_color=(1, 1, 1, 0.3), cursor_color=(0, 0, 0, 1),
                                        input_filter='int') # 限制只能输入整数
        duration_box.add_widget(self.duration_input)
        
        # 时长单位选择器 (修复文字显示问题，指定 option_cls)
        self.duration_unit_spinner = Spinner(
            text='分钟',
            values=('分钟', '小时', '天'),
            font_name='SystemFont',
            size_hint_x=None,
            width='80dp',
            background_color=(1, 1, 1, 0.3),
            option_cls=SystemSpinnerOption  # 使用自定义选项类以支持中文
        )
        duration_box.add_widget(self.duration_unit_spinner)
        self.layout.add_widget(duration_box)
        
        # 2.4 任务步骤管理
        steps_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
        steps_box.add_widget(Label(text='任务步骤', font_name='SystemFont', size_hint_x=None, width=label_w))
        self.steps_button = RoundedButton(text='管理步骤', font_name='SystemFont')
        self.steps_button.bind(on_release=self.open_steps_popup)
        steps_box.add_widget(self.steps_button)
        self.layout.add_widget(steps_box)
        
        # 步骤数据
        self.steps = []
            
        self.layout.add_widget(Label()) # 占位
        
        # 3. 保存按钮
        save_btn = RoundedButton(text='保存并退出', font_name='SystemFont', size_hint_y=None, height='60dp')
        save_btn.bind(on_release=self.save_and_exit)
        self.layout.add_widget(save_btn)
        
        self.add_widget(self.layout)

    def load_task(self, task=None):
        """加载待编辑的任务数据"""
        if task:
            self.task_id = task['id']
            self.name_input.text = task['name']
            self.duration_input.text = task['duration']
            self.duration_unit_spinner.text = task.get('duration_unit', '分钟')
            # 加载步骤数据
            self.steps = task.get('steps', [])
            if not self.steps:
                # 默认添加一个步骤
                self.steps = [{'name': '步骤 1', 'completed': False}]
        else:
            self.task_id = None
            self.name_input.text = ''
            self.duration_input.text = ''
            self.duration_unit_spinner.text = '分钟'
            # 新建任务默认一个步骤
            self.steps = [{'name': '步骤 1', 'completed': False}]

    def save_and_exit(self, *args):
        app = App.get_running_app()
        name = self.name_input.text.strip()
        duration = self.duration_input.text.strip()
        duration_unit = self.duration_unit_spinner.text
        
        if not name:
            return # 简单校验：名称不能为空
            
        if self.task_id:
            # 更新已有任务
            for t in app.tasks:
                if t['id'] == self.task_id:
                    t.update({
                        'name': name, 
                        'duration': duration, 
                        'duration_unit': duration_unit,
                        'frequency': str(len(self.steps)),
                        'total_frequency': str(len(self.steps)),
                        'steps': self.steps
                    })
                    break
        else:
            # 创建新任务
            new_task = {
                'id': str(uuid.uuid4()),
                'name': name,
                'duration': duration,
                'duration_unit': duration_unit,
                'frequency': str(len(self.steps)),
                'total_frequency': str(len(self.steps)),
                'steps': self.steps,
                'created_at': time.time()
            }
            app.tasks.append(new_task)
            
        app.save_task_data()
        app.change_screen('task_mgmt', direction='right')

    def open_steps_popup(self, instance):
        """打开步骤管理弹窗"""
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        
        # 步骤列表
        steps_list = BoxLayout(orientation='vertical', size_hint_y=None)
        steps_list.bind(minimum_height=steps_list.setter('height'))
        
        # 滚动视图
        scroll_view = ScrollView()
        scroll_view.add_widget(steps_list)
        content.add_widget(scroll_view)
        
        # 添加步骤按钮
        add_btn = RoundedButton(text='添加步骤', font_name='SystemFont', size_hint_y=None, height='40dp')
        add_btn.bind(on_release=lambda x: self.add_step(steps_list))
        content.add_widget(add_btn)
        
        # 保存按钮
        save_btn = RoundedButton(text='保存', font_name='SystemFont', size_hint_y=None, height='40dp')
        save_btn.bind(on_release=lambda x: popup.dismiss())
        content.add_widget(save_btn)
        
        # 创建弹窗
        popup = Popup(title='管理任务步骤', content=content, size_hint=(0.8, 0.6),
                     title_font='SystemFont')
        
        # 填充现有步骤
        for i, step in enumerate(self.steps):
            self.add_step_row(steps_list, step, i)
        
        popup.open()

    def add_step_row(self, container, step, index):
        """添加步骤行"""
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing='10dp')
        
        # 步骤名称输入
        step_input = TextInput(text=step['name'], font_name='SystemFont', font_size='16sp',
                              background_color=(1, 1, 1, 0.3), cursor_color=(0, 0, 0, 1))
        step_input.bind(text=lambda instance, value, idx=index: self.update_step_name(idx, value))
        row.add_widget(step_input)
        
        # 删除按钮
        delete_btn = RoundedButton(text='删除', font_name='SystemFont', size_hint_x=None, width='80dp')
        delete_btn.bind(on_release=lambda x, idx=index, r=row: self.delete_step(container, idx, r))
        row.add_widget(delete_btn)
        
        container.add_widget(row)

    def add_step(self, container):
        """添加新步骤"""
        new_step = {'name': f'步骤 {len(self.steps) + 1}', 'completed': False}
        self.steps.append(new_step)
        self.add_step_row(container, new_step, len(self.steps) - 1)

    def update_step_name(self, index, name):
        """更新步骤名称"""
        if 0 <= index < len(self.steps):
            self.steps[index]['name'] = name

    def delete_step(self, container, index, row_widget):
        """删除步骤"""
        if len(self.steps) > 1:  # 至少保留一个步骤
            self.steps.pop(index)
            container.remove_widget(row_widget)
            # 更新剩余步骤的编号
            for i, step in enumerate(self.steps):
                if step['name'].startswith('步骤 '):
                    step['name'] = f'步骤 {i + 1}'

class HistoryScreen(BaseScreen):
    """“历史任务”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding='15dp', spacing='15dp')
        
        # 1. 标题栏
        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text='已完成的任务', font_name='SystemFont', font_size='22sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        back_btn = RoundedButton(text='返回', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                pos_hint={'center_y': 0.5, 'x': 0})
        back_btn.bind(on_release=lambda x: App.get_running_app().change_screen('task_mgmt', direction='right'))
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # 2. 任务列表容器
        self.scroll_view = ScrollView()
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp')
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.scroll_view.add_widget(self.task_list)
        self.layout.add_widget(self.scroll_view)
        
        # 3. 清空按钮
        clear_btn = RoundedButton(text='一键清空历史', font_name='SystemFont', size_hint_y=None, height='50dp', alpha=0.5)
        clear_btn.bind(on_release=self.clear_history)
        self.layout.add_widget(clear_btn)
        
        self.add_widget(self.layout)

    def on_enter(self, *args):
        """进入页面时加载已完成的任务列表"""
        self.task_list.clear_widgets()
        app = App.get_running_app()
        
        # 按完成时间倒序排序
        sorted_tasks = sorted(app.completed_tasks, key=lambda x: x.get('completed_at', 0), reverse=True)
        
        for task in sorted_tasks:
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
            
            info = f"{task['name']} (完成于: {time.strftime('%Y-%m-%d', time.localtime(task['completed_at']))})"
            label = Label(text=info, font_name='SystemFont', color=app.font_color, halign='left')
            label.bind(size=label.setter('text_size'))
            item_layout.add_widget(label)
            
            delete_btn = RoundedButton(text='删除', font_name='SystemFont', size_hint_x=None, width='80dp', alpha=0.3)
            delete_btn.bind(on_release=lambda x, task_id=task['id']: self.delete_single_history(task_id))
            item_layout.add_widget(delete_btn)
            
            self.task_list.add_widget(item_layout)

    def delete_single_history(self, task_id):
        """删除单条历史记录"""
        app = App.get_running_app()
        app.completed_tasks = [t for t in app.completed_tasks if t['id'] != task_id]
        app.save_task_data()
        self.on_enter() # 重新加载列表

    def clear_history(self, instance):
        """清空所有历史记录"""
        app = App.get_running_app()
        app.completed_tasks = []
        app.save_task_data()
        self.on_enter() # 重新加载列表

class UpdateLogScreen(BaseScreen):
    """“更新日志”屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding='15dp', spacing='15dp')
        
        # 1. 标题栏
        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text='更新日志', font_name='SystemFont', font_size='22sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        back_btn = RoundedButton(text='返回', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                pos_hint={'center_y': 0.5, 'x': 0})
        back_btn.bind(on_release=lambda x: App.get_running_app().change_screen('profile', direction='right'))
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # 2. 日志文件列表
        self.log_list_layout = BoxLayout(orientation='vertical', spacing='10dp')
        self.log_list_scroll = ScrollView()
        self.log_buttons_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp')
        self.log_buttons_layout.bind(minimum_height=self.log_buttons_layout.setter('height'))
        self.log_list_scroll.add_widget(self.log_buttons_layout)
        self.log_list_layout.add_widget(self.log_list_scroll)
        self.layout.add_widget(self.log_list_layout)
        
        # 3. 提示信息
        self.tip_label = Label(text='点击版本号查看更新日志', font_name='SystemFont', font_size='16sp', 
                             halign='center', color=(0.5, 0.5, 0.5, 1))
        self.layout.add_widget(self.tip_label)
        
        self.add_widget(self.layout)

    def on_enter(self, *args):
        """进入页面时加载更新日志文件列表"""
        self.load_log_files()

    def load_log_files(self):
        """加载更新日志文件列表"""
        self.log_buttons_layout.clear_widgets()
        app = App.get_running_app()
        
        # 获取日志文件夹路径
        logs_dir = resource_path('sources/logs')
        try:
            import os
            # 列出所有txt文件
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.txt')]
            # 按文件名排序（版本号排序）
            log_files.sort(reverse=True)  # 最新的版本在前面
            
            if log_files:
                for log_file in log_files:
                    # 创建按钮
                    btn = RoundedButton(text=log_file[:-4], font_name='SystemFont', size_hint_y=None, height='50dp', alpha=0.3)
                    btn.bind(on_release=lambda x, file=log_file: self.show_log_window(file))
                    self.log_buttons_layout.add_widget(btn)
            else:
                # 没有日志文件
                no_log_label = Label(text='暂无更新日志', font_name='SystemFont', font_size='16sp', 
                                  halign='center', color=app.font_color, size_hint_y=None, height='50dp')
                self.log_buttons_layout.add_widget(no_log_label)
        except Exception as e:
            error_label = Label(text=f"无法加载更新日志文件: {str(e)}", font_name='SystemFont', font_size='16sp', 
                              halign='center', color=(1, 0, 0, 1), size_hint_y=None, height='50dp')
            self.log_buttons_layout.add_widget(error_label)

    def show_log_window(self, log_file):
        """打开新窗口显示更新日志内容"""
        try:
            # 获取应用实例
            app = App.get_running_app()
            
            # 创建一个新的屏幕来显示更新日志
            screen_name = f'log_detail_{log_file[:-4]}'
            
            # 移除已存在的屏幕
            if screen_name in app.screen_manager.screen_names:
                app.screen_manager.remove_widget(app.screen_manager.get_screen(screen_name))
                print(f"Removed existing screen: {screen_name}")
            
            # 创建新屏幕并设置名称
            log_screen = LogDetailScreen(log_file=log_file)
            log_screen.name = screen_name
            print(f"Created new screen: {screen_name}")
            
            # 将新屏幕添加到屏幕管理器
            app.screen_manager.add_widget(log_screen)
            print(f"Added screen to manager: {screen_name}")
            print(f"Current screens: {app.screen_manager.screen_names}")
            
            # 切换到新屏幕
            app.screen_manager.transition = SlideTransition(direction='left', duration=0.25)
            app.screen_manager.current = screen_name
            print(f"Switched to screen: {screen_name}")
            
            # 手动更新新屏幕的样式
            if hasattr(log_screen, 'log_label'):
                log_screen.log_label.color = app.font_color
            if hasattr(log_screen, 'page_info'):
                log_screen.page_info.color = app.font_color
                
        except Exception as e:
            print(f"Error opening log window: {str(e)}")
            # 显示错误提示
            content = BoxLayout(orientation='vertical', padding='15dp', spacing='10dp')
            error_label = Label(text=f"打开更新日志失败: {str(e)}", font_name='SystemFont', font_size='16sp', 
                              halign='center', color=(1, 0, 0, 1))
            content.add_widget(error_label)
            close_btn = RoundedButton(text='关闭', font_name='SystemFont', size_hint_y=None, height='50dp')
            content.add_widget(close_btn)
            
            popup = Popup(title='错误', content=content, size_hint=(0.8, 0.4),
                         title_font='SystemFont', title_align='center')
            close_btn.bind(on_release=popup.dismiss)
            popup.open()

class SplashScreen(BaseScreen):
    """开屏屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 使用RelativeLayout作为根布局
        self.layout = RelativeLayout()
        
        # 显示开屏图片，设置为背景
        self.splash_image = Image(source=resource_path('sources/backgrounds/startbk.png'), allow_stretch=True, keep_ratio=False)
        self.splash_image.size = self.layout.size
        self.splash_image.pos = self.layout.pos
        self.layout.add_widget(self.splash_image)
        
        # 创建一个专门的按钮布局，确保按钮在最上层
        btn_layout = RelativeLayout()
        
        # 添加跳过按钮，使用黑色半透明效果，减小大小
        self.skip_btn = RoundedButton(text='跳过 5', font_name='SystemFont', size_hint=(None, None), size=('70dp', '25dp'),
                                           pos_hint={'top': 0.95, 'right': 0.95}, alpha=0.5)
        self.skip_btn.color = (0, 0, 0, 1)  # 设置字体颜色为黑色
        self.skip_btn.font_size = '16sp'  # 调整字体大小
        # 手动设置按钮背景为黑色半透明
        with self.skip_btn.canvas.before:
            Color(0, 0, 0, 0.5)  # 黑色半透明
            bg_rect = RoundedRectangle(pos=self.skip_btn.pos, size=self.skip_btn.size, radius=[15,])
        # 绑定按钮位置和大小变化，更新背景
        def update_bg(instance, value):
            bg_rect.pos = instance.pos
            bg_rect.size = instance.size
        self.skip_btn.bind(pos=update_bg, size=update_bg)
        self.skip_btn.bind(on_release=self.skip_splash)
        btn_layout.add_widget(self.skip_btn)
        
        # 将按钮布局添加到主布局，确保在最上层
        self.layout.add_widget(btn_layout)
        
        # 绑定布局大小变化，确保图片始终充满屏幕
        self.layout.bind(size=self._update_splash_image)
        
        self.add_widget(self.layout)
        
        # 倒计时设置
        self.countdown_time = 5
        # 启动倒计时更新
        self.countdown_timer = Clock.schedule_interval(self.update_countdown, 1)
        # 启动计时器，5秒后自动跳转到主界面
        self.timer = Clock.schedule_once(self.go_to_main, 5)
    
    def _update_splash_image(self, instance, value):
        """更新开屏图片大小"""
        self.splash_image.size = value
    
    def update_countdown(self, dt):
        """更新倒计时显示"""
        self.countdown_time -= 1
        if self.countdown_time > 0:
            self.skip_btn.text = f'跳过 {self.countdown_time}'
        else:
            self.skip_btn.text = '跳过'
            Clock.unschedule(self.countdown_timer)
    
    def skip_splash(self, *args):
        """跳过开屏"""
        Clock.unschedule(self.timer)
        Clock.unschedule(self.countdown_timer)
        self.go_to_main()
    
    def go_to_main(self, *args):
        """跳转到主界面"""
        app = App.get_running_app()
        # 显示导航栏并恢复高度
        app.nav_bar.opacity = 1
        app.nav_bar.height = '50dp'  # 恢复导航栏高度
        app.change_screen('main', direction='left')

class LogDetailScreen(BaseScreen):
    """更新日志详情屏幕"""
    def __init__(self, log_file, **kwargs):
        super().__init__(**kwargs)
        self.log_file = log_file
        self.current_page = 0
        self.page_size = 10  # 每页显示10行
        
        self.layout = BoxLayout(orientation='vertical', padding='15dp', spacing='15dp')
        
        # 1. 标题栏
        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text=log_file[:-4], font_name='SystemFont', font_size='22sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        back_btn = RoundedButton(text='返回', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                                pos_hint={'center_y': 0.5, 'x': 0})
        back_btn.bind(on_release=lambda x: App.get_running_app().change_screen('update_log', direction='right'))
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # 2. 日志内容显示区
        self.content_layout = BoxLayout(orientation='vertical', spacing='10dp')
        
        # 日志内容标签
        self.log_label = Label(text='', font_name='SystemFont', font_size='16sp', halign='left', valign='top')
        self.log_label.bind(size=self.log_label.setter('text_size'))
        self.content_layout.add_widget(self.log_label)
        
        # 分页按钮
        self.pagination_layout = BoxLayout(orientation='horizontal', spacing='10dp', size_hint_y=None, height='50dp')
        self.prev_btn = RoundedButton(text='上一页', font_name='SystemFont', size_hint_x=1)
        self.prev_btn.bind(on_release=self.show_prev_page)
        self.prev_btn.disabled = True
        
        self.page_info = Label(text='第 1 页', font_name='SystemFont', font_size='16sp', halign='center', valign='middle')
        
        self.next_btn = RoundedButton(text='下一页', font_name='SystemFont', size_hint_x=1)
        self.next_btn.bind(on_release=self.show_next_page)
        
        self.pagination_layout.add_widget(self.prev_btn)
        self.pagination_layout.add_widget(self.page_info)
        self.pagination_layout.add_widget(self.next_btn)
        
        self.content_layout.add_widget(self.pagination_layout)
        
        self.layout.add_widget(self.content_layout)
        
        self.add_widget(self.layout)
        
        # 加载日志内容
        self.load_log_content()

    def load_log_content(self):
        """加载指定的更新日志内容"""
        # 读取更新日志文件
        log_path = resource_path(f'sources/logs/{self.log_file}')
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                self.log_content = f.read()
            
            # 分割内容为行
            self.log_lines = self.log_content.split('\n')
            # 计算总页数
            self.total_pages = (len(self.log_lines) + self.page_size - 1) // self.page_size
            
            # 显示第一页
            self.show_page(0)
            
            # 更新按钮状态
            self.update_pagination_buttons()
        except Exception as e:
            self.log_label.text = f"无法加载更新日志: {str(e)}"
            self.prev_btn.disabled = True
            self.next_btn.disabled = True

    def show_page(self, page):
        """显示指定页码的内容"""
        if not hasattr(self, 'log_lines'):
            return
        
        start = page * self.page_size
        end = start + self.page_size
        page_content = '\n'.join(self.log_lines[start:end])
        
        self.log_label.text = page_content
        self.current_page = page
        self.page_info.text = f'第 {page + 1} 页 / 共 {self.total_pages} 页'

    def show_prev_page(self, *args):
        """显示上一页"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
            self.update_pagination_buttons()

    def show_next_page(self, *args):
        """显示下一页"""
        if hasattr(self, 'total_pages') and self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)
            self.update_pagination_buttons()

    def update_pagination_buttons(self):
        """更新分页按钮状态"""
        if not hasattr(self, 'total_pages'):
            return
        
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == self.total_pages - 1

class SettingsScreen(BaseScreen):
    """“设置”屏幕"""
    pass

class GardenBabyApp(App):
    background_image = StringProperty('')
    background_alpha = NumericProperty(1.0)
    font_color = ListProperty([0, 0, 0, 1])
    username = StringProperty('小英雄')
    avatar_path = StringProperty('')
    poems = ListProperty([])
    tasks = ListProperty([])
    completed_tasks = ListProperty([])
    active_task_id = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 JsonStore，将数据文件存储在用户的应用数据目录中
        import os
        import getpass
        # 获取用户的应用数据目录
        app_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'GardenBaby')
        # 创建目录（如果不存在）
        os.makedirs(app_data_dir, exist_ok=True)
        # 构建数据文件路径
        self.data_file = os.path.join(app_data_dir, 'user_data.json')
        self.store = JsonStore(self.data_file)
        
        # 设置默认值（确保 resource_path 在正确的工作目录下调用）
        default_avatar = resource_path('sources/avatars/head0.png')
        default_background = resource_path('sources/backgrounds/bk0.jpg')
        
        # 加载存储的数据
        if self.store.exists('profile'):
            profile = self.store.get('profile')
            self.username = profile.get('username', '小英雄')
            # 处理存储的头像路径（可能是相对路径）
            stored_avatar = profile.get('avatar_path', default_avatar)
            if stored_avatar.startswith('sources/'):
                self.avatar_path = resource_path(stored_avatar)
            else:
                self.avatar_path = stored_avatar
        else:
            # 首次打开，设置默认头像
            self.avatar_path = default_avatar
        
        # 加载存储的设置
        if self.store.exists('settings'):
            settings = self.store.get('settings')
            # 处理存储的背景路径（可能是相对路径）
            stored_background = settings.get('background_image', default_background)
            if stored_background.startswith('sources/'):
                self.background_image = resource_path(stored_background)
            else:
                self.background_image = stored_background
            self.background_alpha = settings.get('background_alpha', 1.0)
            self.font_color = settings.get('font_color', [0, 0, 0, 1])
        else:
            # 首次打开，设置默认背景
            self.background_image = default_background
        
        # 加载存储的任务
        if self.store.exists('task_data'):
            task_data = self.store.get('task_data')
            self.tasks = task_data.get('tasks', [])
            self.completed_tasks = task_data.get('completed_tasks', [])
            self.active_task_id = task_data.get('active_task_id', '')
        
        # 加载古诗词
        self.load_poems()

    def save_settings(self, *args):
        """保存设置到 JsonStore"""
        # 保存相对路径而不是绝对路径
        import os
        # 提取相对路径
        if 'sources/' in self.background_image:
            rel_background = self.background_image.split('sources/', 1)[1]
            rel_background = 'sources/' + rel_background
        else:
            rel_background = self.background_image
        
        self.store.put('settings', 
                      background_image=rel_background,
                      background_alpha=self.background_alpha,
                      font_color=self.font_color)

    def save_task_data(self, *args):
        """保存任务数据到 JsonStore"""
        self.store.put('task_data',
                      tasks=list(self.tasks),
                      completed_tasks=list(self.completed_tasks),
                      active_task_id=self.active_task_id)

    def load_poems(self):
        """从 sources/data/text.txt 加载古诗词"""
        try:
            import os
            path = resource_path('sources/data/text.txt')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.poems = [line.strip() for line in f.readlines() if line.strip()]
            
            # 如果文件为空或不存在，提供一些默认诗句
            if not self.poems:
                self.poems = ["床前明月光，疑是地上霜。", "欲穷千里目，更上一层楼。"]
        except Exception as e:
            print(f"Error loading poems: {e}")
            self.poems = ["床前明月光，疑是地上霜。"]

    def build(self):
        # 注册中文字体
        from kivy.core.text import LabelBase
        LabelBase.register(name='SystemFont', fn_regular=resource_path('sources/fonts/ziti2.ttf'))
        LabelBase.register(name='PoetryFont', fn_regular=resource_path('sources/fonts/ziti1.ttf'))
        
        self.root_layout = BoxLayout(orientation='vertical')
        # 在根布局上添加背景绘制指令
        with self.root_layout.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        # 绑定根布局大小变化以同步背景
        self.root_layout.bind(size=self._update_root_bg, pos=self._update_root_bg)

        self.screen_manager = ScreenManager()

        self.screen_manager.add_widget(SplashScreen(name='splash'))
        self.screen_manager.add_widget(GardenScreen(name='garden'))
        self.screen_manager.add_widget(MainScreen(name='main'))
        self.screen_manager.add_widget(ProfileScreen(name='profile'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(TaskManagementScreen(name='task_mgmt'))
        self.screen_manager.add_widget(EditTaskScreen(name='edit_task'))
        self.screen_manager.add_widget(HistoryScreen(name='history'))
        self.screen_manager.add_widget(UpdateLogScreen(name='update_log'))

        # 先设置默认值
        print(f"DEBUG: build - before setup - background_image = {self.background_image}")
        print(f"DEBUG: build - before setup - avatar_path = {self.avatar_path}")
        
        self.setup_profile_screen()
        self.setup_settings_screen()
        self.nav_bar = self.setup_nav_bar()
        self.nav_bar.opacity = 0  # 初始隐藏导航栏
        self.nav_bar.height = 0  # 初始设置导航栏高度为0

        self.root_layout.add_widget(self.screen_manager)
        self.root_layout.add_widget(self.nav_bar)

        self.bind(background_image=self.update_styles, 
                    background_alpha=self.update_styles, 
                    font_color=self.update_styles)
        
        # 绑定设置变化时自动保存
        self.bind(background_image=self.save_settings,
                  background_alpha=self.save_settings,
                  font_color=self.save_settings)
        
        # 强制更新样式
        print(f"DEBUG: build - before update_styles - background_image = {self.background_image}")
        self.update_styles()
        
        self.screen_manager.current = 'splash'
        return self.root_layout

    def _update_root_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def setup_profile_screen(self):
        screen = self.screen_manager.get_screen('profile')
        screen.clear_widgets() # 清空旧组件
        
        layout = RelativeLayout()
        
        # 1. 右上角设置按钮
        settings_button = RoundedButton(text='设置', font_name='SystemFont', size_hint=(None, None), size=('100dp', '50dp'), 
                                  pos_hint={'top': 1, 'right': 1})
        settings_button.bind(on_press=lambda x: self.change_screen('settings', direction='left'))
        layout.add_widget(settings_button)
        
        # 2. 中间区域 (头像 + 用户名) - 上移位置
        center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=('200dp', '230dp'), 
                                 pos_hint={'center_x': 0.5, 'top': 0.9}, spacing='5dp')
        
        # 头像组件
        self.avatar_image = ImageButton(source=self.avatar_path, size_hint=(None, None), size=('130dp', '130dp'),
                                       pos_hint={'center_x': 0.5})
        self.avatar_image.bind(on_release=self.open_avatar_popup)
        center_layout.add_widget(self.avatar_image)
        
        # 用户名组件
        self.username_label = Button(text=self.username, font_name='SystemFont', font_size='22sp', size_hint=(1, None), height='40dp',
                                    background_normal='', background_color=(0,0,0,0), color=self.font_color)
        self.username_label.bind(on_release=self.open_username_popup)
        center_layout.add_widget(self.username_label)
        
        layout.add_widget(center_layout)

        # 3. 任务管理入口
        task_mgmt_btn = RoundedButton(text='任务管理', font_name='SystemFont', font_size='20sp',
                                     size_hint=(0.8, None), height='60dp',
                                     pos_hint={'center_x': 0.5, 'top': 0.4})
        task_mgmt_btn.bind(on_release=lambda x: self.change_screen('task_mgmt', direction='left'))
        layout.add_widget(task_mgmt_btn)
        
        # 4. 更新日志按钮
        update_log_btn = RoundedButton(text='更新日志', font_name='SystemFont', font_size='20sp',
                                     size_hint=(0.8, None), height='60dp',
                                     pos_hint={'center_x': 0.5, 'top': 0.3})
        update_log_btn.bind(on_release=lambda x: self.change_screen('update_log', direction='left'))
        layout.add_widget(update_log_btn)
        
        screen.add_widget(layout)

    def open_avatar_popup(self, instance):
        """打开头像选择弹窗"""
        content = GridLayout(cols=2, padding='10dp', spacing='10dp')
        avatars = ['head0.png', 'head1.png', 'head2.png', 'head3.png']
        
        popup = Popup(title='选择头像', content=content, size_hint=(None, None), size=('320dp', '350dp'),
                     title_font='SystemFont', title_align='center')

        for avatar in avatars:
            path = resource_path(f'sources/avatars/{avatar}')
            # 使用 ImageButton 保持比例
            btn = ImageButton(source=path, size_hint=(1, 1))
            btn.bind(on_release=lambda btn, p=path: self.save_profile(avatar_path=p, popup=popup))
            content.add_widget(btn)
        
        popup.open()

    def open_username_popup(self, instance):
        """打开用户名修改弹窗"""
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        # 关键：TextInput 必须指定支持中文的字体
        text_input = TextInput(text=self.username, multiline=False, font_name='SystemFont', 
                              font_size='20sp', size_hint_y=None, height='50dp')
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
        save_btn = RoundedButton(text='保存', font_name='SystemFont')
        cancel_btn = RoundedButton(text='取消', font_name='SystemFont')
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(text_input)
        content.add_widget(btn_layout)
        
        popup = Popup(title='修改用户名', content=content, size_hint=(None, None), size=('300dp', '200dp'),
                     title_font='SystemFont', title_align='center', auto_dismiss=True)
        
        save_btn.bind(on_release=lambda x: self.save_profile(username=text_input.text, popup=popup))
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()

    def save_profile(self, username=None, avatar_path=None, dropdown=None, popup=None):
        """保存个人信息并实现数据持久化"""
        if username is not None:
            self.username = username
            self.username_label.text = username
        if avatar_path is not None:
            self.avatar_path = avatar_path
            self.avatar_image.source = avatar_path
            
        # 数据持久化 - 保存相对路径
        import os
        if 'sources/' in self.avatar_path:
            rel_avatar = self.avatar_path.split('sources/', 1)[1]
            rel_avatar = 'sources/' + rel_avatar
        else:
            rel_avatar = self.avatar_path
        
        self.store.put('profile', username=self.username, avatar_path=rel_avatar)
        
        # 关闭弹窗或下拉菜单
        if dropdown:
            dropdown.dismiss()
        if popup:
            popup.dismiss()

    def setup_settings_screen(self):
        screen = self.screen_manager.get_screen('settings')
        screen.clear_widgets() # 清空旧组件，确保每次都重新构建
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        header = RelativeLayout(size_hint_y=None, height='50dp')
        header.add_widget(Label(text='设置', font_name='SystemFont', font_size='24sp', pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        back_button = RoundedButton(text='返回', font_name='SystemFont', size_hint=(None, None), size=('80dp', '40dp'), 
                             pos_hint={'center_y': 0.5, 'x': 0})
        back_button.bind(on_press=lambda x: self.change_screen('profile', direction='right'))
        header.add_widget(back_button)
        main_layout.add_widget(header)

        # Background Image Dropdown
        bg_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        bg_layout.add_widget(Label(text='背景图片', font_name='SystemFont'))
        
        dropdown = DropDown()
        bg_options = {
            '默认背景': resource_path('sources/backgrounds/bk0.jpg'),
            '背景一': resource_path('sources/backgrounds/bk1.jpg'),
            '背景二': resource_path('sources/backgrounds/bk2.jpg'),
            '背景三': resource_path('sources/backgrounds/bk3.jpg'),
            '背景四': resource_path('sources/backgrounds/bk4.jpg'),
            '背景五': resource_path('sources/backgrounds/bk5.jpg'),
            '背景六': resource_path('sources/backgrounds/bk6.jpg'),
            '背景七': resource_path('sources/backgrounds/bk7.jpg'),
            '背景八': resource_path('sources/backgrounds/bk8.jpg')
        }
        for name, path in bg_options.items():
            btn = RoundedButton(text=name, size_hint_y=None, height=44, font_name='SystemFont')
            btn.bind(on_release=lambda btn, p=path: self.set_background(p, dropdown))
            dropdown.add_widget(btn)

        main_button = RoundedButton(text='选择背景', font_name='SystemFont')
        main_button.bind(on_release=dropdown.open)
        bg_layout.add_widget(main_button)
        main_layout.add_widget(bg_layout)

        # Background Alpha
        alpha_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        alpha_layout.add_widget(Label(text='背景透明度', font_name='SystemFont'))
        alpha_slider = Slider(min=0, max=1, value=self.background_alpha)
        alpha_slider.bind(value=lambda instance, value: setattr(self, 'background_alpha', value))
        alpha_layout.add_widget(alpha_slider)
        main_layout.add_widget(alpha_layout)

        # Font Color
        font_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        font_layout.add_widget(Label(text='黑色字体', font_name='SystemFont'))
        # 根据当前 font_color 设置 Switch 的初始状态
        is_black = self.font_color == [0, 0, 0, 1]
        font_switch = Switch(active=is_black)
        font_switch.bind(active=lambda instance, value: setattr(self, 'font_color', [0,0,0,1] if value else [1,1,1,1]))
        font_layout.add_widget(font_switch)
        main_layout.add_widget(font_layout)

        main_layout.add_widget(Label()) # Spacer
        screen.add_widget(main_layout)

    def setup_nav_bar(self):
        nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        # 设置导航栏背景为透明
        nav_bar.background_color = (0, 0, 0, 0)
        buttons = {'garden': '花园', 'main': '主界面', 'profile': '我的'}
        for name, text in buttons.items():
            button = RoundedButton(text=text, font_name='SystemFont', alpha=0.3)
            button.bind(on_press=lambda x, screen_name=name: self.change_screen(screen_name, duration=0))
            nav_bar.add_widget(button)
        return nav_bar

    def change_screen(self, screen_name, direction='left', duration=0.25):
        # 切换到“设置”界面时，强制刷新重建，确保状态正确
        if screen_name == 'settings':
            self.setup_settings_screen()

        self.screen_manager.transition = SlideTransition(direction=direction, duration=duration)
        self.screen_manager.current = screen_name
        # 切换屏幕后立即更新背景显示状态
        self.update_styles()

    def set_background(self, path, dropdown):
        self.background_image = path
        dropdown.dismiss()

    def update_styles(self, *args):
        # 1. 更新根布局背景图和透明度
        # 花园界面使用固定背景 bk9.jpg
        current_screen = self.screen_manager.current
        if current_screen == 'garden':
            garden_bg = resource_path('sources/backgrounds/bk9.jpg')
            print(f"DEBUG: update_styles - garden background = {garden_bg}")
            print(f"DEBUG: update_styles - os.path.exists(garden_bg) = {os.path.exists(garden_bg)}")
            self.bg_rect.source = garden_bg
            self.bg_color.a = 1.0  # 花园背景不透明
        else:
            # 其他界面使用用户选择的背景
            print(f"DEBUG: update_styles - background_image = {self.background_image}")
            print(f"DEBUG: update_styles - os.path.exists(background_image) = {os.path.exists(self.background_image)}")
            self.bg_rect.source = self.background_image
            self.bg_color.a = self.background_alpha

        # 2. 更新所有界面的字体颜色
        for screen in self.screen_manager.screens:
            try:
                for widget in screen.walk():
                    # 统一更新 Label 和 模拟 Label 的 Button
                    # 特殊处理：主界面的古诗词 Label 虽然在 Button 内部，但也需要更新颜色
                    is_poetry_label = hasattr(screen, 'poetry_upper') and (widget == screen.poetry_upper or widget == screen.poetry_lower)
                    # 特殊处理：主界面的步骤 Label
                    is_step_label = hasattr(screen, 'steps_layout') and widget.parent and widget.parent.parent == screen.steps_layout
                    
                    if isinstance(widget, Label) or (isinstance(widget, Button) and widget.background_color == [0,0,0,0]):
                        if not isinstance(widget.parent, Button) or (isinstance(widget, Button) and widget.background_color == [0,0,0,0]) or is_poetry_label or is_step_label:
                            widget.color = self.font_color
            except Exception as e:
                print(f"Error updating styles for screen {screen.name}: {str(e)}")
        
        # 3. 更新头像图片
        if hasattr(self, 'avatar_image'):
            try:
                print(f"DEBUG: update_styles - avatar_path = {self.avatar_path}")
                print(f"DEBUG: update_styles - os.path.exists(avatar_path) = {os.path.exists(self.avatar_path)}")
                self.avatar_image.source = self.avatar_path
            except Exception as e:
                print(f"Error updating avatar: {str(e)}")


if __name__ == '__main__':
    GardenBabyApp().run()

