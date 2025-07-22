#!/usr/bin/env python3
"""
Consumer-Grade Accelerometer Example
消费级加速度计示例代码
"""

import sys
import os

# 设置环境变量来避免NumPy 2.0兼容性问题
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from theory.imu_theory import IMUTheoryCalculator, IMUPerformanceParams
from layout.accelerometer_layout import AccelerometerLayoutGenerator
from utils.visualization import LayoutVisualizer

def create_consumer_accelerometer():
    """创建消费级加速度计示例"""
    
    print("=== 消费级加速度计设计示例 ===\n")
    
    # 1. 定义性能参数
    performance_params = IMUPerformanceParams(
        sensitivity=100.0,      # 灵敏度 100 mV/g
        bandwidth=1000.0,       # 带宽 1000 Hz
        noise_density=50.0,     # 噪声密度 50 μg/√Hz
        full_scale_range=10.0,  # 量程 10 g
        resolution=1.0,         # 分辨率 1 mg
        power_consumption=5.0   # 功耗 5 mW
    )
    
    print("性能参数:")
    print(f"  灵敏度: {performance_params.sensitivity} mV/g")
    print(f"  带宽: {performance_params.bandwidth} Hz")
    print(f"  噪声密度: {performance_params.noise_density} μg/√Hz")
    print(f"  量程: {performance_params.full_scale_range} g")
    print(f"  分辨率: {performance_params.resolution} mg")
    print(f"  功耗: {performance_params.power_consumption} mW\n")
    
    # 2. 理论计算
    print("正在进行理论计算...")
    calculator = IMUTheoryCalculator()
    mask_params = calculator.calculate_mask_parameters(performance_params)
    
    print("计算得到的Mask参数:")
    for key, value in mask_params.items():
        print(f"  {key}: {value:.2f} μm")
    
    # 3. 设计验证
    print("\n正在进行设计验证...")
    is_valid, message = calculator.validate_design(mask_params)
    
    if is_valid:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        return
    
    # 4. 生成版图
    print("\n正在生成版图...")
    layout_generator = AccelerometerLayoutGenerator()
    component = layout_generator.generate_accelerometer_layout(mask_params)
    
    # 5. 显示版图预览
    print("\n正在生成版图预览...")
    visualizer = LayoutVisualizer()
    
    # 保存预览图片
    preview_filename = "layout_preview.png"
    visualizer.save_layout_preview(component, preview_filename, 
                                 "消费级加速度计版图预览")
    print(f"✓ 版图预览已保存: {preview_filename}")
    
    # 显示预览图片
    print("正在显示版图预览...")
    try:
        visualizer.show_layout_preview(component, "消费级加速度计版图预览")
        print("✓ 版图预览已显示")
    except Exception as e:
        print(f"⚠ 无法显示预览图片: {e}")
        print("请查看保存的预览图片文件")
    
    # 6. 保存GDS文件
    output_file = "consumer_accelerometer.gds"
    component.write_gds(output_file)
    print(f"✓ GDS文件已保存: {output_file}")
    
    # 7. 计算设计指标
    print("\n=== 设计指标 ===")
    
    # 质量块面积
    proof_mass_area = mask_params["proof_mass_size"] ** 2
    print(f"质量块面积: {proof_mass_area:.0f} μm²")
    
    # 弹簧刚度
    spring_stiffness = 4 * 169e9 * (mask_params["spring_width"] * 50**3 / 12) / mask_params["spring_length"]**3
    print(f"弹簧刚度: {spring_stiffness:.2e} N/m")
    
    # 自然频率
    natural_freq = calculator.calculate_natural_frequency(
        mask_params["proof_mass_size"],
        mask_params["spring_length"],
        mask_params["spring_width"],
        50.0
    )
    print(f"自然频率: {natural_freq:.1f} Hz")
    
    # 吸合电压
    pull_in_voltage = calculator.calculate_pull_in_voltage(
        mask_params["proof_mass_size"],
        mask_params["spring_length"],
        mask_params["spring_width"],
        mask_params["gap"]
    )
    print(f"吸合电压: {pull_in_voltage:.2f} V")
    
    # 阻尼比
    damping_ratio = calculator.calculate_damping_ratio(
        mask_params["proof_mass_size"],
        mask_params["gap"]
    )
    print(f"阻尼比: {damping_ratio:.3f}")
    
    print("\n=== 设计完成 ===")
    print("消费级加速度计设计已完成！")
    print("生成的GDS文件可用于流片制造。")
    print(f"版图预览图片: {preview_filename}")
    print(f"GDS文件: {output_file}")

def main():
    """主函数"""
    try:
        create_consumer_accelerometer()
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 