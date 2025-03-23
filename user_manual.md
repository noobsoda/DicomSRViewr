"""
DICOM SR 뷰어 사용 설명서
"""

# DICOM SR 뷰어 사용 설명서

## 소개

DICOM SR(Structured Report) 뷰어는 병원에서 사용하는 DICOM SR 파일을 트리 형태로 시각화하고 검색할 수 있는 도구입니다. 이 애플리케이션은 Python과 PyQt5를 사용하여 개발되었으며, DICOM SR 파일의 구조화된 데이터를 쉽게 탐색할 수 있는 인터페이스를 제공합니다.

## 주요 기능

- DICOM SR 파일 로드 및 파싱
- 트리 형태로 SR 데이터 시각화
- 노드 확장/축소 기능
- 텍스트 검색 기능
- 검색 결과 하이라이팅
- 노드 선택 시 상세 정보 표시

## 설치 방법

### 필수 요구사항

- Python 3.6 이상
- 다음 Python 라이브러리:
  - pydicom
  - numpy
  - matplotlib
  - PyQt5

### 설치 단계

1. 필요한 라이브러리 설치:
```bash
pip install pydicom numpy matplotlib PyQt5
```

2. 소스 코드 다운로드:
```bash
git clone https://github.com/yourusername/dicom-sr-viewer.git
cd dicom-sr-viewer
```

## 사용 방법

### 애플리케이션 실행

```bash
python src/main.py
```

### DICOM SR 파일 열기

1. 애플리케이션 실행 후 상단의 '파일 열기' 버튼을 클릭합니다.
2. 파일 선택 대화상자에서 DICOM SR 파일(.dcm)을 선택합니다.
3. 파일이 로드되면 트리 뷰에 DICOM SR 데이터가 표시됩니다.

### 트리 탐색

- 트리 노드 옆의 '+' 또는 '-' 아이콘을 클릭하여 노드를 확장하거나 축소할 수 있습니다.
- 노드를 클릭하면 오른쪽 패널에 해당 노드의 상세 정보가 표시됩니다.
- 트리는 기본적으로 모두 확장된 상태로 표시됩니다.

### 검색 기능 사용

1. 상단의 검색 입력창에 검색어를 입력합니다.
2. '검색' 버튼을 클릭하거나 Enter 키를 누릅니다.
3. 검색 결과가 트리 뷰에서 노란색으로 하이라이트됩니다.
4. 검색 결과가 있는 노드의 부모 노드들은 자동으로 확장됩니다.
5. 상태 바에 검색 결과 수가 표시됩니다.

## 프로젝트 구조

```
dicom_sr_viewer/
├── src/
│   ├── models/
│   │   ├── dicom_sr_parser.py  # DICOM SR 파일 파싱 모듈
│   │   └── search.py           # 검색 기능 모듈
│   ├── views/
│   │   └── tree_view.py        # 트리 뷰 UI 컴포넌트
│   ├── controllers/
│   │   └── (향후 확장용)
│   └── main.py                 # 메인 애플리케이션
├── data/
│   └── sample/                 # 샘플 DICOM SR 파일
└── docs/
    └── user_manual.md          # 사용자 매뉴얼
```

## 문제 해결

### 파일 로드 실패

- DICOM 파일 형식이 올바른지 확인하세요.
- 파일이 DICOM SR(Structured Report) 형식인지 확인하세요.
- 파일이 손상되지 않았는지 확인하세요.

### 트리 뷰가 비어 있음

- 로드한 파일이 DICOM SR 형식이 맞는지 확인하세요.
- 파일에 ContentSequence가 포함되어 있는지 확인하세요.
- 상태 바에 표시된 오류 메시지를 확인하세요.

## 향후 개선 사항

- 여러 DICOM SR 파일 동시 비교 기능
- 고급 검색 필터링 옵션
- DICOM SR 파일 편집 및 저장 기능
- 다양한 DICOM SR 템플릿 지원 확장
- 국제화 및 다국어 지원

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 연락처

문제 보고 또는 기능 요청은 GitHub 이슈 트래커를 통해 제출해 주세요.
