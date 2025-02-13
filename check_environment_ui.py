import tkinter as tk
from tkinter import ttk, messagebox
from environment_checker import EnvironmentManager
import os
import sys

class EnvironmentCheckerUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AI聊天 - 环境检查")
        self.window.geometry("600x700")  # 增加窗口高度
        self.window.resizable(False, False)  # 禁止调整窗口大小
        
        # 设置窗口图标
        if os.path.exists('icon.ico'):
            self.window.iconbitmap('icon.ico')
            
        # 使窗口居中
        self.center_window()
        
        # 标记窗口状态
        self.is_running = True
        
        # 创建环境管理器
        self.env_manager = EnvironmentManager()
        
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(
            main_frame, 
            text="AI聊天环境检查", 
            font=("Microsoft YaHei UI", 14, "bold")
        ).pack(pady=(0, 20))
        
        # 创建日志文本框和滚动条
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            height=25,  # 增加文本框高度
            width=60,
            font=("Microsoft YaHei UI", 10),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state='disabled'  # 设置为只读
        )
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置文本标签颜色
        self.log_text.tag_configure("black", foreground="black")
        self.log_text.tag_configure("green", foreground="green")
        self.log_text.tag_configure("orange", foreground="orange")
        self.log_text.tag_configure("red", foreground="red")
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备开始检查...")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 10)
        )
        self.status_label.pack(pady=5)
        
        # 按钮框架
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(pady=10)
        
        # 开始检查按钮
        self.check_button = ttk.Button(
            self.button_frame,
            text="开始检查",
            command=self.start_check,
            width=15
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        # 安装依赖按钮
        self.install_button = ttk.Button(
            self.button_frame,
            text="安装缺失依赖",
            command=self.install_dependencies,
            width=15,
            state='disabled'  # 初始状态设为禁用
        )
        # 初始就将按钮放置，但设为禁用状态
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_button = ttk.Button(
            self.button_frame,
            text="退出",
            command=self.on_closing,
            width=15
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        self.complete_callback = None
        self.all_checks_passed = False
        
    def log(self, message, level="info"):
        """添加日志到文本框"""
        if not self.is_running:
            return
            
        try:
            tag = {
                "info": "black",
                "success": "green",
                "warning": "orange",
                "error": "red",
                "bold": "bold"
            }.get(level, "black")
            
            # 临时启用文本框以插入文本
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, message + "\n", tag)
            self.log_text.see(tk.END)
            # 插入后重新设为只读
            self.log_text.config(state='disabled')
            self.window.update()
        except Exception:
            pass
        
    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def set_complete_callback(self, callback):
        """设置检查完成后的回调函数"""
        self.complete_callback = callback
    
    def start_check(self):
        """开始检查"""
        if not self.is_running:
            return
            
        try:
            self.check_button.config(state='disabled')
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state='disabled')
            
            self.log("欢迎使用AI聊天环境检查工具", "bold")
            self.log("本程序将检查您的系统是否满足运行AI聊天的要求\n", "info")
            
            # 执行检查
            all_passed = True
            
            # 检查 Python 版本
            success, message = self.env_manager.check_python_version()
            self.log(message, "success" if success else "error")
            all_passed = all_passed and success
            
            # 检查 CUDA
            success, message = self.env_manager.check_cuda()
            self.log(message, "success" if success else "warning")
            
            # 检查依赖包
            results = self.env_manager.check_dependencies()
            self.log("\n必需包检查:", "bold")
            for success, message in results:
                self.log(message, "success" if success else "error")
                all_passed = all_passed and success
            
            # 检查可选包
            results = self.env_manager.check_optional_dependencies()
            self.log("\n可选包检查:", "bold")
            for success, message in results:
                self.log(message, "info")
            
            # 检查磁盘空间
            success, message = self.env_manager.check_disk_space()
            self.log(f"\n{message}", "success" if success else "error")
            all_passed = all_passed and success
            
            self.log("\n检查完成！", "bold")
            
            if all_passed:
                self.log("\n所有依赖已满足要求！", "success")
                self.all_checks_passed = True
                self.window.after(1000, self.window.quit)  # 延迟1秒后关闭窗口
            else:
                self.log('\n发现缺失的依赖包，请点击"安装缺失依赖"按钮进行安装', "warning")
                self.all_checks_passed = False
            
            self.check_button.config(state='normal')
            
        except Exception as e:
            self.log(f"\n检查过程出错: {str(e)}", "error")
            self.check_button.config(state='normal')
        
    def install_dependencies(self):
        """安装缺失的依赖"""
        if not self.env_manager.missing_packages:
            self.log("没有需要安装的依赖")
            return
            
        self.install_button.config(state='disabled')
        self.check_button.config(state='disabled')
        
        success, message = self.env_manager.install_dependencies(self.log)
        
        if success:
            self.log("\n依赖安装完成！", "success")
            # 重新检查环境
            self.start_check()
        else:
            self.log(f"\n{message}", "error")
            self.install_button.config(state='normal')
            
        self.check_button.config(state='normal')
        
    def on_closing(self):
        """退出程序"""
        self.is_running = False
        try:
            if messagebox.askokcancel("退出", "确定要退出环境检查吗？"):
                self.window.destroy()
                sys.exit(1)  # 确保程序完全退出
        except Exception:
            self.window.destroy()
            sys.exit(1)  # 如果出错也要确保退出
            
    def run(self):
        """运行环境检查"""
        try:
            self.start_check()
            self.window.mainloop()
            if self.all_checks_passed:
                self.window.destroy()  # 确保窗口被销毁
                return True
            return False
        except Exception as e:
            print(f"环境检查出错：{str(e)}")
            self.window.destroy()
            return False

if __name__ == "__main__":
    checker = EnvironmentCheckerUI()
    checker.run() 