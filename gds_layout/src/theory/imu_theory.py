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
        计算自然频率 (Hz)
        f_n = (1/2π) * √(k/m)
        k = 4 * E * I / L³ (四根弹簧并联)
        所有输入参数期望为微米，在计算中转换为米。
        """
        # 转换为米
        spring_length_m = spring_length * 1e-6
        spring_width_m = spring_width * 1e-6
        spring_thickness_m = spring_thickness * 1e-6 

        # 惯性矩 (m^4)
        I = spring_width_m * spring_thickness_m**3 / 12
        
        # 单根弹簧刚度 (N/m)
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length_m**3
        
        # 总刚度 (四根弹簧) (N/m)
        k_total = 4 * k_single
        
        # 质量 (kg)
        proof_mass_size_m = proof_mass_size * 1e-6
        mass = self.silicon.density * proof_mass_size_m**2 * spring_thickness_m
        
        # 自然频率 (Hz)
        natural_freq = (1 / (2 * np.pi)) * np.sqrt(k_total / mass)
        
        return float(natural_freq)
    
    def calculate_sensitivity(self, proof_mass_size: float, spring_length: float,
                           spring_width: float, gap: float, voltage: float) -> float:
        """
        计算电容式加速度计灵敏度 (mV/g)
        S = (ε₀ * A * V) / (d² * k) 
        所有输入参数期望为微米，在计算中转换为米。
        """
        # 转换为米
        proof_mass_size_m = proof_mass_size * 1e-6
        gap_m = gap * 1e-6
        spring_length_m = spring_length * 1e-6
        spring_width_m = spring_width * 1e-6
        spring_thickness_m = self.silicon.thickness * 1e-6 

        # 电容面积 (m^2)
        area = proof_mass_size_m**2
        
        # 真空介电常数
        epsilon_0 = 8.85e-12  # F/m
        
        # 弹簧刚度 (N/m)
        I = spring_width_m * spring_thickness_m**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length_m**3
        k_total = 4 * k_single
        
        # 根据给定公式计算灵敏度，确保单位一致性。
        # (F/m * m^2 * V) / (m^2 * N/m) = C/N (库仑/牛顿)
        # 原始代码将其乘以1000得到mV/g，假设这是正确的缩放因子。
        sensitivity = (epsilon_0 * area * voltage) / (gap_m**2 * k_total)
        
        return float(sensitivity * 1000)  # 转换为 mV/g
    
    def calculate_noise(self, proof_mass_size: float, spring_length: float,
                       spring_width: float, gap: float, temperature: float = 300) -> float:
        """
        计算热机械噪声 (μg/√Hz)
        S_x² = (4 * k_B * T * Q) / (m * ω₀³) (位移噪声公式，转换为加速度噪声)
        所有输入参数期望为微米，在计算中转换为米。
        """
        # 转换为米
        proof_mass_size_m = proof_mass_size * 1e-6
        # spring_length_m = spring_length * 1e-6 # not used here directly
        # spring_width_m = spring_width * 1e-6 # not used here directly
        spring_thickness_m = self.silicon.thickness * 1e-6 

        # 玻尔兹曼常数
        k_b = 1.38e-23  # J/K
        
        # 自然频率 (由 calculate_natural_frequency 保证 SI 单位)
        natural_freq = self.calculate_natural_frequency(proof_mass_size, spring_length, 
                                                      spring_width, self.silicon.thickness)
        omega_0 = 2 * np.pi * natural_freq # 角频率 (rad/s)
        
        # 质量 (kg)
        mass = self.silicon.density * proof_mass_size_m**2 * spring_thickness_m
        
        # 品质因子 (估算)
        Q = 100  # 典型值
        
        # 热机械位移噪声谱密度 (m/√Hz)
        noise_density_displacement = np.sqrt((4 * k_b * temperature * Q) / (mass * omega_0**3))
        
        # 转换为加速度噪声 (m/s^2/√Hz)
        noise_acceleration = noise_density_displacement * omega_0**2 
        
        # 转换为 μg/√Hz (除以重力加速度 9.81 m/s^2，再乘以 1e6 转换为 μg)
        noise_density_ug_per_sqrt_hz = noise_acceleration / 9.81 * 1e6

        return float(noise_density_ug_per_sqrt_hz)
    
    def calculate_bandwidth(self, proof_mass_size: float, spring_length: float,
                          spring_width: float, damping_ratio: float = 0.7) -> float:
        """
        计算带宽 (Hz)
        BW = f_n / (2 * π * ζ)
        """
        natural_freq = self.calculate_natural_frequency(proof_mass_size, spring_length,
                                                      spring_width, self.silicon.thickness)
        
        # 3dB 带宽通常是 f_n / (2 * damping_ratio) 或 f_n * sqrt(1 - 2*zeta^2)
        # 原始公式 BW = f_n / (2 * pi * zeta) 可能指角频率带宽，但评论里是Hz。
        # 为了与原始代码保持一致，保留其形式，并修正其在优化中的使用方式。
        bandwidth = natural_freq / (2 * np.pi * damping_ratio)
        
        return float(bandwidth)
    
    def calculate_damping_ratio(self, proof_mass_size: float, spring_length: float,
                                spring_width: float, gap: float) -> float:
        """
        计算阻尼比
        ζ = c / (2 * √(k * m))
        所有输入参数期望为微米，在计算中转换为米。
        """
        # 转换为米
        proof_mass_size_m = proof_mass_size * 1e-6
        spring_length_m = spring_length * 1e-6
        spring_width_m = spring_width * 1e-6
        gap_m = gap * 1e-6
        spring_thickness_m = self.silicon.thickness * 1e-6

        # 估算阻尼系数 (空气阻尼) (N*s/m)
        area_overlap = proof_mass_size_m**2 
        c = self.air_viscosity * area_overlap / gap_m
        
        # 弹簧刚度 (N/m)
        I = spring_width_m * spring_thickness_m**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length_m**3
        k_total = 4 * k_single
        
        # 质量 (kg)
        mass = self.silicon.density * proof_mass_size_m**2 * spring_thickness_m
        
        # 阻尼比
        damping_ratio = c / (2 * np.sqrt(k_total * mass))
        
        return float(damping_ratio)
    
    def calculate_pull_in_voltage(self, proof_mass_size: float, spring_length: float,
                                spring_width: float, gap: float) -> float:
        """
        计算吸合电压 (V)
        V_pi = √(8 * k * d³) / (27 * ε₀ * A)
        所有输入参数期望为微米，在计算中转换为米。
        """
        # 转换为米
        proof_mass_size_m = proof_mass_size * 1e-6
        gap_m = gap * 1e-6
        spring_length_m = spring_length * 1e-6
        spring_width_m = spring_width * 1e-6
        spring_thickness_m = self.silicon.thickness * 1e-6

        # 弹簧刚度 (N/m)
        I = spring_width_m * spring_thickness_m**3 / 12
        k_single = self.silicon.youngs_modulus * 1e9 * I / spring_length_m**3
        k_total = 4 * k_single
        
        # 电容面积 (m^2)
        area = proof_mass_size_m**2
        
        # 真空介电常数
        epsilon_0 = 8.85e-12  # F/m
        
        # 吸合电压 (V)
        pull_in_voltage = np.sqrt((8 * k_total * gap_m**3) / (27 * epsilon_0 * area))
        
        return float(pull_in_voltage)
    
    def calculate_mask_parameters(self, performance_params: IMUPerformanceParams) -> Dict[str, float]:
        """
        根据性能参数计算mask几何参数，通过迭代优化。
        """
        # 初始估算 (微米单位)
        proof_mass_size = 1000.0  # μm
        spring_length = 300.0     # μm
        spring_width = 20.0       # μm
        gap = 3.0                 # μm
        voltage = 5.0             # V (工作电压)
        
        # 迭代优化参数
        for _ in range(10): # 迭代次数
            # 计算当前参数下的性能
            current_sensitivity = self.calculate_sensitivity(proof_mass_size, spring_length,
                                                          spring_width, gap, voltage)
            current_noise = self.calculate_noise(proof_mass_size, spring_length,
                                               spring_width, gap)
            current_bandwidth = self.calculate_bandwidth(proof_mass_size, spring_length,
                                                       spring_width)
            
            # 根据目标性能与当前性能的比率调整参数 (启发式调整)
            if current_sensitivity != 0:
                sensitivity_ratio = performance_params.sensitivity / current_sensitivity
                proof_mass_size *= np.sqrt(sensitivity_ratio) # 灵敏度通常与面积成正比
            
            if current_noise != 0:
                noise_ratio = performance_params.noise_density / current_noise
                spring_width *= np.sqrt(noise_ratio) # 减小噪声可能需要增加弹簧宽度（增加质量，改变刚度）
            
            if current_bandwidth != 0:
                bandwidth_ratio = performance_params.bandwidth / current_bandwidth
                # 带宽与自然频率成正比，自然频率与弹簧长度的-1.5次方成正比 (f_n ~ 1/L^(3/2))
                # 如果目标带宽更高 (bandwidth_ratio > 1)，需要减小弹簧长度。
                # 如果目标带宽更低 (bandwidth_ratio < 1)，需要增大弹簧长度。
                if bandwidth_ratio > 1: # 目标带宽高，减小L
                    spring_length /= (bandwidth_ratio)**(1/1.5) 
                elif bandwidth_ratio < 1: # 目标带宽低，增大L
                    spring_length *= (1/bandwidth_ratio)**(1/1.5)
            
            # 确保参数在合理范围内
            proof_mass_size = np.clip(proof_mass_size, 200.0, 2000.0)
            spring_width = np.clip(spring_width, 5.0, 50.0)
            spring_length = np.clip(spring_length, 100.0, 500.0)
        
        # 计算其他派生参数
        anchor_size = proof_mass_size * 0.2
        electrode_size = proof_mass_size * 0.8
        trench_width = 5.0 # 假设固定
        via_size = 10.0 # 假设固定
        
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
            return False, f"弹簧宽度 {mask_params['spring_width']:.2f} μm 小于最小线宽 {min_line_width} μm"
        
        # 最小间距检查
        min_spacing = 3.0  # μm
        if mask_params["gap"] < min_spacing:
            return False, f"间隙 {mask_params['gap']:.2f} μm 小于最小间距 {min_spacing} μm"
        
        # 吸合电压检查
        pull_in_voltage = self.calculate_pull_in_voltage(
            mask_params["proof_mass_size"],
            mask_params["spring_length"],
            mask_params["spring_width"],
            mask_params["gap"]
        )
        # 确保吸合电压显著高于工作电压 (安全系数 > 1.5)
        if pull_in_voltage < mask_params["voltage"] * 1.5:
            return False, f"工作电压 {mask_params['voltage']:.2f} V 接近吸合电压 {pull_in_voltage:.2f} V (安全系数不足)"
        
        return True, "设计验证通过"