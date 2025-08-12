import json
import math
from typing import Dict, List, Tuple, Any

class VisualizationService:
    """Serviço para gerar dados de visualização 3D para toldos e coberturas"""
    
    @staticmethod
    def generate_3d_geometry(product_type: str, dimensions: Dict, materials: Dict) -> Dict:
        """Gera geometria 3D baseada no tipo de produto e dimensões"""
        
        width = float(dimensions.get('width', 0))
        length = float(dimensions.get('length', 0))
        height = float(dimensions.get('height', 2.5))
        angle = float(dimensions.get('angle', 0))  # Ângulo de inclinação
        
        geometry_data = {
            'type': product_type,
            'vertices': [],
            'faces': [],
            'materials': materials,
            'measurements': VisualizationService._calculate_measurements(width, length, height, angle)
        }
        
        if product_type == 'toldo_fixo':
            geometry_data.update(VisualizationService._generate_fixed_awning(width, length, height, angle))
        elif product_type == 'toldo_retratil':
            geometry_data.update(VisualizationService._generate_retractable_awning(width, length, height, angle))
        elif product_type == 'cobertura_policarbonato':
            geometry_data.update(VisualizationService._generate_polycarbonate_cover(width, length, height, angle))
        elif product_type == 'pergolado':
            geometry_data.update(VisualizationService._generate_pergola(width, length, height))
        elif product_type == 'tenda':
            geometry_data.update(VisualizationService._generate_tent(width, length, height))
        else:
            # Estrutura genérica
            geometry_data.update(VisualizationService._generate_generic_structure(width, length, height))
        
        return geometry_data
    
    @staticmethod
    def _calculate_measurements(width: float, length: float, height: float, angle: float) -> Dict:
        """Calcula medidas e cotas da estrutura"""
        area = width * length
        perimeter = 2 * (width + length)
        
        # Calcular área real considerando inclinação
        if angle > 0:
            real_length = length / math.cos(math.radians(angle))
            real_area = width * real_length
        else:
            real_area = area
        
        return {
            'area': round(area, 2),
            'real_area': round(real_area, 2),
            'perimeter': round(perimeter, 2),
            'width': width,
            'length': length,
            'height': height,
            'angle': angle,
            'diagonal': round(math.sqrt(width**2 + length**2), 2)
        }
    
    @staticmethod
    def _generate_fixed_awning(width: float, length: float, height: float, angle: float) -> Dict:
        """Gera geometria para toldo fixo"""
        # Estrutura básica de toldo fixo
        vertices = [
            # Base da estrutura (4 pontos)
            [0, 0, 0],
            [width, 0, 0],
            [width, length, 0],
            [0, length, 0],
            
            # Topo da estrutura (4 pontos)
            [0, 0, height],
            [width, 0, height],
            [width, length, height - (length * math.tan(math.radians(angle)))],
            [0, length, height - (length * math.tan(math.radians(angle)))]
        ]
        
        # Faces da estrutura
        faces = [
            # Lona/cobertura (face superior)
            [4, 5, 6, 7],
            # Laterais da estrutura
            [0, 1, 5, 4],  # Frente
            [2, 3, 7, 6],  # Fundo
            [1, 2, 6, 5],  # Lateral direita
            [3, 0, 4, 7]   # Lateral esquerda
        ]
        
        # Estrutura de suporte
        support_structure = VisualizationService._generate_support_posts(width, length, height)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'support_structure': support_structure,
            'features': {
                'retractable': False,
                'motorized': False,
                'angle_adjustable': False
            }
        }
    
    @staticmethod
    def _generate_retractable_awning(width: float, length: float, height: float, angle: float) -> Dict:
        """Gera geometria para toldo retrátil"""
        # Similar ao fixo, mas com mecanismo retrátil
        base_geometry = VisualizationService._generate_fixed_awning(width, length, height, angle)
        
        # Adicionar trilhos e mecanismo retrátil
        rail_height = height - 0.2
        rails = [
            # Trilho esquerdo
            [[0, 0, rail_height], [0, length, rail_height]],
            # Trilho direito
            [[width, 0, rail_height], [width, length, rail_height]]
        ]
        
        # Cassete (caixa do toldo)
        cassette = {
            'position': [width/2, 0, height],
            'dimensions': [width, 0.3, 0.2]
        }
        
        base_geometry.update({
            'rails': rails,
            'cassette': cassette,
            'features': {
                'retractable': True,
                'motorized': True,
                'angle_adjustable': True,
                'extension_range': [0, length]
            }
        })
        
        return base_geometry
    
    @staticmethod
    def _generate_polycarbonate_cover(width: float, length: float, height: float, angle: float) -> Dict:
        """Gera geometria para cobertura de policarbonato"""
        # Estrutura mais robusta para policarbonato
        vertices = [
            # Base
            [0, 0, 0],
            [width, 0, 0],
            [width, length, 0],
            [0, length, 0],
            
            # Topo com inclinação
            [0, 0, height],
            [width, 0, height],
            [width, length, height - (length * math.tan(math.radians(angle)))],
            [0, length, height - (length * math.tan(math.radians(angle)))]
        ]
        
        # Vigas de suporte adicionais
        beam_spacing = min(width, length) / 3
        support_beams = []
        
        for i in range(1, 3):
            beam_y = i * beam_spacing
            if beam_y < length:
                support_beams.append([
                    [0, beam_y, height],
                    [width, beam_y, height - (beam_y * math.tan(math.radians(angle)))]
                ])
        
        return {
            'vertices': vertices,
            'faces': [[4, 5, 6, 7]],  # Apenas a cobertura
            'support_beams': support_beams,
            'material_type': 'polycarbonate',
            'features': {
                'transparent': True,
                'uv_protection': True,
                'thermal_insulation': True
            }
        }
    
    @staticmethod
    def _generate_pergola(width: float, length: float, height: float) -> Dict:
        """Gera geometria para pergolado"""
        # Estrutura de pergolado com vigas cruzadas
        post_positions = [
            [0, 0], [width, 0], [width, length], [0, length]
        ]
        
        posts = []
        for pos in post_positions:
            posts.append({
                'position': [pos[0], pos[1], 0],
                'height': height,
                'cross_section': [0.1, 0.1]  # 10cm x 10cm
            })
        
        # Vigas principais
        main_beams = [
            [[0, 0, height], [width, 0, height]],
            [[0, length, height], [width, length, height]],
            [[0, 0, height], [0, length, height]],
            [[width, 0, height], [width, length, height]]
        ]
        
        # Ripas transversais
        rafter_spacing = 0.5  # 50cm entre ripas
        rafters = []
        
        num_rafters = int(length / rafter_spacing) + 1
        for i in range(num_rafters):
            y_pos = i * rafter_spacing
            if y_pos <= length:
                rafters.append([[0, y_pos, height], [width, y_pos, height]])
        
        return {
            'posts': posts,
            'main_beams': main_beams,
            'rafters': rafters,
            'features': {
                'open_roof': True,
                'climbing_support': True,
                'partial_shade': True
            }
        }
    
    @staticmethod
    def _generate_tent(width: float, length: float, height: float) -> Dict:
        """Gera geometria para tenda"""
        # Estrutura de tenda com formato triangular
        center_height = height
        side_height = height * 0.6
        
        vertices = [
            # Base
            [0, 0, 0],
            [width, 0, 0],
            [width, length, 0],
            [0, length, 0],
            
            # Laterais
            [0, 0, side_height],
            [width, 0, side_height],
            [width, length, side_height],
            [0, length, side_height],
            
            # Pico central
            [width/2, 0, center_height],
            [width/2, length, center_height]
        ]
        
        faces = [
            # Laterais da tenda
            [0, 1, 8, 4],  # Frente esquerda
            [1, 8, 5],     # Frente direita
            [2, 3, 9, 6],  # Fundo esquerda
            [3, 9, 7],     # Fundo direita
            [4, 8, 9, 7],  # Lateral esquerda
            [5, 8, 9, 6]   # Lateral direita
        ]
        
        return {
            'vertices': vertices,
            'faces': faces,
            'features': {
                'portable': True,
                'weather_resistant': True,
                'quick_setup': True
            }
        }
    
    @staticmethod
    def _generate_generic_structure(width: float, length: float, height: float) -> Dict:
        """Gera estrutura genérica"""
        vertices = [
            [0, 0, 0], [width, 0, 0], [width, length, 0], [0, length, 0],
            [0, 0, height], [width, 0, height], [width, length, height], [0, length, height]
        ]
        
        faces = [[4, 5, 6, 7]]  # Apenas o topo
        
        return {
            'vertices': vertices,
            'faces': faces,
            'features': {}
        }
    
    @staticmethod
    def _generate_support_posts(width: float, length: float, height: float) -> List[Dict]:
        """Gera postes de suporte"""
        posts = []
        
        # Postes nos cantos
        corner_positions = [
            [0, 0], [width, 0], [width, length], [0, length]
        ]
        
        for pos in corner_positions:
            posts.append({
                'position': [pos[0], pos[1], 0],
                'height': height,
                'diameter': 0.08,  # 8cm de diâmetro
                'material': 'aluminum'
            })
        
        # Postes intermediários se necessário
        if width > 4:  # Adicionar poste intermediário se largura > 4m
            posts.append({
                'position': [width/2, 0, 0],
                'height': height,
                'diameter': 0.08,
                'material': 'aluminum'
            })
            posts.append({
                'position': [width/2, length, 0],
                'height': height,
                'diameter': 0.08,
                'material': 'aluminum'
            })
        
        return posts
    
    @staticmethod
    def generate_quotation_lines(geometry_data: Dict) -> List[Dict]:
        """Gera linhas de cotação para a visualização"""
        measurements = geometry_data.get('measurements', {})
        
        quotation_lines = [
            {
                'type': 'dimension',
                'label': f"{measurements.get('width', 0):.2f}m",
                'start': [0, 0, 0],
                'end': [measurements.get('width', 0), 0, 0],
                'offset': [0, -0.5, 0]
            },
            {
                'type': 'dimension',
                'label': f"{measurements.get('length', 0):.2f}m",
                'start': [0, 0, 0],
                'end': [0, measurements.get('length', 0), 0],
                'offset': [-0.5, 0, 0]
            },
            {
                'type': 'dimension',
                'label': f"{measurements.get('height', 0):.2f}m",
                'start': [0, 0, 0],
                'end': [0, 0, measurements.get('height', 0)],
                'offset': [-0.5, -0.5, 0]
            }
        ]
        
        # Adicionar cota de área
        quotation_lines.append({
            'type': 'area',
            'label': f"Área: {measurements.get('area', 0):.2f}m²",
            'position': [measurements.get('width', 0)/2, measurements.get('length', 0)/2, 0],
            'offset': [0, 0, 0.1]
        })
        
        return quotation_lines
    
    @staticmethod
    def export_to_threejs_format(geometry_data: Dict) -> Dict:
        """Exporta dados no formato compatível com Three.js"""
        return {
            'geometry': {
                'vertices': geometry_data.get('vertices', []),
                'faces': geometry_data.get('faces', []),
                'normals': VisualizationService._calculate_normals(
                    geometry_data.get('vertices', []),
                    geometry_data.get('faces', [])
                )
            },
            'materials': geometry_data.get('materials', {}),
            'measurements': geometry_data.get('measurements', {}),
            'quotation_lines': VisualizationService.generate_quotation_lines(geometry_data),
            'features': geometry_data.get('features', {}),
            'metadata': {
                'type': geometry_data.get('type', 'generic'),
                'generated_at': 'server_timestamp',
                'version': '1.0'
            }
        }
    
    @staticmethod
    def _calculate_normals(vertices: List, faces: List) -> List:
        """Calcula normais das faces para iluminação 3D"""
        normals = []
        
        for face in faces:
            if len(face) >= 3:
                # Pegar três primeiros vértices da face
                v1 = vertices[face[0]]
                v2 = vertices[face[1]]
                v3 = vertices[face[2]]
                
                # Calcular vetores das arestas
                edge1 = [v2[i] - v1[i] for i in range(3)]
                edge2 = [v3[i] - v1[i] for i in range(3)]
                
                # Produto vetorial para obter normal
                normal = [
                    edge1[1] * edge2[2] - edge1[2] * edge2[1],
                    edge1[2] * edge2[0] - edge1[0] * edge2[2],
                    edge1[0] * edge2[1] - edge1[1] * edge2[0]
                ]
                
                # Normalizar
                length = math.sqrt(sum(n**2 for n in normal))
                if length > 0:
                    normal = [n/length for n in normal]
                
                normals.append(normal)
            else:
                normals.append([0, 0, 1])  # Normal padrão
        
        return normals

