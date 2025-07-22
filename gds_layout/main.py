#!/usr/bin/env python3
"""
MEMS IMU Mask Layout Design Tool
主程序入口
"""

import sys
import os

# 设置环境变量来避免NumPy 2.0兼容性问题
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("MEMS IMU Mask Layout Design Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MEMS Design Lab")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 