import sys

def main():
    """主函数"""
    try:
        # 导入主程序
        import ui
        # 启动主程序并保持运行
        ui.run()
        # 程序会在这里等待，直到所有窗口关闭
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 