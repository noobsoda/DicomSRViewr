"""
검색 기능 모듈
DICOM SR 데이터에서 텍스트 검색 기능을 제공합니다.
"""

class DicomSRSearcher:
    """DICOM SR 데이터에서 텍스트 검색 기능을 제공하는 클래스"""
    
    def __init__(self, sr_parser=None):
        """
        DicomSRSearcher 클래스 초기화
        
        Args:
            sr_parser (DicomSRParser, optional): DICOM SR 파서 인스턴스
        """
        self.sr_parser = sr_parser
    
    def set_parser(self, sr_parser):
        """
        DICOM SR 파서를 설정합니다.
        
        Args:
            sr_parser (DicomSRParser): DICOM SR 파서 인스턴스
        """
        self.sr_parser = sr_parser
    
    def search(self, search_term):
        """
        DICOM SR 데이터에서 텍스트를 검색합니다.
        
        Args:
            search_term (str): 검색할 텍스트
            
        Returns:
            list: 검색 결과 노드 리스트
        """
        if self.sr_parser is None:
            return []
        
        return self.sr_parser.search_in_tree(search_term)
    
    def search_by_type(self, node_type):
        """
        특정 타입의 노드를 검색합니다.
        
        Args:
            node_type (str): 검색할 노드 타입 (예: 'TEXT', 'CODE', 'NUM', 'CONTAINER')
            
        Returns:
            list: 검색 결과 노드 리스트
        """
        if self.sr_parser is None or self.sr_parser.get_tree() is None:
            return []
        
        results = []
        self._search_by_type_recursive(self.sr_parser.get_tree(), node_type.upper(), results)
        return results
    
    def _search_by_type_recursive(self, node, node_type, results):
        """
        노드에서 재귀적으로 특정 타입의 노드를 검색합니다.
        
        Args:
            node (dict): 검색할 노드
            node_type (str): 검색할 노드 타입
            results (list): 검색 결과를 저장할 리스트
        """
        # 현재 노드의 타입 확인
        if 'type' in node and node['type'] == node_type:
            results.append(node)
        
        # 자식 노드에서 재귀적으로 검색
        if 'children' in node:
            for child in node['children']:
                self._search_by_type_recursive(child, node_type, results)
    
    def search_by_relationship(self, relationship_type):
        """
        특정 관계 타입의 노드를 검색합니다.
        
        Args:
            relationship_type (str): 검색할 관계 타입 (예: 'CONTAINS', 'HAS OBS CONTEXT')
            
        Returns:
            list: 검색 결과 노드 리스트
        """
        if self.sr_parser is None or self.sr_parser.get_tree() is None:
            return []
        
        results = []
        self._search_by_relationship_recursive(self.sr_parser.get_tree(), relationship_type.upper(), results)
        return results
    
    def _search_by_relationship_recursive(self, node, relationship_type, results):
        """
        노드에서 재귀적으로 특정 관계 타입의 노드를 검색합니다.
        
        Args:
            node (dict): 검색할 노드
            relationship_type (str): 검색할 관계 타입
            results (list): 검색 결과를 저장할 리스트
        """
        # 현재 노드의 관계 타입 확인
        if 'relationship' in node and node['relationship'] == relationship_type:
            results.append(node)
        
        # 자식 노드에서 재귀적으로 검색
        if 'children' in node:
            for child in node['children']:
                self._search_by_relationship_recursive(child, relationship_type, results)
    
    def advanced_search(self, criteria):
        """
        여러 기준으로 고급 검색을 수행합니다.
        
        Args:
            criteria (dict): 검색 기준 (예: {'text': '검색어', 'type': 'TEXT', 'relationship': 'CONTAINS'})
            
        Returns:
            list: 검색 결과 노드 리스트
        """
        if self.sr_parser is None or self.sr_parser.get_tree() is None:
            return []
        
        # 초기 결과는 모든 노드
        all_nodes = []
        self._collect_all_nodes(self.sr_parser.get_tree(), all_nodes)
        
        results = all_nodes
        
        # 텍스트 검색
        if 'text' in criteria and criteria['text']:
            text_results = []
            for node in results:
                if 'value' in node and isinstance(node['value'], str) and criteria['text'].lower() in node['value'].lower():
                    text_results.append(node)
            results = text_results
        
        # 타입 검색
        if 'type' in criteria and criteria['type']:
            type_results = []
            for node in results:
                if 'type' in node and node['type'] == criteria['type'].upper():
                    type_results.append(node)
            results = type_results
        
        # 관계 검색
        if 'relationship' in criteria and criteria['relationship']:
            rel_results = []
            for node in results:
                if 'relationship' in node and node['relationship'] == criteria['relationship'].upper():
                    rel_results.append(node)
            results = rel_results
        
        return results
    
    def _collect_all_nodes(self, node, nodes_list):
        """
        모든 노드를 수집합니다.
        
        Args:
            node (dict): 시작 노드
            nodes_list (list): 노드를 저장할 리스트
        """
        nodes_list.append(node)
        
        if 'children' in node:
            for child in node['children']:
                self._collect_all_nodes(child, nodes_list)
