import sys
import gdsfactory as gf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

# 1. 定义20种自定义layer
LAYERS = {
    f"layer{i+1}": (i+1, 0) for i in range(20)
}

# 2. 理论计算mask参数（示例，实际请根据IMU理论公式调整）
def calculate_mask_params(sensitivity, bandwidth, noise, full_scale):
    # 这里只是示例公式，实际请用真实的物理/工艺关系
    proof_mass_size = sensitivity * 10 + bandwidth * 0.01
    spring_width = 2 + noise * 0.1
    anchor_size = 5 + full_scale * 0.05
    return {
        "proof_mass_size": proof_mass_size,
        "spring_width": spring_width,
        "anchor_size": anchor_size,
    }

# 3. 版图生成函数
def create_imu_layout(mask_params, layers):
    c = gf.Component("IMU")
    # Proof mass
    c.add_ref(gf.components.rectangle(size=(mask_params["proof_mass_size"], mask_params["proof_mass_size"]),
                                      layer=layers["layer1"]))
    # Four anchors
    anchor = gf.components.rectangle(size=(mask_params["anchor_size"], mask_params["anchor_size"]), layer=layers["layer2"])
    c.add_ref(anchor).move((0, 0))
    c.add_ref(anchor).move((mask_params["proof_mass_size"]-mask_params["anchor_size"], 0))
    c.add_ref(anchor).move((0, mask_params["proof_mass_size"]-mask_params["anchor_size"]))
    c.add_ref(anchor).move((mask_params["proof_mass_size"]-mask_params["anchor_size"],
                            mask_params["proof_mass_size"]-mask_params["anchor_size"]))
    # 四根弹簧
    spring = gf.components.rectangle(size=(mask_params["spring_width"], mask_params["proof_mass_size"]), layer=layers["layer3"])
    c.add_ref(spring).move((-mask_params["spring_width"], 0))
    c.add_ref(spring).move((mask_params["proof_mass_size"], 0))
    # 其它layer示例
    for i in range(4, 21):
        # 在版图外围画一圈不同layer的框，示意layer可自定义
        offset = i * 2
        size = mask_params["proof_mass_size"] + offset * 2
        c.add_ref(gf.components.rectangle(size=(size, size), layer=layers[f"layer{i}"])).move((-offset, -offset))
    return c

# 4. GUI界面
class IMUMaskGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MEMS IMU Mask Layout生成器")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 参数输入
        self.inputs = {}
        for label in ["灵敏度(sensitivity)", "带宽(bandwidth)", "噪声(noise)", "量程(full_scale)"]:
            hlayout = QHBoxLayout()
            lbl = QLabel(label)
            edit = QLineEdit()
            edit.setPlaceholderText("请输入数值")
            hlayout.addWidget(lbl)
            hlayout.addWidget(edit)
            layout.addLayout(hlayout)
            self.inputs[label] = edit

        # 生成按钮
        self.btn = QPushButton("生成GDS文件")
        self.btn.clicked.connect(self.generate_gds)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def generate_gds(self):
        try:
            sensitivity = float(self.inputs["灵敏度(sensitivity)"].text())
            bandwidth = float(self.inputs["带宽(bandwidth)"].text())
            noise = float(self.inputs["噪声(noise)"].text())
            full_scale = float(self.inputs["量程(full_scale)"].text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请确保所有参数均为数字！")
            return

        mask_params = calculate_mask_params(sensitivity, bandwidth, noise, full_scale)
        c = create_imu_layout(mask_params, LAYERS)

        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(self, "保存GDS文件", "imu_mask.gds", "GDSII Files (*.gds)")
        if file_path:
            c.write_gds(file_path)
            QMessageBox.information(self, "成功", f"GDS文件已保存到：\n{file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IMUMaskGUI()
    window.show()
    sys.exit(app.exec_()) 