"""
DICOM SR 파서 모듈
DICOM SR(Structured Report) 파일을 파싱하고 트리 구조로 변환하는 기능을 제공합니다.
"""

import pydicom
from pydicom.dataset import Dataset
import logging

class DicomSRParser:
    """DICOM SR 파일을 파싱하고 트리 구조로 변환하는 클래스"""
    
    def __init__(self):
        """DicomSRParser 클래스 초기화"""
        self.logger = logging.getLogger('DicomSRParser')
        self.dataset = None
        self.tree = None
    
    def load_file(self, file_path):
        """
        DICOM SR 파일을 로드합니다.
        
        Args:
            file_path (str): DICOM SR 파일 경로
            
        Returns:
            bool: 파일 로드 성공 여부
        """
        try:
            self.dataset = pydicom.dcmread(file_path)
            self.logger.info(f"DICOM 파일 로드 성공: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"DICOM 파일 로드 실패: {e}")
            return False
    
    def parse_sr(self):
        """
        로드된 DICOM SR 파일을 파싱하여 트리 구조로 변환합니다.
        
        Returns:
            dict: 트리 구조로 변환된 DICOM SR 데이터
        """
        if self.dataset is None:
            self.logger.error("파싱할 DICOM 데이터가 없습니다. 먼저 파일을 로드하세요.")
            return None
        
        try:
            # Content Sequence가 있는지 확인
            if hasattr(self.dataset, 'ContentSequence'):
                if len(self.dataset.ContentSequence) > 0:
                    # 첫 번째 ContentItem을 루트 노드로 사용
                    root_node = self._create_node_from_content_item(self.dataset.ContentSequence[0], 0)
                    if isinstance(root_node, list):
                        root_node = root_node[0]
                    
                    # 루트 노드의 ContentSequence가 있는 경우 파싱
                    if hasattr(self.dataset.ContentSequence[0], 'ContentSequence'):
                        self._parse_content_sequence(self.dataset.ContentSequence[0].ContentSequence, root_node['children'])
                    
                    self.tree = root_node
                    return self.tree
                else:
                    self.logger.warning("ContentSequence가 비어있습니다.")
                    return None
            else:
                self.logger.warning("ContentSequence를 찾을 수 없습니다. SR 문서가 아닐 수 있습니다.")
                return None
                
        except Exception as e:
            self.logger.error(f"SR 파싱 중 오류 발생: {e}")
            return None
    
    def _parse_content_sequence(self, content_sequence, parent_children):
        """
        ContentSequence를 재귀적으로 파싱하여 트리 구조를 생성합니다.
        
        Args:
            content_sequence: DICOM ContentSequence
            parent_children (list): 부모 노드의 children 리스트
        """
        for i, content_item in enumerate(content_sequence):
            node = self._create_node_from_content_item(content_item, i)
            parent_children.append(node)
            
            # 자식 노드가 있는 경우 재귀적으로 파싱
            if hasattr(content_item, 'ContentSequence'):
                self._parse_content_sequence(content_item.ContentSequence, node['children'])
    
    def _create_node_from_content_item(self, content_item, index):
        """
        ContentItem에서 노드 정보를 추출합니다.
        
        Args:
            content_item: DICOM ContentItem
            index (int): 노드 인덱스
            
        Returns:
            dict: 노드 정보
        """
        node = {
            'id': f'node_{index}',
            'children': []
        }
        
        if not hasattr(content_item, 'ValueType'):
            node.update({
                'type': 'UNKNOWN',
                'value': 'Unknown content item'
            })
            return node
            
        node['type'] = content_item.ValueType
        
        # ConceptNameCodeSequence 정보 추출 (모든 타입에 공통)
        name_info = self._extract_code_sequence_info(content_item, 'ConceptNameCodeSequence')
        if name_info:
            node.update({
                'NameCodeMeaning': name_info['CodeMeaning'],
                'NameCodeValue': name_info['CodeValue'],
                'NameCodingSchemeDesignator': name_info['CodingSchemeDesignator']
            })
        
        # ValueType별 처리
        value_handlers = {
            'TEXT': self._handle_text_value,
            'CODE': self._handle_code_value,
            'NUM': self._handle_num_value,
            'CONTAINER': self._handle_container_value
        }
        
        handler = value_handlers.get(content_item.ValueType, self._handle_default_value)
        handler(content_item, node, name_info)
        
        # 관계 정보 추가
        if hasattr(content_item, 'RelationshipType'):
            node['relationship'] = content_item.RelationshipType
        
        return node
    
    def _handle_text_value(self, content_item, node, name_info):
        """TEXT 타입 값 처리"""
        if hasattr(content_item, 'TextValue') and name_info:
            node['value'] = f"{name_info['CodeMeaning']} : {content_item.TextValue} ({name_info['CodeValue']} {name_info['CodingSchemeDesignator']})"
    
    def _handle_code_value(self, content_item, node, name_info):
        """CODE 타입 값 처리"""
        code_info = self._extract_code_sequence_info(content_item, 'ConceptCodeSequence')
        if code_info:
            node.update({
                'CodeMeaning': code_info['CodeMeaning'],
                'CodeValue': code_info['CodeValue'],
                'CodingSchemeDesignator': code_info['CodingSchemeDesignator']
            })
            if name_info:
                node['value'] = f"{name_info['CodeMeaning']} ({name_info['CodeValue']} {name_info['CodingSchemeDesignator']}) : {code_info['CodeMeaning']} ({code_info['CodeValue']})"
    
    def _handle_num_value(self, content_item, node, name_info):
        """NUM 타입 값 처리"""
        if not hasattr(content_item, 'MeasuredValueSequence'):
            return
            
        measured_value = content_item.MeasuredValueSequence[0]
        if not hasattr(measured_value, 'NumericValue'):
            return
            
        num_value = measured_value.NumericValue
        
        # 단위 정보 추출
        unit_info = self._extract_code_sequence_info(measured_value, 'MeasurementUnitsCodeSequence')
        if unit_info:
            node.update({
                'UnitCodeMeaning': unit_info['CodeMeaning'],
                'UnitCodeValue': unit_info['CodeValue'],
                'UnitCodingSchemeDesignator': unit_info['CodingSchemeDesignator']
            })
        
        if name_info:
            node['value'] = f"{name_info['CodeMeaning']} : {num_value} ({name_info['CodeValue']} {name_info['CodingSchemeDesignator']})"
    
    def _handle_container_value(self, content_item, node, name_info):
        """CONTAINER 타입 값 처리"""
        if name_info:
            node['value'] = f"{name_info['CodeMeaning']} ({name_info['CodeValue']} {name_info['CodingSchemeDesignator']})"
    
    def _handle_default_value(self, content_item, node, name_info):
        """기본 ValueType 처리"""
        node['value'] = f"ValueType: {content_item.ValueType}"
    
    def get_tree(self):
        """
        파싱된 트리 구조를 반환합니다.
        
        Returns:
            dict: 트리 구조로 변환된 DICOM SR 데이터
        """
        return self.tree
    
    def search_in_tree(self, search_term):
        """
        트리에서 특정 텍스트를 검색합니다.
        
        Args:
            search_term (str): 검색할 텍스트
            
        Returns:
            list: 검색 결과 노드 리스트
        """
        if self.tree is None:
            self.logger.error("검색할 트리가 없습니다. 먼저 SR을 파싱하세요.")
            return []
        
        results = []
        self._search_node(self.tree, search_term.lower(), results)
        return results
    
    def _search_node(self, node, search_term, results):
        """
        노드에서 재귀적으로 검색합니다.
        
        Args:
            node (dict): 검색할 노드
            search_term (str): 검색할 텍스트
            results (list): 검색 결과를 저장할 리스트
        """
        # 현재 노드의 값에서 검색
        if 'value' in node and isinstance(node['value'], str) and search_term in node['value'].lower():
            results.append(node)
        
        # 자식 노드에서 재귀적으로 검색
        if 'children' in node:
            for child in node['children']:
                self._search_node(child, search_term, results)
    
    def _extract_code_sequence_info(self, item, sequence_name):
        """
        CodeSequence에서 정보를 추출합니다.
        
        Args:
            item: DICOM 아이템
            sequence_name (str): CodeSequence 이름
            
        Returns:
            dict: 추출된 코드 정보 또는 None
        """
        if not hasattr(item, sequence_name) or not getattr(item, sequence_name):
            return None
            
        try:
            code_seq = getattr(item, sequence_name)[0]
            info = {}
            
            # CodeMeaning 체크
            if (hasattr(code_seq, 'CodeMeaning') and 
                code_seq.CodeMeaning is not None and 
                str(code_seq.CodeMeaning).strip()):
                info['CodeMeaning'] = str(code_seq.CodeMeaning).strip()
            else:
                info['CodeMeaning'] = ""
                
            # CodeValue 체크
            if (hasattr(code_seq, 'CodeValue') and 
                code_seq.CodeValue is not None and 
                str(code_seq.CodeValue).strip()):
                info['CodeValue'] = str(code_seq.CodeValue).strip()
            else:
                info['CodeValue'] = ""
                
            # CodingSchemeDesignator 체크
            if (hasattr(code_seq, 'CodingSchemeDesignator') and 
                code_seq.CodingSchemeDesignator is not None and 
                str(code_seq.CodingSchemeDesignator).strip()):
                info['CodingSchemeDesignator'] = str(code_seq.CodingSchemeDesignator).strip()
            else:
                info['CodingSchemeDesignator'] = ""
                
            return info;
            
        except Exception as e:
            self.logger.error(f"Code Sequence 정보 추출 중 오류 발생: {e}")
            return None
