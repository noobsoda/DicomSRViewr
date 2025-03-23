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
            # DICOM SR 문서의 루트 노드 생성
            self.tree = {
                'id': 'root',
                'type': 'root',
                'value': 'DICOM SR Document',
                'children': []
            }
            
            # Content Sequence가 있는지 확인
            if hasattr(self.dataset, 'ContentSequence'):
                self._parse_content_sequence(self.dataset.ContentSequence, self.tree['children'])
            else:
                self.logger.warning("ContentSequence를 찾을 수 없습니다. SR 문서가 아닐 수 있습니다.")
            
            return self.tree
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
        
        # ValueType에 따라 노드 정보 설정
        if hasattr(content_item, 'ValueType'):
            node['type'] = content_item.ValueType
            
            # ValueType에 따라 값 추출
            if content_item.ValueType == 'TEXT':
                if hasattr(content_item, 'TextValue'):
                    node['value'] = content_item.TextValue
            elif content_item.ValueType == 'CODE':
                if hasattr(content_item, 'ConceptNameCodeSequence'):
                    code_seq = content_item.ConceptNameCodeSequence[0]
                    node['value'] = f"{code_seq.CodeMeaning} ({code_seq.CodeValue})"
            elif content_item.ValueType == 'NUM':
                if hasattr(content_item, 'MeasuredValueSequence'):
                    measured_value = content_item.MeasuredValueSequence[0]
                    if hasattr(measured_value, 'NumericValue'):
                        node['value'] = measured_value.NumericValue
            elif content_item.ValueType == 'CONTAINER':
                if hasattr(content_item, 'ConceptNameCodeSequence'):
                    code_seq = content_item.ConceptNameCodeSequence[0]
                    node['value'] = code_seq.CodeMeaning
            else:
                node['value'] = f"ValueType: {content_item.ValueType}"
        else:
            node['type'] = 'UNKNOWN'
            node['value'] = 'Unknown content item'
        
        # 관계 정보 추가
        if hasattr(content_item, 'RelationshipType'):
            node['relationship'] = content_item.RelationshipType
        
        return node
    
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
