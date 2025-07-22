"""
Consumer-Grade Accelerometer Layout Generator
消费级加速度计版图生成器
"""

import gdsfactory as gf
from typing import Dict, Tuple, List
import numpy as np
from .layer_definitions import MEMSLayerDefinitions

class AccelerometerLayoutGenerator:
    """加速度计版图生成器"""
    
    def __init__(self):
        self.layer_defs = MEMSLayerDefinitions()
        
    def create_proof_mass(self, c: gf.Component, params: Dict[str, float], 
                          center: Tuple[float, float] = (0, 0)) -> gf.Component:
        """创建质量块"""
        size = params["proof_mass_size"]
        layer_info = self.layer_defs.get_layer_info("proof_mass")
        
        # 主质量块
        proof_mass = c.add_ref(
            gf.components.rectangle(
                size=(size, size),
                layer=(layer_info.layer_number, layer_info.datatype)
            )
        ).move(center)
        
        # 质量块上的减重孔 (提高灵敏度)
        hole_size = size * 0.1
        hole_spacing = size * 0.2
        holes_per_row = 3
        
        for i in range(holes_per_row):
            for j in range(holes_per_row):
                x = center[0] + (i - 1) * hole_spacing
                y = center[1] + (j - 1) * hole_spacing
                c.add_ref(
                    gf.components.rectangle(
                        size=(hole_size, hole_size),
                        layer=(layer_info.layer_number, layer_info.datatype)
                    )
                ).move((x, y))
        
        return proof_mass
    
    def create_springs(self, c: gf.Component, params: Dict[str, float], 
                       proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建四根弹簧"""
        springs = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        spring_width = params["spring_width"]
        
        layer_info = self.layer_defs.get_layer_info("spring")
        
        # 四个方向的弹簧位置
        spring_positions = [
            (-spring_length, 0),  # 左
            (size, 0),            # 右
            (0, -spring_length),  # 下
            (0, size)             # 上
        ]
        
        for i, (dx, dy) in enumerate(spring_positions):
            if i < 2:  # 水平弹簧
                spring = c.add_ref(
                    gf.components.rectangle(
                        size=(spring_length, spring_width),
                        layer=(layer_info.layer_number, layer_info.datatype)
                    )
                ).move((proof_mass_center[0] + dx, proof_mass_center[1] + dy - spring_width/2))
            else:  # 垂直弹簧
                spring = c.add_ref(
                    gf.components.rectangle(
                        size=(spring_width, spring_length),
                        layer=(layer_info.layer_number, layer_info.datatype)
                    )
                ).move((proof_mass_center[0] + dx - spring_width/2, proof_mass_center[1] + dy))
            
            springs.append(spring)
        
        return springs
    
    def create_anchors(self, c: gf.Component, params: Dict[str, float], 
                       proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建四个锚点"""
        anchors = []
        size = params["proof_mass_size"]
        anchor_size = params["anchor_size"]
        spring_length = params["spring_length"]
        
        layer_info = self.layer_defs.get_layer_info("anchor")
        
        # 四个锚点位置
        anchor_positions = [
            (-spring_length - anchor_size, -anchor_size),  # 左下
            (size + spring_length, -anchor_size),          # 右下
            (-spring_length - anchor_size, size),          # 左上
            (size + spring_length, size)                   # 右上
        ]
        
        for dx, dy in anchor_positions:
            anchor = c.add_ref(
                gf.components.rectangle(
                    size=(anchor_size, anchor_size),
                    layer=(layer_info.layer_number, layer_info.datatype)
                )
            ).move((proof_mass_center[0] + dx, proof_mass_center[1] + dy))
            anchors.append(anchor)
        
        return anchors
    
    def create_electrodes(self, c: gf.Component, params: Dict[str, float], 
                          proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建检测电极"""
        electrodes = []
        size = params["proof_mass_size"]
        electrode_size = params["electrode_size"]
        gap = params["gap"]
        
        layer_info = self.layer_defs.get_layer_info("electrode")
        
        # 四个电极位置 (在质量块四周)
        electrode_positions = [
            (-gap - electrode_size, 0),                    # 左
            (size + gap, 0),                               # 右
            (0, -gap - electrode_size),                    # 下
            (0, size + gap)                                # 上
        ]
        
        for dx, dy in electrode_positions:
            electrode = c.add_ref(
                gf.components.rectangle(
                    size=(electrode_size, electrode_size),
                    layer=(layer_info.layer_number, layer_info.datatype)
                )
            ).move((proof_mass_center[0] + dx, proof_mass_center[1] + dy))
            electrodes.append(electrode)
        
        return electrodes
    
    def create_metal_routing(self, c: gf.Component, params: Dict[str, float], 
                            proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建金属布线"""
        routing = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        # 金属1层布线
        metal1_info = self.layer_defs.get_layer_info("metal1")
        metal2_info = self.layer_defs.get_layer_info("metal2")
        
        # 从锚点到焊盘的布线
        bond_pad_size = 200  # μm
        routing_width = 20   # μm
        
        # 四个焊盘位置
        pad_positions = [
            (-spring_length - 300, -300),  # 左下
            (size + spring_length + 100, -300),  # 右下
            (-spring_length - 300, size + 100),  # 左上
            (size + spring_length + 100, size + 100)  # 右上
        ]
        
        for i, (dx, dy) in enumerate(pad_positions):
            # 焊盘
            pad = c.add_ref(
                gf.components.rectangle(
                    size=(bond_pad_size, bond_pad_size),
                    layer=(metal1_info.layer_number, metal1_info.datatype)
                )
            ).move((proof_mass_center[0] + dx, proof_mass_center[1] + dy))
            routing.append(pad)
            
            # 布线
            if i < 2:  # 水平布线
                route = c.add_ref(
                    gf.components.rectangle(
                        size=(300, routing_width),
                        layer=(metal1_info.layer_number, metal1_info.datatype)
                    )
                ).move((proof_mass_center[0] + dx + bond_pad_size, 
                       proof_mass_center[1] + dy + bond_pad_size/2 - routing_width/2))
            else:  # 垂直布线
                route = c.add_ref(
                    gf.components.rectangle(
                        size=(routing_width, 300),
                        layer=(metal1_info.layer_number, metal1_info.datatype)
                    )
                ).move((proof_mass_center[0] + dx + bond_pad_size/2 - routing_width/2,
                       proof_mass_center[1] + dy + bond_pad_size))
            
            routing.append(route)
        
        return routing
    
    def create_vias(self, c: gf.Component, params: Dict[str, float], 
                    proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建通孔"""
        vias = []
        via_size = params["via_size"]
        
        via_info = self.layer_defs.get_layer_info("via")
        
        # 在锚点位置添加通孔
        anchor_size = params["anchor_size"]
        spring_length = params["spring_length"]
        size = params["proof_mass_size"]
        
        via_positions = [
            (-spring_length - anchor_size/2, -anchor_size/2),
            (size + spring_length + anchor_size/2, -anchor_size/2),
            (-spring_length - anchor_size/2, size + anchor_size/2),
            (size + spring_length + anchor_size/2, size + anchor_size/2)
        ]
        
        for dx, dy in via_positions:
            via = c.add_ref(
                gf.components.rectangle(
                    size=(via_size, via_size),
                    layer=(via_info.layer_number, via_info.datatype)
                )
            ).move((proof_mass_center[0] + dx - via_size/2, 
                   proof_mass_center[1] + dy - via_size/2))
            vias.append(via)
        
        return vias
    
    def create_alignment_marks(self, c: gf.Component, params: Dict[str, float], 
                              proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建对准标记"""
        marks = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        align_info = self.layer_defs.get_layer_info("alignment")
        
        # 四个角的对准标记
        mark_size = 100  # μm
        mark_positions = [
            (-spring_length - 400, -400),  # 左下
            (size + spring_length + 200, -400),  # 右下
            (-spring_length - 400, size + 200),  # 左上
            (size + spring_length + 200, size + 200)  # 右上
        ]
        
        for dx, dy in mark_positions:
            # 十字对准标记
            mark_h = c.add_ref(
                gf.components.rectangle(
                    size=(mark_size, 20),
                    layer=(align_info.layer_number, align_info.datatype)
                )
            ).move((proof_mass_center[0] + dx, proof_mass_center[1] + dy + mark_size/2 - 10))
            
            mark_v = c.add_ref(
                gf.components.rectangle(
                    size=(20, mark_size),
                    layer=(align_info.layer_number, align_info.datatype)
                )
            ).move((proof_mass_center[0] + dx + mark_size/2 - 10, proof_mass_center[1] + dy))
            
            marks.extend([mark_h, mark_v])
        
        return marks
    
    def create_dicing_lines(self, c: gf.Component, params: Dict[str, float], 
                           proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建切割线"""
        dicing = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        dicing_info = self.layer_defs.get_layer_info("dicing")
        
        # 芯片边界
        chip_size = max(size + spring_length * 2 + 600, 2000)  # 确保足够大
        
        # 四条切割线
        dicing_lines = [
            # 上边
            ((0, chip_size/2), (chip_size, chip_size/2)),
            # 下边
            ((0, -chip_size/2), (chip_size, -chip_size/2)),
            # 左边
            ((-chip_size/2, 0), (-chip_size/2, chip_size)),
            # 右边
            ((chip_size/2, 0), (chip_size/2, chip_size))
        ]
        
        for start, end in dicing_lines:
            # 计算线段长度和角度
            length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            angle = np.arctan2(end[1] - start[1], end[0] - start[0])
            
            dicing_line = c.add_ref(
                gf.components.rectangle(
                    size=(length, 50),
                    layer=(dicing_info.layer_number, dicing_info.datatype)
                )
            ).move((proof_mass_center[0] + start[0], proof_mass_center[1] + start[1]))
            
            dicing.append(dicing_line)
        
        return dicing
    
    def create_seal_ring(self, c: gf.Component, params: Dict[str, float], 
                         proof_mass_center: Tuple[float, float] = (0, 0)) -> gf.Component:
        """创建密封环"""
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        seal_info = self.layer_defs.get_layer_info("seal_ring")
        
        # 密封环尺寸
        ring_width = 100  # μm
        ring_size = max(size + spring_length * 2 + 400, 1500)
        
        # 外环
        outer_ring = c.add_ref(
            gf.components.rectangle(
                size=(ring_size + ring_width, ring_size + ring_width),
                layer=(seal_info.layer_number, seal_info.datatype)
            )
        ).move((proof_mass_center[0] - ring_size/2 - ring_width/2, 
               proof_mass_center[1] - ring_size/2 - ring_width/2))
        
        # 内环 (挖空)
        inner_ring = c.add_ref(
            gf.components.rectangle(
                size=(ring_size - ring_width, ring_size - ring_width),
                layer=(seal_info.layer_number, seal_info.datatype)
            )
        ).move((proof_mass_center[0] - ring_size/2 + ring_width/2, 
               proof_mass_center[1] - ring_size/2 + ring_width/2))
        
        return outer_ring
    
    def create_guard_ring(self, c: gf.Component, params: Dict[str, float], 
                          proof_mass_center: Tuple[float, float] = (0, 0)) -> gf.Component:
        """创建保护环"""
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        guard_info = self.layer_defs.get_layer_info("guard_ring")
        
        # 保护环尺寸
        guard_width = 50  # μm
        guard_size = size + spring_length * 2 + 200
        
        guard_ring = c.add_ref(
            gf.components.rectangle(
                size=(guard_size + guard_width, guard_size + guard_width),
                layer=(guard_info.layer_number, guard_info.datatype)
            )
        ).move((proof_mass_center[0] - guard_size/2 - guard_width/2, 
               proof_mass_center[1] - guard_size/2 - guard_width/2))
        
        return guard_ring
    
    def create_text_labels(self, c: gf.Component, params: Dict[str, float], 
                          proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建文字标记"""
        labels = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        text_info = self.layer_defs.get_layer_info("text")
        
        # 添加设计信息文字
        text_elements = [
            ("IMU_ACCEL", (0, size + spring_length + 100)),
            ("SENSOR", (0, size + spring_length + 150)),
            ("V1.0", (0, size + spring_length + 200))
        ]
        
        for text, (dx, dy) in text_elements:
            # 使用矩形表示文字 (简化处理)
            text_box = c.add_ref(
                gf.components.rectangle(
                    size=(200, 30),
                    layer=(text_info.layer_number, text_info.datatype)
                )
            ).move((proof_mass_center[0] + dx - 100, proof_mass_center[1] + dy - 15))
            labels.append(text_box)
        
        return labels
    
    def generate_accelerometer_layout(self, params: Dict[str, float]) -> gf.Component:
        """生成完整的加速度计版图"""
        c = gf.Component("Accelerometer")
        
        # 中心位置
        center = (0, 0)
        
        # 创建各个组件
        proof_mass = self.create_proof_mass(c, params, center)
        springs = self.create_springs(c, params, center)
        anchors = self.create_anchors(c, params, center)
        electrodes = self.create_electrodes(c, params, center)
        routing = self.create_metal_routing(c, params, center)
        vias = self.create_vias(c, params, center)
        alignment_marks = self.create_alignment_marks(c, params, center)
        dicing_lines = self.create_dicing_lines(c, params, center)
        seal_ring = self.create_seal_ring(c, params, center)
        guard_ring = self.create_guard_ring(c, params, center)
        text_labels = self.create_text_labels(c, params, center)
        
        return c 