"""
메인 애플리케이션 모듈
DICOM SR 뷰어의 메인 애플리케이션 클래스를 제공합니다.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                            QLineEdit, QStatusBar, QSplitter, QFrame)
from PyQt5.QtCore import Qt

# 모델 및 뷰 모듈 임포트
from models.dicom_sr_parser import DicomSRParser
from models.search import DicomSRSearcher
from views.tree_view import DicomSRTreeView

class DicomSRViewer(QMainWindow):
    """DICOM SR 뷰어 메인 애플리케이션 클래스"""
    
    def __init__(self):
        """DicomSRViewer 클래스 초기화"""
        super().__init__()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('DicomSRViewer')
        
        # 모델 초기화
        self.sr_parser = DicomSRParser()
        self.sr_searcher = DicomSRSearcher(self.sr_parser)
        
        # UI 초기화
        self.init_ui()
        
        # 현재 로드된 파일 경로
        self.current_file = None
    
    def init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle('DICOM SR 뷰어')
        self.setGeometry(100, 100, 1000, 800)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 툴바 레이아웃
        toolbar_layout = QHBoxLayout()
        
        # 파일 열기 버튼
        self.open_button = QPushButton('파일 열기')
        self.open_button.clicked.connect(self.open_file)
        toolbar_layout.addWidget(self.open_button)
        
        # 검색 입력창
        self.search_label = QLabel('검색:')
        toolbar_layout.addWidget(self.search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('검색어 입력')
        self.search_input.returnPressed.connect(self.search_text)
        toolbar_layout.addWidget(self.search_input)
        
        # 검색 버튼
        self.search_button = QPushButton('검색')
        self.search_button.clicked.connect(self.search_text)
        toolbar_layout.addWidget(self.search_button)
        
        # 툴바 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(toolbar_layout)
        
        # 스플리터 생성
        splitter = QSplitter(Qt.Horizontal)
        
        # 트리 뷰 위젯
        self.tree_view = DicomSRTreeView()
        splitter.addWidget(self.tree_view)
        
        # 상세 정보 패널
        self.detail_panel = QFrame()
        self.detail_panel.setFrameShape(QFrame.StyledPanel)
        self.detail_layout = QVBoxLayout(self.detail_panel)
        
        self.detail_title = QLabel('상세 정보')
        self.detail_title.setStyleSheet('font-weight: bold; font-size: 14px;')
        self.detail_layout.addWidget(self.detail_title)
        
        self.detail_content = QLabel('노드를 선택하면 상세 정보가 표시됩니다.')
        self.detail_layout.addWidget(self.detail_content)
        self.detail_layout.addStretch()
        
        splitter.addWidget(self.detail_panel)
        
        # 스플리터 비율 설정
        splitter.setSizes([600, 400])
        
        # 스플리터를 메인 레이아웃에 추가
        main_layout.addWidget(splitter)
        
        # 상태 바 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('준비됨')
        
        # 트리 노드 선택 이벤트 연결
        self.tree_view.node_selected.connect(self.show_node_details)
    
    def open_file(self):
        """DICOM SR 파일 열기 대화상자 표시"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '파일 열기', '', 'DICOM 파일 (*.dcm);;모든 파일 (*.*)'
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """
        DICOM SR 파일 로드 및 파싱
        
        Args:
            file_path (str): DICOM SR 파일 경로
        """
        self.status_bar.showMessage(f'파일 로드 중: {file_path}')
        
        # 파일 로드
        if self.sr_parser.load_file(file_path):
            # SR 파싱
            tree_data = self.sr_parser.parse_sr()
            
            if tree_data:
                # 트리 뷰 업데이트
                self.tree_view.set_tree_data(tree_data)
                
                # 현재 파일 경로 저장
                self.current_file = file_path
                
                file_name = os.path.basename(file_path)
                self.status_bar.showMessage(f'파일 로드 완료: {file_name}')
                self.setWindowTitle(f'DICOM SR 뷰어 - {file_name}')
            else:
                self.status_bar.showMessage('SR 파싱 실패')
        else:
            self.status_bar.showMessage('파일 로드 실패')
    
    def search_text(self):
        """검색 기능 실행"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.status_bar.showMessage('검색어를 입력하세요')
            return
        
        if not self.current_file:
            self.status_bar.showMessage('먼저 DICOM SR 파일을 로드하세요')
            return
        
        # 검색 실행
        search_results = self.sr_searcher.search(search_term)
        
        # 검색 결과 하이라이트
        self.tree_view.highlight_search_results(search_results)
        
        # 상태 바 업데이트
        result_count = len(search_results)
        self.status_bar.showMessage(f'검색 결과: {result_count}개 항목 발견')
    
    def show_node_details(self, node_data):
        """
        선택한 노드의 상세 정보 표시
        
        Args:
            node_data (dict): 노드 데이터
        """
        if not node_data:
            return
        
        # 상세 정보 텍스트 생성
        details = f"<h3>노드 정보</h3>"
        
        if 'type' in node_data:
            details += f"<p><b>타입:</b> {node_data['type']}</p>"
        
        if 'value' in node_data:
            details += f"<p><b>값:</b> {node_data['value']}</p>"
        
        if 'relationship' in node_data:
            details += f"<p><b>관계:</b> {node_data['relationship']}</p>"
        
        if 'id' in node_data:
            details += f"<p><b>ID:</b> {node_data['id']}</p>"
        
        # 자식 노드 수 표시
        children_count = len(node_data.get('children', []))
        details += f"<p><b>자식 노드:</b> {children_count}개</p>"
        
        # 상세 정보 패널 업데이트
        self.detail_content.setText(details)
        self.detail_content.setTextFormat(Qt.RichText)

def main():
    """애플리케이션 메인 함수"""
    app = QApplication(sys.argv)
    viewer = DicomSRViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
