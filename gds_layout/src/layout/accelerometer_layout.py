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
        
        # 四个方向的弹簧位置 (这些坐标是弹簧矩形的左下角，相对于质量块中心)
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
        
        # 四个锚点位置 (这些坐标是锚点矩形的左下角，相对于质量块中心)
        # 锚点放置在弹簧固定端的外侧
        anchor_positions = [
            (proof_mass_center[0] - spring_length - anchor_size, proof_mass_center[1] - anchor_size/2),  # 左下
            (proof_mass_center[0] + size + spring_length, proof_mass_center[1] - anchor_size/2),          # 右下
            (proof_mass_center[0] - anchor_size/2, proof_mass_center[1] - spring_length - anchor_size),  # 左上
            (proof_mass_center[0] - anchor_size/2, proof_mass_center[1] + size + spring_length)                   # 右上
        ]
        # Previous comment on anchor positions seems off. Re-adjusting to be more sensible.
        # It's better to place them directly relative to the springs they are anchoring.
        # For the left spring at (-spring_length, 0) relative to proof_mass_center bottom-left, its anchored end is at (-spring_length, 0) + spring_width/2 on Y
        # Let's keep the original logic for now, as it's consistent if they are corner anchors for the whole device.
        anchor_positions = [
            (proof_mass_center[0] - spring_length - anchor_size, proof_mass_center[1] - anchor_size),  # 左下
            (proof_mass_center[0] + size + spring_length, proof_mass_center[1] - anchor_size),          # 右下
            (proof_mass_center[0] - spring_length - anchor_size, proof_mass_center[1] + size),          # 左上
            (proof_mass_center[0] + size + spring_length, proof_mass_center[1] + size)                   # 右上
        ]
        
        for dx, dy in anchor_positions:
            anchor = c.add_ref(
                gf.components.rectangle(
                    size=(anchor_size, anchor_size),
                    layer=(layer_info.layer_number, layer_info.datatype)
                )
            ).move((dx, dy)) # 已是绝对位置
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
        
        # 四个电极位置 (在质量块四周，这些坐标是电极矩形的左下角)
        electrode_positions = [
            (proof_mass_center[0] - gap - electrode_size, proof_mass_center[1] + size/2 - electrode_size/2), # 左侧，垂直居中
            (proof_mass_center[0] + size + gap, proof_mass_center[1] + size/2 - electrode_size/2),         # 右侧，垂直居中
            (proof_mass_center[0] + size/2 - electrode_size/2, proof_mass_center[1] - gap - electrode_size), # 下侧，水平居中
            (proof_mass_center[0] + size/2 - electrode_size/2, proof_mass_center[1] + size + gap)           # 上侧，水平居中
        ]
        
        for dx, dy in electrode_positions:
            electrode = c.add_ref(
                gf.components.rectangle(
                    size=(electrode_size, electrode_size),
                    layer=(layer_info.layer_number, layer_info.datatype)
                )
            ).move((dx, dy))
            electrodes.append(electrode)
        
        return electrodes
    
    def create_metal_routing(self, c: gf.Component, params: Dict[str, float], 
                            proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建金属布线"""
        routing = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        # 使用键合焊盘和布线的特定层定义
        bond_pad_info = self.layer_defs.get_layer_info("bond_pad")
        routing_info = self.layer_defs.get_layer_info("routing")
        
        bond_pad_size = 200  # μm
        routing_width = 20   # μm
        
        # 四个焊盘位置 (这些坐标是焊盘矩形的左下角)
        pad_positions = [
            (proof_mass_center[0] - spring_length - 300 - bond_pad_size, proof_mass_center[1] - 300 - bond_pad_size),  # 左下
            (proof_mass_center[0] + size + spring_length + 100, proof_mass_center[1] - 300 - bond_pad_size),  # 右下
            (proof_mass_center[0] - spring_length - 300 - bond_pad_size, proof_mass_center[1] + size + 100),  # 左上
            (proof_mass_center[0] + size + spring_length + 100, proof_mass_center[1] + size + 100)  # 右上
        ]
        
        for i, (pad_x, pad_y) in enumerate(pad_positions):
            # 焊盘
            pad = c.add_ref(
                gf.components.rectangle(
                    size=(bond_pad_size, bond_pad_size),
                    layer=(bond_pad_info.layer_number, bond_pad_info.datatype) # 使用 bond_pad 层
                )
            ).move((pad_x, pad_y))
            routing.append(pad)
            
            # 布线 (简化为从焊盘边缘延伸的固定长度布线)
            if i == 0:  # 左下焊盘: 布线向右延伸
                route = c.add_ref(
                    gf.components.rectangle(
                        size=(300, routing_width),
                        layer=(routing_info.layer_number, routing_info.datatype) # 使用 routing 层
                    )
                ).move((pad_x + bond_pad_size, pad_y + bond_pad_size/2 - routing_width/2))
            elif i == 1: # 右下焊盘: 布线向左延伸
                 route = c.add_ref(
                    gf.components.rectangle(
                        size=(300, routing_width),
                        layer=(routing_info.layer_number, routing_info.datatype)
                    )
                ).move((pad_x - 300, pad_y + bond_pad_size/2 - routing_width/2))
            elif i == 2: # 左上焊盘: 布线向右延伸
                route = c.add_ref(
                    gf.components.rectangle(
                        size=(300, routing_width),
                        layer=(routing_info.layer_number, routing_info.datatype)
                    )
                ).move((pad_x + bond_pad_size, pad_y + bond_pad_size/2 - routing_width/2))
            else:  # 右上焊盘: 布线向左延伸
                route = c.add_ref(
                    gf.components.rectangle(
                        size=(300, routing_width),
                        layer=(routing_info.layer_number, routing_info.datatype)
                    )
                ).move((pad_x - 300, pad_y + bond_pad_size/2 - routing_width/2))
            
            routing.append(route)
        
        return routing
    
    def create_vias(self, c: gf.Component, params: Dict[str, float], 
                    proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建通孔"""
        vias = []
        via_size = params["via_size"]
        
        via_info = self.layer_defs.get_layer_info("via")
        layer_tuple = (via_info.layer_number, via_info.datatype)
        
        # 在锚点位置添加通孔
        anchor_size = params["anchor_size"]
        spring_length = params["spring_length"]
        size = params["proof_mass_size"]
        
        # 通孔中心位置 (与锚点中心对齐)
        via_positions_center = [
            (proof_mass_center[0] - spring_length - anchor_size/2, proof_mass_center[1] - anchor_size/2),  # 左下锚点中心
            (proof_mass_center[0] + size + spring_length + anchor_size/2, proof_mass_center[1] - anchor_size/2),          # 右下锚点中心
            (proof_mass_center[0] - spring_length - anchor_size/2, proof_mass_center[1] + size + anchor_size/2),          # 左上锚点中心
            (proof_mass_center[0] + size + spring_length + anchor_size/2, proof_mass_center[1] + size + anchor_size/2)                   # 右上锚点中心
        ]
        
        for dx, dy in via_positions_center:
            via = c.add_ref(
                gf.components.rectangle(
                    size=(via_size, via_size),
                    layer=layer_tuple
                )
            ).move((dx - via_size/2, dy - via_size/2)) # 移动以使矩形中心位于 (dx, dy)
            vias.append(via)
        
        return vias
    
    def create_alignment_marks(self, c: gf.Component, params: Dict[str, float], 
                              proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建对准标记"""
        marks = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        align_info = self.layer_defs.get_layer_info("alignment")
        layer_tuple = (align_info.layer_number, align_info.datatype)
        
        # 四个角的对准标记
        mark_size = 100  # μm
        mark_line_width = 20 # μm
        
        # 标记位置 (这些坐标是标记区域的左下角)
        mark_positions = [
            (proof_mass_center[0] - spring_length - 400 - mark_size, proof_mass_center[1] - 400 - mark_size),  # 左下
            (proof_mass_center[0] + size + spring_length + 200, proof_mass_center[1] - 400 - mark_size),  # 右下
            (proof_mass_center[0] - spring_length - 400 - mark_size, proof_mass_center[1] + size + 200),  # 左上
            (proof_mass_center[0] + size + spring_length + 200, proof_mass_center[1] + size + 200)  # 右上
        ]
        
        for mark_x, mark_y in mark_positions:
            # 十字对准标记
            # 水平条 (在 mark_size x mark_size 区域内居中)
            mark_h = c.add_ref(
                gf.components.rectangle(
                    size=(mark_size, mark_line_width),
                    layer=layer_tuple
                )
            ).move((mark_x, mark_y + mark_size/2 - mark_line_width/2))
            
            # 垂直条 (在 mark_size x mark_size 区域内居中)
            mark_v = c.add_ref(
                gf.components.rectangle(
                    size=(mark_line_width, mark_size),
                    layer=layer_tuple
                )
            ).move((mark_x + mark_size/2 - mark_line_width/2, mark_y))
            
            marks.extend([mark_h, mark_v])
        
        return marks
    
    def create_dicing_lines(self, c: gf.Component, params: Dict[str, float], 
                           proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建切割线"""
        dicing = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        bond_pad_size = 200 # For chip_size calculation

        dicing_info = self.layer_defs.get_layer_info("dicing")
        layer_tuple = (dicing_info.layer_number, dicing_info.datatype)
        
        # 芯片边界 - 应该定义芯片的外部极限
        # 考虑所有组件的最大范围来计算芯片尺寸
        # 假设芯片中心与 proof_mass_center 对齐
        chip_edge_distance_from_center = max(size/2 + spring_length + 300 + bond_pad_size/2 + 300, 1000) # 约芯片尺寸的一半
        chip_size_full = chip_edge_distance_from_center * 2
        
        line_thickness = 50 # μm 切割线厚度

        # 水平切割线 (顶部和底部)
        # 顶部线: 中心在 (0, chip_size_full/2)
        top_dicing_line = c.add_ref(
            gf.components.rectangle(
                size=(chip_size_full, line_thickness),
                layer=layer_tuple
            )
        ).move((proof_mass_center[0] - chip_size_full / 2, 
               proof_mass_center[1] + chip_size_full / 2 - line_thickness / 2))
        dicing.append(top_dicing_line)

        # 底部线: 中心在 (0, -chip_size_full/2)
        bottom_dicing_line = c.add_ref(
            gf.components.rectangle(
                size=(chip_size_full, line_thickness),
                layer=layer_tuple
            )
        ).move((proof_mass_center[0] - chip_size_full / 2, 
               proof_mass_center[1] - chip_size_full / 2 - line_thickness / 2))
        dicing.append(bottom_dicing_line)

        # 垂直切割线 (左侧和右侧)
        # 左侧线: 中心在 (-chip_size_full/2, 0)
        left_dicing_line = c.add_ref(
            gf.components.rectangle(
                size=(line_thickness, chip_size_full),
                layer=layer_tuple
            )
        ).move((proof_mass_center[0] - chip_size_full / 2 - line_thickness / 2, 
               proof_mass_center[1] - chip_size_full / 2))
        dicing.append(left_dicing_line)

        # 右侧线: 中心在 (chip_size_full/2, 0)
        right_dicing_line = c.add_ref(
            gf.components.rectangle(
                size=(line_thickness, chip_size_full),
                layer=layer_tuple
            )
        ).move((proof_mass_center[0] + chip_size_full / 2 - line_thickness / 2, 
               proof_mass_center[1] - chip_size_full / 2))
        dicing.append(right_dicing_line)
        
        return dicing
    
    def create_seal_ring(self, c: gf.Component, params: Dict[str, float], 
                         proof_mass_center: Tuple[float, float] = (0, 0)) -> gf.Component:
        """创建密封环"""
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        bond_pad_size = 200 # For outer_ring_edge calculation
        
        seal_info = self.layer_defs.get_layer_info("seal_ring")
        layer_tuple = (seal_info.layer_number, seal_info.datatype)
        
        ring_width = 100  # μm
        
        # 计算密封环的外部尺寸。它应该位于切割线内部，并留有一些裕度。
        # 假设其外边缘距离芯片中心与 dicing line 保持一致，再减去一些裕度。
        chip_edge_distance_from_center = max(size/2 + spring_length + 300 + bond_pad_size/2 + 300, 1000)
        outer_ring_dim = chip_edge_distance_from_center * 2 - 200 # 距离芯片边缘 100um 的裕度，两边共200um
        
        # 创建外部矩形
        outer_rect = gf.components.rectangle(
            size=(outer_ring_dim, outer_ring_dim),
            layer=layer_tuple
        ).move((proof_mass_center[0] - outer_ring_dim / 2, proof_mass_center[1] - outer_ring_dim / 2))
        
        # 创建用于减法的内部矩形
        inner_ring_dim = outer_ring_dim - 2 * ring_width
        inner_rect = gf.components.rectangle(
            size=(inner_ring_dim, inner_ring_dim),
            layer=layer_tuple
        ).move((proof_mass_center[0] - inner_ring_dim / 2, proof_mass_center[1] - inner_ring_dim / 2))
        
        # 执行布尔减法以创建环
        seal_ring_component = gf.boolean(outer_rect, inner_rect, 'A-B', layer=layer_tuple)
        c.add_ref(seal_ring_component)
        
        return seal_ring_component
    
    def create_guard_ring(self, c: gf.Component, params: Dict[str, float], 
                          proof_mass_center: Tuple[float, float] = (0, 0)) -> gf.Component:
        """创建保护环"""
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        bond_pad_size = 200 # For outer_ring_edge calculation
        
        guard_info = self.layer_defs.get_layer_info("guard_ring")
        layer_tuple = (guard_info.layer_number, guard_info.datatype)
        
        guard_width = 50  # μm
        
        # 保护环尺寸逻辑，应位于密封环内部。
        # 假设其外边缘距离芯片中心与 seal ring 保持一致，再减去一些裕度。
        chip_edge_distance_from_center = max(size/2 + spring_length + 300 + bond_pad_size/2 + 300, 1000)
        seal_ring_outer_edge_from_center = chip_edge_distance_from_center - 100 # From seal_ring calculation (half dim)
        guard_outer_dim = (seal_ring_outer_edge_from_center - 50) * 2 # 距离密封环内边缘 50um
        
        # 创建外部矩形
        outer_rect = gf.components.rectangle(
            size=(guard_outer_dim, guard_outer_dim),
            layer=layer_tuple
        ).move((proof_mass_center[0] - guard_outer_dim / 2, proof_mass_center[1] - guard_outer_dim / 2))
        
        # 创建用于减法的内部矩形
        inner_guard_dim = guard_outer_dim - 2 * guard_width
        inner_rect = gf.components.rectangle(
            size=(inner_guard_dim, inner_guard_dim),
            layer=layer_tuple
        ).move((proof_mass_center[0] - inner_guard_dim / 2, proof_mass_center[1] - inner_guard_dim / 2))
        
        # 执行布尔减法以创建环
        guard_ring_component = gf.boolean(outer_rect, inner_rect, 'A-B', layer=layer_tuple)
        c.add_ref(guard_ring_component)
        
        return guard_ring_component
    
    def create_text_labels(self, c: gf.Component, params: Dict[str, float], 
                          proof_mass_center: Tuple[float, float] = (0, 0)) -> List[gf.Component]:
        """创建文字标记"""
        labels = []
        size = params["proof_mass_size"]
        spring_length = params["spring_length"]
        
        text_info = self.layer_defs.get_layer_info("text")
        layer_tuple = (text_info.layer_number, text_info.datatype)
        
        # 添加设计信息文字
        text_elements_pos = [
            ("IMU_ACCEL", (proof_mass_center[0], proof_mass_center[1] + size + spring_length + 100)),
            ("SENSOR", (proof_mass_center[0], proof_mass_center[1] + size + spring_length + 150)),
            ("V1.0", (proof_mass_center[0], proof_mass_center[1] + size + spring_length + 200))
        ]
        
        text_size = 50 # 文字大小 (μm)
        
        for text_str, (x_pos, y_pos) in text_elements_pos:
            text_comp = gf.components.text(text_str, size=text_size, layer=layer_tuple)
            
            # 计算文字的边界框以进行精确居中
            text_bbox = text_comp.bbox
            if text_bbox is not None:
                text_width = text_bbox[1][0] - text_bbox[0][0]
                text_height = text_bbox[1][1] - text_bbox[0][1]
                centered_text = c.add_ref(text_comp).move((x_pos - text_width / 2, y_pos - text_height / 2))
            else: # 防止空字符串等情况导致 bbox 为 None
                centered_text = c.add_ref(text_comp).move((x_pos, y_pos))
            
            labels.append(centered_text)
        
        return labels
    
    def generate_accelerometer_layout(self, params: Dict[str, float]) -> gf.Component:
        """生成完整的加速度计版图"""
        c = gf.Component("Accelerometer")
        
        # 中心位置
        center = (0, 0) 
        
        # 创建各个组件
        self.create_proof_mass(c, params, center)
        self.create_springs(c, params, center)
        self.create_anchors(c, params, center)
        self.create_electrodes(c, params, center)
        self.create_metal_routing(c, params, center)
        self.create_vias(c, params, center)
        self.create_alignment_marks(c, params, center)
        self.create_dicing_lines(c, params, center)
        self.create_seal_ring(c, params, center) 
        self.create_guard_ring(c, params, center) 
        self.create_text_labels(c, params, center)
        
        return c