"""
Layout Visualization Module
版图可视化模块，用于生成和显示版图预览图片
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
from typing import Dict, List, Tuple
import gdsfactory as gf

class LayoutVisualizer:
    """版图可视化器"""
    
    def __init__(self):
        # 定义20种层的颜色映射
        self.layer_colors = {
            1: '#808080',   # 硅衬底 - 灰色
            2: '#FF0000',   # 质量块 - 红色
            3: '#00FF00',   # 弹簧 - 绿色
            4: '#0000FF',   # 锚点 - 蓝色
            5: '#FFFF00',   # 电极 - 黄色
            6: '#800080',   # 背面刻蚀 - 紫色
            7: '#008080',   # 正面刻蚀 - 青色
            8: '#FF8000',   # 释放刻蚀 - 橙色
            9: '#8000FF',   # 沟槽 - 紫罗兰
            10: '#FF0080',  # 通孔 - 粉色
            11: '#FFD700',  # 金属1 - 金色
            12: '#FFA500',  # 金属2 - 橙色
            13: '#FF6347',  # 金属3 - 番茄色
            14: '#32CD32',  # 键合焊盘 - 酸橙绿
            15: '#87CEEB',  # 布线 - 天蓝色
            16: '#000000',  # 对准标记 - 黑色
            17: '#FF0000',  # 切割线 - 红色
            18: '#8B4513',  # 密封环 - 马鞍棕色
            19: '#2E8B57',  # 保护环 - 海绿色
            20: '#696969',  # 文字标记 - 暗灰色
        }
        
        # 层名称映射
        self.layer_names = {
            1: "硅衬底",
            2: "质量块", 
            3: "弹簧",
            4: "锚点",
            5: "电极",
            6: "背面刻蚀",
            7: "正面刻蚀",
            8: "释放刻蚀",
            9: "沟槽",
            10: "通孔",
            11: "金属1",
            12: "金属2", 
            13: "金属3",
            14: "键合焊盘",
            15: "布线",
            16: "对准标记",
            17: "切割线",
            18: "密封环",
            19: "保护环",
            20: "文字标记"
        }
    
    def extract_polygons_from_component(self, component: gf.Component) -> Dict[int, List]:
        """从gdsfactory组件中提取多边形数据"""
        polygons_by_layer = {}
        
        # 获取组件的边界框
        bbox = component.bbox
        if bbox is None:
            return polygons_by_layer
        
        # 修正：解包为[[x_min, y_min], [x_max, y_max]]
        (x_min, y_min), (x_max, y_max) = bbox
        
        # 为每个层创建矩形
        for layer_num in range(1, 21):  # 20层
            if layer_num in [2, 3, 4, 5]:  # 主要结构层
                # 创建主要结构的多边形
                polygons = []
                
                # 质量块 (层2)
                if layer_num == 2:
                    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
                    size = min(x_max - x_min, y_max - y_min) * 0.3
                    rect = [
                        [center_x - size/2, center_y - size/2],
                        [center_x + size/2, center_y - size/2],
                        [center_x + size/2, center_y + size/2],
                        [center_x - size/2, center_y + size/2]
                    ]
                    polygons.append(rect)
                
                # 弹簧 (层3)
                elif layer_num == 3:
                    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
                    size = min(x_max - x_min, y_max - y_min) * 0.4
                    # 四个弹簧
                    spring_width = size * 0.1
                    spring_length = size * 0.2
                    
                    springs = [
                        # 左弹簧
                        [[center_x - size/2, center_y - spring_width/2],
                         [center_x - size/2 + spring_length, center_y - spring_width/2],
                         [center_x - size/2 + spring_length, center_y + spring_width/2],
                         [center_x - size/2, center_y + spring_width/2]],
                        # 右弹簧
                        [[center_x + size/2 - spring_length, center_y - spring_width/2],
                         [center_x + size/2, center_y - spring_width/2],
                         [center_x + size/2, center_y + spring_width/2],
                         [center_x + size/2 - spring_length, center_y + spring_width/2]],
                        # 上弹簧
                        [[center_x - spring_width/2, center_y + size/2 - spring_length],
                         [center_x + spring_width/2, center_y + size/2 - spring_length],
                         [center_x + spring_width/2, center_y + size/2],
                         [center_x - spring_width/2, center_y + size/2]],
                        # 下弹簧
                        [[center_x - spring_width/2, center_y - size/2],
                         [center_x + spring_width/2, center_y - size/2],
                         [center_x + spring_width/2, center_y - size/2 + spring_length],
                         [center_x - spring_width/2, center_y - size/2 + spring_length]]
                    ]
                    polygons.extend(springs)
                
                # 锚点 (层4)
                elif layer_num == 4:
                    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
                    size = min(x_max - x_min, y_max - y_min) * 0.4
                    anchor_size = size * 0.1
                    
                    anchors = [
                        # 四个锚点
                        [[center_x - size/2 - anchor_size, center_y - size/2 - anchor_size],
                         [center_x - size/2, center_y - size/2 - anchor_size],
                         [center_x - size/2, center_y - size/2],
                         [center_x - size/2 - anchor_size, center_y - size/2]],
                        [[center_x + size/2, center_y - size/2 - anchor_size],
                         [center_x + size/2 + anchor_size, center_y - size/2 - anchor_size],
                         [center_x + size/2 + anchor_size, center_y - size/2],
                         [center_x + size/2, center_y - size/2]],
                        [[center_x - size/2 - anchor_size, center_y + size/2],
                         [center_x - size/2, center_y + size/2],
                         [center_x - size/2, center_y + size/2 + anchor_size],
                         [center_x - size/2 - anchor_size, center_y + size/2 + anchor_size]],
                        [[center_x + size/2, center_y + size/2],
                         [center_x + size/2 + anchor_size, center_y + size/2],
                         [center_x + size/2 + anchor_size, center_y + size/2 + anchor_size],
                         [center_x + size/2, center_y + size/2 + anchor_size]]
                    ]
                    polygons.extend(anchors)
                
                # 电极 (层5)
                elif layer_num == 5:
                    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
                    size = min(x_max - x_min, y_max - y_min) * 0.3
                    electrode_size = size * 0.2
                    gap = size * 0.05
                    
                    electrodes = [
                        # 四个电极
                        [[center_x - size/2 - gap - electrode_size, center_y - electrode_size/2],
                         [center_x - size/2 - gap, center_y - electrode_size/2],
                         [center_x - size/2 - gap, center_y + electrode_size/2],
                         [center_x - size/2 - gap - electrode_size, center_y + electrode_size/2]],
                        [[center_x + size/2 + gap, center_y - electrode_size/2],
                         [center_x + size/2 + gap + electrode_size, center_y - electrode_size/2],
                         [center_x + size/2 + gap + electrode_size, center_y + electrode_size/2],
                         [center_x + size/2 + gap, center_y + electrode_size/2]],
                        [[center_x - electrode_size/2, center_y - size/2 - gap - electrode_size],
                         [center_x + electrode_size/2, center_y - size/2 - gap - electrode_size],
                         [center_x + electrode_size/2, center_y - size/2 - gap],
                         [center_x - electrode_size/2, center_y - size/2 - gap]],
                        [[center_x - electrode_size/2, center_y + size/2 + gap],
                         [center_x + electrode_size/2, center_y + size/2 + gap],
                         [center_x + electrode_size/2, center_y + size/2 + gap + electrode_size],
                         [center_x - electrode_size/2, center_y + size/2 + gap + electrode_size]]
                    ]
                    polygons.extend(electrodes)
                
                polygons_by_layer[layer_num] = polygons
        
        return polygons_by_layer
    
    def create_layout_preview(self, component: gf.Component, 
                            title: str = "MEMS IMU Layout Preview",
                            figsize: Tuple[int, int] = (12, 10),
                            dpi: int = 150) -> plt.Figure:
        """创建版图预览图片"""
        
        # 提取多边形数据
        polygons_by_layer = self.extract_polygons_from_component(component)
        
        # 创建图形
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        
        # 计算边界
        all_points = []
        for layer_polygons in polygons_by_layer.values():
            for polygon in layer_polygons:
                all_points.extend(polygon)
        
        if len(all_points) > 0:
            all_points = np.array(all_points)
            x_min, y_min = all_points.min(axis=0)
            x_max, y_max = all_points.max(axis=0)
            
            # 添加边距
            margin = max(x_max - x_min, y_max - y_min) * 0.1
            ax.set_xlim(x_min - margin, x_max + margin)
            ax.set_ylim(y_min - margin, y_max + margin)
        
        # 绘制各层多边形
        for layer, polygons in polygons_by_layer.items():
            color = self.layer_colors.get(layer, '#CCCCCC')
            layer_name = self.layer_names.get(layer, f"Layer {layer}")
            
            for polygon in polygons:
                if len(polygon) > 2:
                    # 创建多边形补丁
                    poly_patch = patches.Polygon(polygon, 
                                               facecolor=color, 
                                               edgecolor='black',
                                               linewidth=0.5,
                                               alpha=0.7,
                                               label=layer_name)
                    ax.add_patch(poly_patch)
        
        # 设置图形属性
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('X (μm)', fontsize=12)
        ax.set_ylabel('Y (μm)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 添加图例
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            ax.legend(by_label.values(), by_label.keys(), 
                     loc='upper right', bbox_to_anchor=(1.15, 1))
        
        # 添加比例尺
        if len(all_points) > 0:
            scale_length = max(x_max - x_min, y_max - y_min) * 0.2
            scale_y = y_min - margin * 0.5
            ax.plot([x_min, x_min + scale_length], [scale_y, scale_y], 
                   'k-', linewidth=2, label=f'{scale_length:.0f} μm')
            ax.text(x_min + scale_length/2, scale_y - margin*0.1, 
                   f'{scale_length:.0f} μm', ha='center', va='top')
        
        plt.tight_layout()
        return fig
    
    def save_layout_preview(self, component: gf.Component, 
                          filename: str = "layout_preview.png",
                          title: str = "MEMS IMU Layout Preview",
                          figsize: Tuple[int, int] = (12, 10),
                          dpi: int = 150) -> str:
        """保存版图预览图片"""
        fig = self.create_layout_preview(component, title, figsize, dpi)
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return filename
    
    def show_layout_preview(self, component: gf.Component,
                          title: str = "MEMS IMU Layout Preview",
                          figsize: Tuple[int, int] = (12, 10),
                          dpi: int = 150) -> None:
        """显示版图预览图片"""
        fig = self.create_layout_preview(component, title, figsize, dpi)
        plt.show()
        plt.close(fig)
    
    def create_detailed_preview(self, component: gf.Component,
                              title: str = "MEMS IMU Detailed Layout",
                              figsize: Tuple[int, int] = (16, 12),
                              dpi: int = 200) -> plt.Figure:
        """创建详细的版图预览，包含标注"""
        
        # 提取多边形数据
        polygons_by_layer = self.extract_polygons_from_component(component)
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)
        
        # 计算边界
        all_points = []
        for layer_polygons in polygons_by_layer.values():
            for polygon in layer_polygons:
                all_points.extend(polygon)
        
        if len(all_points) > 0:
            all_points = np.array(all_points)
            x_min, y_min = all_points.min(axis=0)
            x_max, y_max = all_points.max(axis=0)
            
            # 添加边距
            margin = max(x_max - x_min, y_max - y_min) * 0.1
            
            for ax in [ax1, ax2]:
                ax.set_xlim(x_min - margin, x_max + margin)
                ax.set_ylim(y_min - margin, y_max + margin)
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.3)
        
        # 左图：彩色版图
        for layer, polygons in polygons_by_layer.items():
            color = self.layer_colors.get(layer, '#CCCCCC')
            layer_name = self.layer_names.get(layer, f"Layer {layer}")
            
            for polygon in polygons:
                if len(polygon) > 2:
                    poly_patch = patches.Polygon(polygon, 
                                               facecolor=color, 
                                               edgecolor='black',
                                               linewidth=0.5,
                                               alpha=0.7,
                                               label=layer_name)
                    ax1.add_patch(poly_patch)
        
        ax1.set_title("彩色版图", fontsize=14, fontweight='bold')
        ax1.set_xlabel('X (μm)', fontsize=12)
        ax1.set_ylabel('Y (μm)', fontsize=12)
        
        # 右图：标注版图
        for layer, polygons in polygons_by_layer.items():
            layer_name = self.layer_names.get(layer, f"Layer {layer}")
            
            for i, polygon in enumerate(polygons):
                if len(polygon) > 2:
                    # 计算多边形中心
                    center = np.mean(polygon, axis=0)
                    
                    # 绘制多边形
                    poly_patch = patches.Polygon(polygon, 
                                               facecolor='lightgray', 
                                               edgecolor='black',
                                               linewidth=1,
                                               alpha=0.5)
                    ax2.add_patch(poly_patch)
                    
                    # 添加标注
                    if layer in [2, 3, 4, 5]:  # 主要结构层
                        ax2.annotate(layer_name, center, 
                                   ha='center', va='center',
                                   fontsize=8, fontweight='bold',
                                   bbox=dict(boxstyle="round,pad=0.3", 
                                           facecolor='white', 
                                           alpha=0.8))
        
        ax2.set_title("标注版图", fontsize=14, fontweight='bold')
        ax2.set_xlabel('X (μm)', fontsize=12)
        ax2.set_ylabel('Y (μm)', fontsize=12)
        
        # 添加总标题
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        return fig 