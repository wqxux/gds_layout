"""
MEMS IMU Theory Calculations
包含完整的IMU器件物理理论推导和参数计算
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class IMUPerformanceParams:
    """IMU性能参数类"""
    sensitivity: float  # 灵敏度 (mV/g)
    bandwidth: float    # 带宽 (Hz)
    noise_density: float  # 噪声密度 (μg/√Hz)
    full_scale_range: float  # 量程 (g)
    resolution: float   # 分辨率 (mg)
    power_consumption: float  # 功耗 (mW)
    
@dataclass
class MaterialProperties:
    """材料属性类"""
    youngs_modulus: float  # 杨氏模量 (GPa)
    density: float         # 密度 (kg/m³)
    poisson_ratio: float   # 泊松比
    thickness: float       # 厚度 (μm)

class IMUTheoryCalculator:
    """IMU理论计算器"""
    
    def __init__(self):
        # 硅材料属性 (单晶硅)
        self.silicon = MaterialProperties(
            youngs_modulus=169.0,  # GPa
            density=2330.0,        # kg/m³
            poisson_ratio=0.28,
            thickness=50.0         # μm
        )
        
        # 空气阻尼系数
        self.air_viscosity = 1.81e-5  # Pa·s
        
    def calculate_natural_frequency(self, proof_mass_size: float, spring_length: float, 
                                  spring_width: float, spring_thickness: float) -> float:
        """
        计算自然频率
        f_n = (1/2π) * √(k/m)
        k = 4 * E * I / L³ (四根弹簧并联)
        """
        # 惯性矩
        I = spring_width * spring_thickness**3 / 12
        
        # 单根弹簧刚度
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length**3
        
        # 总刚度 (四根弹簧)
        k_total = 4 * k_single
        
        # 质量
        mass = self.silicon.density * proof_mass_size**2 * self.silicon.thickness * 1e-6
        
        # 自然频率
        natural_freq = (1 / (2 * np.pi)) * np.sqrt(k_total / mass)
        
        return float(natural_freq)
    
    def calculate_sensitivity(self, proof_mass_size: float, spring_length: float,
                           spring_width: float, gap: float, voltage: float) -> float:
        """
        计算电容式加速度计灵敏度
        S = (ε₀ * A * V) / (d² * k)
        """
        # 电容面积
        area = proof_mass_size**2
        
        # 真空介电常数
        epsilon_0 = 8.85e-12  # F/m
        
        # 弹簧刚度
        I = spring_width * self.silicon.thickness**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length**3
        k_total = 4 * k_single
        
        # 灵敏度 (V/g)
        sensitivity = (epsilon_0 * area * voltage) / (gap**2 * k_total)
        
        return float(sensitivity * 1000)  # 转换为 mV/g
    
    def calculate_noise(self, proof_mass_size: float, spring_length: float,
                       spring_width: float, gap: float, temperature: float = 300) -> float:
        """
        计算热机械噪声
        S_x² = (4 * k_B * T * Q) / (m * ω₀³)
        """
        # 玻尔兹曼常数
        k_b = 1.38e-23  # J/K
        
        # 自然频率
        natural_freq = self.calculate_natural_frequency(proof_mass_size, spring_length, 
                                                      spring_width, self.silicon.thickness)
        omega_0 = 2 * np.pi * natural_freq
        
        # 质量
        mass = self.silicon.density * proof_mass_size**2 * self.silicon.thickness * 1e-6
        
        # 品质因子 (估算)
        Q = 100  # 典型值
        
        # 热机械噪声
        noise_density = np.sqrt((4 * k_b * temperature * Q) / (mass * omega_0**3))
        
        return float(noise_density * 1e6)  # 转换为 μg/√Hz
    
    def calculate_bandwidth(self, proof_mass_size: float, spring_length: float,
                          spring_width: float, damping_ratio: float = 0.7) -> float:
        """
        计算带宽
        BW = f_n / (2 * π * ζ)
        """
        natural_freq = self.calculate_natural_frequency(proof_mass_size, spring_length,
                                                      spring_width, self.silicon.thickness)
        
        bandwidth = natural_freq / (2 * np.pi * damping_ratio)
        
        return float(bandwidth)
    
    def calculate_damping_ratio(self, proof_mass_size: float, gap: float) -> float:
        """
        计算阻尼比
        ζ = c / (2 * √(k * m))
        """
        # 估算阻尼系数 (空气阻尼)
        area = proof_mass_size**2
        c = self.air_viscosity * area / gap
        
        # 弹簧刚度
        spring_length = proof_mass_size * 0.3  # 估算
        spring_width = proof_mass_size * 0.05  # 估算
        I = spring_width * self.silicon.thickness**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length**3
        k_total = 4 * k_single
        
        # 质量
        mass = self.silicon.density * proof_mass_size**2 * self.silicon.thickness * 1e-6
        
        # 阻尼比
        damping_ratio = c / (2 * np.sqrt(k_total * mass))
        
        return float(damping_ratio)
    
    def calculate_pull_in_voltage(self, proof_mass_size: float, spring_length: float,
                                spring_width: float, gap: float) -> float:
        """
        计算吸合电压
        V_pi = √(8 * k * d³) / (27 * ε₀ * A)
        """
        # 弹簧刚度
        I = spring_width * self.silicon.thickness**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length**3
        k_total = 4 * k_single
        
        # 电容面积
        area = proof_mass_size**2
        
        # 真空介电常数
        epsilon_0 = 8.85e-12  # F/m
        
        # 吸合电压
        pull_in_voltage = np.sqrt((8 * k_total * gap**3) / (27 * epsilon_0 * area))
        
        return float(pull_in_voltage)
    
    def calculate_mask_parameters(self, performance_params: IMUPerformanceParams) -> Dict[str, float]:
        """
        根据性能参数计算mask几何参数
        """
        # 初始估算
        proof_mass_size = 1000.0  # μm
        spring_length = 300.0     # μm
        spring_width = 20.0       # μm
        gap = 3.0                 # μm
        voltage = 5.0             # V
        
        # 迭代优化参数
        for _ in range(10):
            # 计算当前参数下的性能
            current_sensitivity = self.calculate_sensitivity(proof_mass_size, spring_length,
                                                          spring_width, gap, voltage)
            current_noise = self.calculate_noise(proof_mass_size, spring_length,
                                               spring_width, gap)
            current_bandwidth = self.calculate_bandwidth(proof_mass_size, spring_length,
                                                       spring_width)
            
            # 调整参数
            sensitivity_ratio = performance_params.sensitivity / current_sensitivity
            noise_ratio = performance_params.noise_density / current_noise
            bandwidth_ratio = performance_params.bandwidth / current_bandwidth
            
            # 更新参数
            proof_mass_size *= np.sqrt(sensitivity_ratio)
            spring_width *= np.sqrt(noise_ratio)
            spring_length *= np.sqrt(bandwidth_ratio)
            
            # 确保参数在合理范围内
            proof_mass_size = np.clip(proof_mass_size, 200.0, 2000.0)
            spring_width = np.clip(spring_width, 5.0, 50.0)
            spring_length = np.clip(spring_length, 100.0, 500.0)
        
        # 计算其他参数
        anchor_size = proof_mass_size * 0.2
        electrode_size = proof_mass_size * 0.8
        trench_width = 5.0
        via_size = 10.0
        
        return {
            "proof_mass_size": float(proof_mass_size),
            "spring_length": float(spring_length),
            "spring_width": float(spring_width),
            "anchor_size": float(anchor_size),
            "electrode_size": float(electrode_size),
            "gap": float(gap),
            "trench_width": float(trench_width),
            "via_size": float(via_size),
            "voltage": float(voltage)
        }
    
    def validate_design(self, mask_params: Dict[str, float]) -> Tuple[bool, str]:
        """
        验证设计是否满足制造约束
        """
        # 最小线宽检查
        min_line_width = 2.0  # μm
        if mask_params["spring_width"] < min_line_width:
            return False, f"弹簧宽度 {mask_params['spring_width']} μm 小于最小线宽 {min_line_width} μm"
        
        # 最小间距检查
        min_spacing = 3.0  # μm
        if mask_params["gap"] < min_spacing:
            return False, f"间隙 {mask_params['gap']} μm 小于最小间距 {min_spacing} μm"
        
        # 吸合电压检查
        pull_in_voltage = self.calculate_pull_in_voltage(
            mask_params["proof_mass_size"],
            mask_params["spring_length"],
            mask_params["spring_width"],
            mask_params["gap"]
        )
        if pull_in_voltage < mask_params["voltage"] * 1.5:
            return False, f"工作电压 {mask_params['voltage']} V 接近吸合电压 {pull_in_voltage:.2f} V"
        
        return True, "设计验证通过" 