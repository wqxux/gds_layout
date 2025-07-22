"""
Main GUI Window for MEMS IMU Design
主GUI窗口，包含参数输入和GDS生成功能
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QTabWidget, QGroupBox, QGridLayout, QTextEdit, QProgressBar,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from theory.imu_theory import IMUTheoryCalculator, IMUPerformanceParams
from layout.accelerometer_layout import AccelerometerLayoutGenerator

class DesignWorker(QThread):
    """后台设计工作线程"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    design_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, performance_params):
        super().__init__()
        self.performance_params = performance_params
        
    def run(self):
        try:
            self.status_updated.emit("正在计算理论参数...")
            self.progress_updated.emit(20)
            
            # 理论计算
            calculator = IMUTheoryCalculator()
            mask_params = calculator.calculate_mask_parameters(self.performance_params)
            
            self.status_updated.emit("正在验证设计...")
            self.progress_updated.emit(40)
            
            # 设计验证
            is_valid, message = calculator.validate_design(mask_params)
            if not is_valid:
                self.error_occurred.emit(f"设计验证失败: {message}")
                return
            
            self.status_updated.emit("正在生成版图...")
            self.progress_updated.emit(60)
            
            # 生成版图
            layout_generator = AccelerometerLayoutGenerator()
            component = layout_generator.generate_accelerometer_layout(mask_params)
            
            self.status_updated.emit("设计完成")
            self.progress_updated.emit(100)
            
            self.design_completed.emit({
                'mask_params': mask_params,
                'component': component,
                'performance_params': self.performance_params
            })
            
        except Exception as e:
            self.error_occurred.emit(f"设计过程中发生错误: {str(e)}")

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEMS IMU Mask Layout 设计工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化组件
        self.performance_params = None
        self.mask_params = None
        self.component = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧参数输入面板
        left_panel = self.create_parameter_panel()
        main_layout.addWidget(left_panel, 1)
        
        # 右侧结果显示面板
        right_panel = self.create_result_panel()
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
    def create_parameter_panel(self):
        """创建参数输入面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("IMU性能参数输入")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 参数输入组
        param_group = QGroupBox("性能参数")
        param_layout = QGridLayout()
        
        # 灵敏度
        param_layout.addWidget(QLabel("灵敏度 (mV/g):"), 0, 0)
        self.sensitivity_input = QDoubleSpinBox()
        self.sensitivity_input.setRange(0.1, 1000.0)
        self.sensitivity_input.setValue(100.0)
        self.sensitivity_input.setSuffix(" mV/g")
        param_layout.addWidget(self.sensitivity_input, 0, 1)
        
        # 带宽
        param_layout.addWidget(QLabel("带宽 (Hz):"), 1, 0)
        self.bandwidth_input = QDoubleSpinBox()
        self.bandwidth_input.setRange(1.0, 10000.0)
        self.bandwidth_input.setValue(1000.0)
        self.bandwidth_input.setSuffix(" Hz")
        param_layout.addWidget(self.bandwidth_input, 1, 1)
        
        # 噪声密度
        param_layout.addWidget(QLabel("噪声密度 (μg/√Hz):"), 2, 0)
        self.noise_input = QDoubleSpinBox()
        self.noise_input.setRange(0.1, 1000.0)
        self.noise_input.setValue(50.0)
        self.noise_input.setSuffix(" μg/√Hz")
        param_layout.addWidget(self.noise_input, 2, 1)
        
        # 量程
        param_layout.addWidget(QLabel("量程 (g):"), 3, 0)
        self.full_scale_input = QDoubleSpinBox()
        self.full_scale_input.setRange(1.0, 100.0)
        self.full_scale_input.setValue(10.0)
        self.full_scale_input.setSuffix(" g")
        param_layout.addWidget(self.full_scale_input, 3, 1)
        
        # 分辨率
        param_layout.addWidget(QLabel("分辨率 (mg):"), 4, 0)
        self.resolution_input = QDoubleSpinBox()
        self.resolution_input.setRange(0.1, 100.0)
        self.resolution_input.setValue(1.0)
        self.resolution_input.setSuffix(" mg")
        param_layout.addWidget(self.resolution_input, 4, 1)
        
        # 功耗
        param_layout.addWidget(QLabel("功耗 (mW):"), 5, 0)
        self.power_input = QDoubleSpinBox()
        self.power_input.setRange(0.1, 100.0)
        self.power_input.setValue(5.0)
        self.power_input.setSuffix(" mW")
        param_layout.addWidget(self.power_input, 5, 1)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 预设参数组
        preset_group = QGroupBox("预设参数")
        preset_layout = QVBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "消费级加速度计",
            "工业级加速度计", 
            "汽车级加速度计",
            "高精度加速度计"
        ])
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # 设计按钮
        self.design_button = QPushButton("开始设计")
        self.design_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.design_button.clicked.connect(self.start_design)
        layout.addWidget(self.design_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def create_result_panel(self):
        """创建结果显示面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("设计结果")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 参数结果选项卡
        self.params_tab = QWidget()
        self.params_layout = QVBoxLayout()
        self.params_text = QTextEdit()
        self.params_text.setReadOnly(True)
        self.params_layout.addWidget(self.params_text)
        self.params_tab.setLayout(self.params_layout)
        self.tab_widget.addTab(self.params_tab, "计算参数")
        
        # 设计信息选项卡
        self.info_tab = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_layout.addWidget(self.info_text)
        self.info_tab.setLayout(self.info_layout)
        self.tab_widget.addTab(self.info_tab, "设计信息")
        
        layout.addWidget(self.tab_widget)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        
        self.export_gds_button = QPushButton("导出GDS文件")
        self.export_gds_button.setEnabled(False)
        self.export_gds_button.clicked.connect(self.export_gds)
        export_layout.addWidget(self.export_gds_button)
        
        self.export_params_button = QPushButton("导出参数")
        self.export_params_button.setEnabled(False)
        self.export_params_button.clicked.connect(self.export_params)
        export_layout.addWidget(self.export_params_button)
        
        layout.addLayout(export_layout)
        
        panel.setLayout(layout)
        return panel
        
    def load_preset(self, preset_name):
        """加载预设参数"""
        presets = {
            "消费级加速度计": {
                "sensitivity": 100.0,
                "bandwidth": 1000.0,
                "noise_density": 50.0,
                "full_scale_range": 10.0,
                "resolution": 1.0,
                "power_consumption": 5.0
            },
            "工业级加速度计": {
                "sensitivity": 200.0,
                "bandwidth": 500.0,
                "noise_density": 20.0,
                "full_scale_range": 20.0,
                "resolution": 0.5,
                "power_consumption": 10.0
            },
            "汽车级加速度计": {
                "sensitivity": 150.0,
                "bandwidth": 2000.0,
                "noise_density": 30.0,
                "full_scale_range": 50.0,
                "resolution": 2.0,
                "power_consumption": 15.0
            },
            "高精度加速度计": {
                "sensitivity": 500.0,
                "bandwidth": 100.0,
                "noise_density": 5.0,
                "full_scale_range": 5.0,
                "resolution": 0.1,
                "power_consumption": 20.0
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.sensitivity_input.setValue(preset["sensitivity"])
            self.bandwidth_input.setValue(preset["bandwidth"])
            self.noise_input.setValue(preset["noise_density"])
            self.full_scale_input.setValue(preset["full_scale_range"])
            self.resolution_input.setValue(preset["resolution"])
            self.power_input.setValue(preset["power_consumption"])
            
    def get_performance_params(self):
        """获取性能参数"""
        return IMUPerformanceParams(
            sensitivity=self.sensitivity_input.value(),
            bandwidth=self.bandwidth_input.value(),
            noise_density=self.noise_input.value(),
            full_scale_range=self.full_scale_input.value(),
            resolution=self.resolution_input.value(),
            power_consumption=self.power_input.value()
        )
        
    def start_design(self):
        """开始设计"""
        try:
            # 获取参数
            self.performance_params = self.get_performance_params()
            
            # 禁用按钮
            self.design_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 启动工作线程
            self.worker = DesignWorker(self.performance_params)
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.status_updated.connect(self.status_label.setText)
            self.worker.design_completed.connect(self.design_completed)
            self.worker.error_occurred.connect(self.design_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动设计时发生错误: {str(e)}")
            self.design_button.setEnabled(True)
            
    def design_completed(self, result):
        """设计完成"""
        self.mask_params = result['mask_params']
        self.component = result['component']
        
        # 更新显示
        self.update_params_display()
        self.update_info_display()
        
        # 启用导出按钮
        self.export_gds_button.setEnabled(True)
        self.export_params_button.setEnabled(True)
        
        # 恢复按钮
        self.design_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "完成", "设计已完成！")
        
    def design_error(self, error_message):
        """设计错误"""
        QMessageBox.critical(self, "错误", error_message)
        self.design_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def update_params_display(self):
        """更新参数显示"""
        if not self.mask_params:
            return
            
        text = "=== 计算得到的Mask参数 ===\n\n"
        
        for key, value in self.mask_params.items():
            text += f"{key}: {value:.2f} μm\n"
            
        text += "\n=== 性能参数 ===\n\n"
        text += f"灵敏度: {self.performance_params.sensitivity:.2f} mV/g\n"
        text += f"带宽: {self.performance_params.bandwidth:.2f} Hz\n"
        text += f"噪声密度: {self.performance_params.noise_density:.2f} μg/√Hz\n"
        text += f"量程: {self.performance_params.full_scale_range:.2f} g\n"
        text += f"分辨率: {self.performance_params.resolution:.2f} mg\n"
        text += f"功耗: {self.performance_params.power_consumption:.2f} mW\n"
        
        self.params_text.setText(text)
        
    def update_info_display(self):
        """更新设计信息显示"""
        if not self.mask_params:
            return
            
        text = "=== 设计信息 ===\n\n"
        
        # 计算一些设计指标
        proof_mass_area = self.mask_params["proof_mass_size"] ** 2
        spring_stiffness = 4 * 169e9 * (self.mask_params["spring_width"] * 50**3 / 12) / self.mask_params["spring_length"]**3
        
        text += f"质量块面积: {proof_mass_area:.0f} μm²\n"
        text += f"弹簧刚度: {spring_stiffness:.2e} N/m\n"
        text += f"设计类型: 电容式加速度计\n"
        text += f"制造工艺: 表面微加工\n"
        text += f"材料: 单晶硅\n"
        text += f"层数: 20层\n"
        
        text += "\n=== 制造约束 ===\n\n"
        text += "✓ 最小线宽: 2 μm\n"
        text += "✓ 最小间距: 3 μm\n"
        text += "✓ 吸合电压检查通过\n"
        
        self.info_text.setText(text)
        
    def export_gds(self):
        """导出GDS文件"""
        if not self.component:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存GDS文件", "imu_accelerometer.gds", "GDSII Files (*.gds)"
        )
        
        if file_path:
            try:
                self.component.write_gds(file_path)
                QMessageBox.information(self, "成功", f"GDS文件已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存GDS文件时发生错误: {str(e)}")
                
    def export_params(self):
        """导出参数文件"""
        if not self.mask_params:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存参数文件", "imu_params.txt", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=== IMU设计参数 ===\n\n")
                    f.write("性能参数:\n")
                    f.write(f"  灵敏度: {self.performance_params.sensitivity:.2f} mV/g\n")
                    f.write(f"  带宽: {self.performance_params.bandwidth:.2f} Hz\n")
                    f.write(f"  噪声密度: {self.performance_params.noise_density:.2f} μg/√Hz\n")
                    f.write(f"  量程: {self.performance_params.full_scale_range:.2f} g\n")
                    f.write(f"  分辨率: {self.performance_params.resolution:.2f} mg\n")
                    f.write(f"  功耗: {self.performance_params.power_consumption:.2f} mW\n\n")
                    
                    f.write("Mask参数:\n")
                    for key, value in self.mask_params.items():
                        f.write(f"  {key}: {value:.2f} μm\n")
                        
                QMessageBox.information(self, "成功", f"参数文件已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存参数文件时发生错误: {str(e)}") 