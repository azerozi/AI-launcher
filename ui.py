import tkinter as tk
from tkinter import scrolledtext, ttk
from ai_controller import AIController
import os
import sys

class ModelSelector:
    def __init__(self, parent):
        self.selected_model = None
        
        # 创建选择窗口，使用 Toplevel
        self.window = tk.Toplevel(parent)
        self.window.title("选择模型")
        self.window.geometry("600x250")
        
        # 获取可用模型列表
        self.models = AIController.get_available_models()
        
        if not self.models:
            tk.Label(self.window, text="未找到可用模型！\n请确保模型文件已放置在models文件夹中。").pack(pady=20)
            tk.Button(self.window, text="退出", command=self.on_exit).pack()
        else:
            tk.Label(self.window, text="请选择要使用的模型：").pack(pady=10)
            
            # 创建下拉选择框，设置宽度
            self.model_var = tk.StringVar()
            self.model_selector = ttk.Combobox(
                self.window, 
                textvariable=self.model_var,
                values=self.models,
                state="readonly",
                width=50
            )
            self.model_selector.pack(pady=10)
            self.model_selector.set(self.models[0])
            
            # 确认按钮
            tk.Button(self.window, text="确认", command=self.confirm).pack(pady=10)
    
    def confirm(self):
        self.selected_model = os.path.join("models", self.model_var.get())
        self.window.destroy()
    
    def on_exit(self):
        """处理退出事件"""
        try:
            self.window.destroy()  # 销毁当前窗口
            self.window.master.destroy()  # 销毁父窗口
            sys.exit(0)  # 确保程序完全退出
        except Exception as e:
            print(f"退出时出错：{str(e)}")
            sys.exit(1)
    
    def run(self):
        self.window.grab_set()  # 模态窗口
        self.window.wait_window()  # 等待窗口关闭
        return self.selected_model

class SettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent.root)  # 使用 parent.root 作为父窗口
        self.window.title("设置")
        self.window.geometry("600x400")
        
        # 保存父窗口引用
        self.parent = parent
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 提示词设置选项卡
        self.prompt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.prompt_frame, text='提示词设置')
        
        # 提示词输入区域
        tk.Label(self.prompt_frame, text="系统提示词：", font=("Microsoft YaHei UI", 10)).pack(pady=5)
        self.prompt_text = scrolledtext.ScrolledText(
            self.prompt_frame, 
            height=10,
            font=("Microsoft YaHei UI", 10),
            bg="white",
            fg="black"
        )
        self.prompt_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 加载当前设置到输入框
        current_prompt = self.parent.settings.get('system_prompt', "你是一个有用的助手。")
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', current_prompt)
        
        # 保存按钮
        tk.Button(
            self.prompt_frame, 
            text="保存设置", 
            command=self.save_and_close,
            font=("Microsoft YaHei UI", 10),
            bg="#e8e8e8",
            fg="black"
        ).pack(pady=10)
    
    def save_and_close(self):
        """保存设置并关闭窗口"""
        # 获取当前输入的提示词
        prompt = self.prompt_text.get('1.0', tk.END).strip()
        
        # 更新父窗口的设置
        if hasattr(self.parent, 'settings'):
            self.parent.settings['system_prompt'] = prompt
            # 清空历史记录，因为提示词改变了
            self.parent.clear_history()
        
        # 关闭窗口
        self.window.destroy()

class ChatWindow:
    def __init__(self, parent, ai_controller):
        self.root = tk.Toplevel(parent)
        model_name = os.path.basename(ai_controller.model_path)
        self.root.title(f"AI启动器 - {model_name}")
        self.root.geometry("800x600")
        self.root.deiconify()
        
        # 添加窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 保存父窗口引用
        self.parent = parent
        
        # 保存 AI 控制器
        self.ai = ai_controller
        
        # 初始化思考过程相关的变量
        self.thought_count = 0
        self.thought_visibility = {}
        
        # 初始化设置
        self.settings = {
            'system_prompt': "你是一个有用的助手。"
        }
        
        # 设置窗口样式
        self.root.configure(bg="white")
        
        # 创建主框架，使用pack布局
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 聊天历史显示区域
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 11),
            bg="white",
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=10,
            state='disabled',
            cursor='arrow'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置文本标签样式
        self.setup_text_tags()
        
        # 底部输入区域框架
        bottom_frame = tk.Frame(main_frame, bg="white")
        bottom_frame.pack(fill=tk.X, pady=5)
        
        # 输入框
        self.input_box = tk.Entry(
            bottom_frame,
            font=("Microsoft YaHei UI", 11),
            relief=tk.SOLID,
            borderwidth=1,
            bg="white"
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # 创建按钮
        self.create_buttons(bottom_frame)
        
        # 绑定事件
        self.bind_events()
        
        # 在初始化时清空一次历史记录
        self.clear_history()
        
        # 确保窗口显示在最前面
        self.root.lift()
        self.root.focus_force()
    
    def setup_text_tags(self):
        """配置文本标签样式"""
        self.chat_display.tag_configure("user", font=("Microsoft YaHei UI", 11, "bold"), spacing1=10, spacing3=5)
        self.chat_display.tag_configure("thought", font=("Microsoft YaHei UI", 10), foreground="#666666", spacing1=2, spacing3=2)
        self.chat_display.tag_configure("response", font=("Microsoft YaHei UI", 11), foreground="#000000", spacing1=5, spacing3=5)
        self.chat_display.tag_configure("toggle_button", font=("Microsoft YaHei UI", 9), foreground="#1a73e8", underline=True, spacing1=5, spacing3=2)
        self.chat_display.tag_configure("error", font=("Microsoft YaHei UI", 10), foreground="#dc3545")
    
    def create_buttons(self, bottom_frame):
        """创建按钮"""
        button_style = {
            "font": ("Microsoft YaHei UI", 10),
            "relief": tk.RAISED,
            "borderwidth": 1,
            "bg": "#e8e8e8",
            "fg": "#000000",
            "padx": 10,
            "pady": 3,
            "cursor": "hand2"
        }
        
        buttons_frame = tk.Frame(bottom_frame, bg="white")
        buttons_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.send_button = tk.Button(buttons_frame, text="发送", command=self.send_message, **button_style)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        self.clear_button = tk.Button(buttons_frame, text="清空历史", command=self.clear_history, **button_style)
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        self.settings_button = tk.Button(buttons_frame, text="设置", command=self.open_settings, **button_style)
        self.settings_button.pack(side=tk.RIGHT, padx=5)
    
    def bind_events(self):
        """绑定事件"""
        self.input_box.bind("<Return>", lambda e: self.send_message())
        self.chat_display.tag_bind("toggle_button", "<Button-1>", self.handle_toggle_click)
    
    def send_message(self):
        """发送消息"""
        user_input = self.input_box.get()
        if not user_input.strip():
            return
            
        # 显示用户输入
        self.insert_text("\n你: ", "user")
        self.insert_text(f"{user_input}\n", "user")
        self.input_box.delete(0, tk.END)
        
        # 获取AI响应
        try:
            thought, response = self.ai.chat(user_input, system_prompt=self.settings['system_prompt'])
            
            # 如果有思考过程且模型支持思考过程输出，创建一个可点击的标签来切换显示
            if thought and self.ai.supports_thinking:
                thought_id = self.thought_count
                self.thought_count += 1
                self.thought_visibility[thought_id] = True
                
                # 添加思考过程的折叠按钮（单独一行）
                self.insert_text("[−] 隐藏思考过程", ("toggle_button", f"thought_toggle_{thought_id}"))
                
                # 添加思考过程文本（使用单独的标签）
                self.insert_text("\n", ("thought", f"thought_content_{thought_id}"))
                self.insert_text(f"{thought}", ("thought", f"thought_{thought_id}", f"thought_content_{thought_id}"))
                
                # 显示正式回复（新的一行）
                self.insert_text("\nAI: ", "response")
                self.insert_text(f"{response}\n\n", "response")
            else:
                # 如果没有思考过程或模型不支持，直接显示回复
                self.insert_text("AI: ", "response")
                self.insert_text(f"{response}\n\n", "response")
            
        except Exception as e:
            self.insert_text(f"错误: {str(e)}\n\n", "error")
            
        # 自动滚动到底部
        self.chat_display.see(tk.END)
    
    def clear_history(self):
        """清空聊天历史"""
        self.ai.clear_history()
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.insert_text("已清空聊天历史\n\n")
        self.chat_display.config(state='disabled')
    
    def open_settings(self):
        """打开设置窗口"""
        settings_window = SettingsWindow(self)  # 传递 self 作为父窗口
        self.root.wait_window(settings_window.window)
    
    def insert_text(self, text, tag=None):
        """安全地插入文本的辅助方法"""
        self.chat_display.config(state='normal')  # 临时启用编辑
        if tag:
            self.chat_display.insert(tk.END, text, tag)
        else:
            self.chat_display.insert(tk.END, text)
        self.chat_display.config(state='disabled')  # 恢复禁用状态
    
    def toggle_thought(self, thought_id):
        """切换思考过程的显示状态"""
        if thought_id not in self.thought_visibility:
            return
        
        current_state = self.thought_visibility[thought_id]
        
        try:
            # 获取思考过程内容的标签
            content_tag = f"thought_content_{thought_id}"
            
            if current_state:
                # 隐藏思考过程（通过elide属性）
                self.chat_display.tag_configure(content_tag, elide=True)
                # 更新按钮文本
                button_start = self.chat_display.index(f"thought_toggle_{thought_id}.first")
                button_end = self.chat_display.index(f"thought_toggle_{thought_id}.last")
                self.chat_display.delete(button_start, button_end)
                self.chat_display.insert(button_start, "[+] 显示思考过程", 
                                      ("toggle_button", f"thought_toggle_{thought_id}"))
            else:
                # 显示思考过程
                self.chat_display.tag_configure(content_tag, elide=False)
                # 更新按钮文本
                button_start = self.chat_display.index(f"thought_toggle_{thought_id}.first")
                button_end = self.chat_display.index(f"thought_toggle_{thought_id}.last")
                self.chat_display.delete(button_start, button_end)
                self.chat_display.insert(button_start, "[−] 隐藏思考过程", 
                                      ("toggle_button", f"thought_toggle_{thought_id}"))
            
            self.thought_visibility[thought_id] = not current_state
        except Exception as e:
            print(f"Toggle error: {str(e)}")
    
    def handle_toggle_click(self, event):
        """处理折叠按钮的点击事件"""
        try:
            # 获取点击位置
            index = self.chat_display.index(f"@{event.x},{event.y}")
            
            # 查找点击位置的标签
            tags = self.chat_display.tag_names(index)
            for tag in tags:
                if tag.startswith("thought_toggle_"):
                    thought_id = int(tag.split("_")[-1])
                    self.toggle_thought(thought_id)
                    break
        except Exception as e:
            print(f"Click handler error: {str(e)}")  # 添加错误日志
    
    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            self.root.destroy()  # 销毁聊天窗口
            self.parent.destroy()  # 销毁父窗口
            sys.exit(0)  # 确保程序完全退出
        except Exception as e:
            print(f"关闭窗口时出错：{str(e)}")
            sys.exit(1)  # 如果出错也要确保退出

def run():
    """启动主程序"""
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口
    
    # 首先选择模型
    model_selector = ModelSelector(root)
    selected_model = model_selector.run()
    
    if selected_model:
        try:
            # 创建 AI 控制器
            ai = AIController(selected_model)
            # 创建并显示聊天窗口
            chat_window = ChatWindow(root, ai)
            # 确保主循环运行
            root.mainloop()
        except Exception as e:
            print(f"错误：{str(e)}")  # 添加错误输出以便调试
    else:
        root.quit()

if __name__ == "__main__":
    run() 