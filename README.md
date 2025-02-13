# AI Chat Launcher

一个简单的本地大语言模型聊天界面程序，支持自定义系统提示词和思考过程显示。

## 环境要求
python >= 3.8

torch >= 2.0.0

transformers >= 4.36.0

tkinter (Python自带)

numpy >= 1.24.0

accelerate >= 0.25.0

safetensors >= 0.4.0


## 快速开始

1. 安装依赖
- pip install -r requirements.txt(codes里面有)

2. 准备模型
- 在程序根目录创建`models`文件夹
- 将支持transformers库的模型放入`models`文件夹的子目录中

3. 启动程序
- python launcher.py


## 使用说明

### 模型选择
- 程序启动时会自动扫描`models`文件夹
- 从下拉菜单中选择要使用的模型
- 点击确认按钮加载模型

### 聊天界面
- 在底部输入框输入消息
- 按回车键或点击发送按钮发送消息
- 使用清空历史按钮重置对话
- 点击设置按钮自定义系统提示词

### 思考过程显示
- 如果模型支持，会显示AI的思考过程
- 可通过[+]/[-]按钮展开/折叠思考过程
- 思考过程使用灰色字体显示

### 系统提示词
- 点击设置按钮打开设置窗口
- 在文本框中编辑系统提示词
- 点击保存设置按钮应用更改
- 修改提示词会自动清空当前对话历史

## 常见问题

1. 找不到可用模型
   - 检查`models`文件夹是否存在
   - 确保模型文件结构完整
   - 模型需要支持transformers库

2. 显存不足
   - 尝试使用更小的模型
   - 关闭其他占用显存的程序
   - 检查是否有多个程序实例在运行

3. 程序无响应
   - 等待模型加载完成
   - 检查显卡驱动是否正常
   - 查看程序错误输出

如有问题或建议，欢迎提交Issue或Pull Request。如果你不想这么麻烦，这里有一键启动程序链接：https://pan.xunlei.com/s/VOIz9_SCeCAI3TS-k7FUBPMeA1?pwd=ugvx#

