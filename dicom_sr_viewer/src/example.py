import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from pydicom.sequence import Sequence

# 1. DICOM SR 파일 메타데이터 설정
file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'  # SR SOP Class
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian

# 2. 기본 DICOM 속성 설정
ds = FileDataset('structured_report.dcm', {}, file_meta=file_meta, preamble=b"\0" * 128)
ds.PatientName = "Complex^SR^Test"
ds.PatientID = "SR-12345"
ds.Modality = "SR"
ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'
ds.SOPInstanceUID = generate_uid()

# 3. 계층 구조 생성 (4-depth + 형제 노드)
# ------------------------------------------------------------
### Depth 1: Root Container (보고서 최상위)
root = Dataset()
root.ValueType = "CONTAINER"
root.ContinuityOfContent = "SEPARATE"
root.ConceptNameCodeSequence = [Dataset()]
root.ConceptNameCodeSequence[0].CodeValue = "121139"
root.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
root.ConceptNameCodeSequence[0].CodeMeaning = "Imaging Report"

### Depth 2: 형제 노드 2개 (1. Findings / 2. Measurements)
# --- 형제 노드 1: Findings Section ---
section_findings = Dataset()
section_findings.ValueType = "CONTAINER"
section_findings.ConceptNameCodeSequence = [Dataset()]
section_findings.ConceptNameCodeSequence[0].CodeValue = "123456"
section_findings.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
section_findings.ConceptNameCodeSequence[0].CodeMeaning = "Findings Section"

# --- 형제 노드 2: Measurements Section ---
section_measurements = Dataset()
section_measurements.ValueType = "CONTAINER"
section_measurements.ConceptNameCodeSequence = [Dataset()]
section_measurements.ConceptNameCodeSequence[0].CodeValue = "789012"
section_measurements.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
section_measurements.ConceptNameCodeSequence[0].CodeMeaning = "Measurements Section"

### Depth 3: Findings Section 하위 노드 (형제 노드 3개)
# --- 노드 1: 텍스트 설명 ---
finding1 = Dataset()
finding1.ValueType = "TEXT"
finding1.ConceptNameCodeSequence = [Dataset()]
finding1.ConceptNameCodeSequence[0].CodeValue = "111001"
finding1.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
finding1.ConceptNameCodeSequence[0].CodeMeaning = "Description"
finding1.TextValue = "Mass detected in the right lung."

# --- 노드 2: 코드화된 진단 ---
finding2 = Dataset()
finding2.ValueType = "CODE"
finding2.ConceptNameCodeSequence = [Dataset()]
finding2.ConceptNameCodeSequence[0].CodeValue = "111002"
finding2.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
finding2.ConceptNameCodeSequence[0].CodeMeaning = "Diagnosis Code"
finding2.ConceptCodeSequence = [Dataset()]
finding2.ConceptCodeSequence[0].CodeValue = "RID1032"
finding2.ConceptCodeSequence[0].CodingSchemeDesignator = "RADLEX"
finding2.ConceptCodeSequence[0].CodeMeaning = "Pulmonary Nodule"

# --- 노드 3: 이미지 참조 (예: DICOM 이미지 연결) ---
finding3 = Dataset()
finding3.ValueType = "IMAGE"
finding3.ReferencedSOPSequence = [Dataset()]
finding3.ReferencedSOPSequence[0].ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"  # CT Image
finding3.ReferencedSOPSequence[0].ReferencedSOPInstanceUID = generate_uid()  # 실제 UID로 교체 필요

### Depth 4: Measurements Section 하위 노드 (형제 노드 2개)
# --- 노드 1: 측정값 ---
measurement1 = Dataset()
measurement1.ValueType = "NUM"
measurement1.ConceptNameCodeSequence = [Dataset()]
measurement1.ConceptNameCodeSequence[0].CodeValue = "112039"
measurement1.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
measurement1.ConceptNameCodeSequence[0].CodeMeaning = "Size"
measurement1.MeasuredValueSequence = [Dataset()]
measurement1.MeasuredValueSequence[0].NumericValue = 8.2
measurement1.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = [Dataset()]
measurement1.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeValue = "mm"
measurement1.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodingSchemeDesignator = "UCUM"

# --- 노드 2: 측정 방법 ---
measurement2 = Dataset()
measurement2.ValueType = "TEXT"
measurement2.ConceptNameCodeSequence = [Dataset()]
measurement2.ConceptNameCodeSequence[0].CodeValue = "111003"
measurement2.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
measurement2.ConceptNameCodeSequence[0].CodeMeaning = "Method"
measurement2.TextValue = "Automated segmentation"

# 4. 계층 구조 연결
# ------------------------------------------------------------
section_findings.ContentSequence = [finding1, finding2, finding3]  # Depth 3
section_measurements.ContentSequence = [measurement1, measurement2]  # Depth 3
root.ContentSequence = [section_findings, section_measurements]  # Depth 2
ds.ContentSequence = [root]  # Depth 1 (Root)

# 5. 파일 저장
ds.save_as("structured_report.dcm")
print("✅ DICOM SR 파일 생성 완료: structured_report.dcm")