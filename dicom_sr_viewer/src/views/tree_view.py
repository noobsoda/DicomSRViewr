"""
DICOM SR 트리 뷰 모듈
DICOM SR 데이터를 트리 형태로 시각화하는 기능을 제공합니다.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

class DicomSRTreeView(QWidget):
    """DICOM SR 데이터를 트리 형태로 시각화하는 위젯"""
    
    # 노드 선택 시 발생하는 시그널
    node_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """DicomSRTreeView 클래스 초기화"""
        super().__init__(parent)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["항목", "값"])
        self.tree_widget.setColumnWidth(0, 300)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)
        
        # 트리 아이템 선택 시 이벤트 연결
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        
        # 노드 데이터를 저장할 딕셔너리
        self.node_data = {}
    
    def set_tree_data(self, tree_data):
        """
        트리 데이터를 설정하고 트리 위젯을 업데이트합니다.
        
        Args:
            tree_data (dict): 트리 구조의 DICOM SR 데이터
        """
        if tree_data is None:
            return
        
        # 트리 위젯 초기화
        self.tree_widget.clear()
        self.node_data = {}
        
        # 루트 노드 생성
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, tree_data.get('value', 'DICOM SR Document'))
        root_item.setText(1, "")
        
        # 노드 ID와 트리 아이템 연결
        self.node_data[id(root_item)] = tree_data
        
        # 자식 노드 추가
        if 'children' in tree_data:
            self._add_children(root_item, tree_data['children'])
        
        # 트리 확장
        self.tree_widget.expandAll()
    
    def _add_children(self, parent_item, children):
        """
        부모 아이템에 자식 노드를 추가합니다.
        
        Args:
            parent_item (QTreeWidgetItem): 부모 트리 아이템
            children (list): 자식 노드 리스트
        """
        for child in children:
            item = QTreeWidgetItem(parent_item)
            
            # 노드 타입과 값 표시
            node_type = child.get('type', '')
            node_value = child.get('value', '')
            
            # 관계 정보가 있으면 표시
            relationship = child.get('relationship', '')
            display_text = f"{node_type}"
            if relationship:
                display_text = f"{relationship}: {display_text}"
            
            item.setText(0, display_text)
            item.setText(1, str(node_value))
            
            # 노드 ID와 트리 아이템 연결
            self.node_data[id(item)] = child
            
            # 자식 노드가 있으면 재귀적으로 추가
            if 'children' in child and child['children']:
                self._add_children(item, child['children'])
    
    def _on_item_clicked(self, item, column):
        """
        트리 아이템 클릭 이벤트 핸들러
        
        Args:
            item (QTreeWidgetItem): 클릭된 트리 아이템
            column (int): 클릭된 컬럼 인덱스
        """
        # 아이템에 연결된 노드 데이터 가져오기
        node_data = self.node_data.get(id(item))
        if node_data:
            # 노드 선택 시그널 발생
            self.node_selected.emit(node_data)
    
    def highlight_search_results(self, search_results):
        """
        검색 결과를 하이라이트합니다.
        
        Args:
            search_results (list): 검색 결과 노드 리스트
        """
        # 모든 아이템의 배경색 초기화
        self._reset_highlight()
        
        if not search_results:
            return
        
        # 검색 결과에 해당하는 아이템 찾아서 하이라이트
        for item in self._get_all_items():
            node_data = self.node_data.get(id(item))
            if node_data in search_results:
                # 검색 결과 하이라이트
                item.setBackground(0, Qt.yellow)
                item.setBackground(1, Qt.yellow)
                
                # 부모 아이템들 확장
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()
    
    def _reset_highlight(self):
        """모든 아이템의 배경색을 초기화합니다."""
        for item in self._get_all_items():
            item.setBackground(0, Qt.transparent)
            item.setBackground(1, Qt.transparent)
    
    def _get_all_items(self):
        """
        트리 위젯의 모든 아이템을 반환합니다.
        
        Returns:
            list: 모든 트리 아이템 리스트
        """
        all_items = []
        
        # 루트 아이템 가져오기
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            all_items.append(top_item)
            self._get_child_items(top_item, all_items)
        
        return all_items
    
    def _get_child_items(self, parent_item, items_list):
        """
        부모 아이템의 모든 자식 아이템을 재귀적으로 가져옵니다.
        
        Args:
            parent_item (QTreeWidgetItem): 부모 트리 아이템
            items_list (list): 아이템을 추가할 리스트
        """
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            items_list.append(child)
            self._get_child_items(child, items_list)
