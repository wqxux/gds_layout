"""
MEMS Layer Definitions
定义20种标准MEMS工艺层，符合制造规范
"""

from typing import Dict, Tuple, NamedTuple

class LayerInfo(NamedTuple):
    """层信息"""
    layer_number: int
    datatype: int
    description: str
    color: str
    min_width: float  # μm
    min_spacing: float  # μm

class MEMSLayerDefinitions:
    """MEMS工艺层定义"""
    
    def __init__(self):
        # 定义20种标准MEMS工艺层
        self.layers = {
            # 1-5: 结构层
            "substrate": LayerInfo(1, 0, "硅衬底", "#808080", 2.0, 3.0),
            "proof_mass": LayerInfo(2, 0, "质量块", "#FF0000", 5.0, 3.0),
            "spring": LayerInfo(3, 0, "弹簧", "#00FF00", 2.0, 3.0),
            "anchor": LayerInfo(4, 0, "锚点", "#0000FF", 10.0, 5.0),
            "electrode": LayerInfo(5, 0, "电极", "#FFFF00", 5.0, 3.0),
            
            # 6-10: 刻蚀层
            "backside_etch": LayerInfo(6, 0, "背面刻蚀", "#800080", 20.0, 10.0),
            "frontside_etch": LayerInfo(7, 0, "正面刻蚀", "#008080", 5.0, 3.0),
            "release_etch": LayerInfo(8, 0, "释放刻蚀", "#FF8000", 10.0, 5.0),
            "trench": LayerInfo(9, 0, "沟槽", "#8000FF", 5.0, 3.0),
            "via": LayerInfo(10, 0, "通孔", "#FF0080", 10.0, 5.0),
            
            # 11-15: 金属层
            "metal1": LayerInfo(11, 0, "金属1", "#FFD700", 3.0, 3.0),
            "metal2": LayerInfo(12, 0, "金属2", "#FFA500", 3.0, 3.0),
            "metal3": LayerInfo(13, 0, "金属3", "#FF6347", 3.0, 3.0),
            "bond_pad": LayerInfo(14, 0, "键合焊盘", "#32CD32", 100.0, 50.0),
            "routing": LayerInfo(15, 0, "布线", "#87CEEB", 5.0, 5.0),
            
            # 16-20: 特殊层
            "alignment": LayerInfo(16, 0, "对准标记", "#000000", 50.0, 20.0),
            "dicing": LayerInfo(17, 0, "切割线", "#FF0000", 100.0, 50.0),
            "seal_ring": LayerInfo(18, 0, "密封环", "#8B4513", 20.0, 10.0),
            "guard_ring": LayerInfo(19, 0, "保护环", "#2E8B57", 10.0, 5.0),
            "text": LayerInfo(20, 0, "文字标记", "#696969", 10.0, 5.0),
        }
    
    def get_layer_info(self, layer_name: str) -> LayerInfo:
        """获取层信息"""
        return self.layers[layer_name]
    
    def get_layer_number(self, layer_name: str) -> int:
        """获取层号"""
        return self.layers[layer_name].layer_number
    
    def get_layer_tuple(self, layer_name: str) -> Tuple[int, int]:
        """获取层元组 (layer_number, datatype)"""
        layer_info = self.layers[layer_name]
        return (layer_info.layer_number, layer_info.datatype)
    
    def validate_dimensions(self, layer_name: str, width: float, spacing: float = 0.0) -> bool:
        """验证尺寸是否符合制造规范"""
        layer_info = self.layers[layer_name]
        
        if width < layer_info.min_width:
            return False
        
        if spacing > 0 and spacing < layer_info.min_spacing:
            return False
        
        return True
    
    def get_all_layers(self) -> Dict[str, LayerInfo]:
        """获取所有层定义"""
        return self.layers.copy()
    
    def get_layer_names(self) -> list:
        """获取所有层名称"""
        return list(self.layers.keys()) 