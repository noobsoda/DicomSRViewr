import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from pydicom.sequence import Sequence

# Create a new DICOM SR file
file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'  # SOP Class UID for SR
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian

# Create the main dataset
ds = FileDataset('dicomSR.dcm', {}, file_meta=file_meta, preamble=b"\0" * 128)
ds.PatientName = "Test^Patient"
ds.PatientID = "123456"
ds.Modality = "SR"
ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'  # SOP Class UID for SR
ds.SOPInstanceUID = generate_uid()

# Root container
root_container = Dataset()
root_container.ValueType = "CONTAINER"
root_container.ContinuityOfContent = "SEPARATE"
root_container.ConceptNameCodeSequence = [Dataset()]
root_container.ConceptNameCodeSequence[0].CodeValue = "121139"
root_container.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
root_container.ConceptNameCodeSequence[0].CodeMeaning = "Imaging Measurement Report"

# Depth 1: Measurement Group
measurement_group = Dataset()
measurement_group.ValueType = "CONTAINER"
measurement_group.ContinuityOfContent = "SEPARATE"
measurement_group.ConceptNameCodeSequence = [Dataset()]
measurement_group.ConceptNameCodeSequence[0].CodeValue = "125007"
measurement_group.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
measurement_group.ConceptNameCodeSequence[0].CodeMeaning = "Measurement Group"

# Depth 2: Finding
finding = Dataset()
finding.ValueType = "TEXT"
finding.ConceptNameCodeSequence = [Dataset()]
finding.ConceptNameCodeSequence[0].CodeValue = "121071"
finding.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
finding.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
finding.TextValue = "Abnormal finding detected."

# Depth 3: Measurement
measurement = Dataset()
measurement.ValueType = "NUM"
measurement.ConceptNameCodeSequence = [Dataset()]
measurement.ConceptNameCodeSequence[0].CodeValue = "112039"
measurement.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
measurement.ConceptNameCodeSequence[0].CodeMeaning = "Measurement"
measurement.MeasuredValueSequence = [Dataset()]
measurement.MeasuredValueSequence[0].NumericValue = 10.5
measurement.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = [Dataset()]
measurement.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeValue = "mm"
measurement.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodingSchemeDesignator = "UCUM"
measurement.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeMeaning = "millimeter"

# Depth 4: Conclusion
conclusion = Dataset()
conclusion.ValueType = "TEXT"
conclusion.ConceptNameCodeSequence = [Dataset()]
conclusion.ConceptNameCodeSequence[0].CodeValue = "121070"
conclusion.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
conclusion.ConceptNameCodeSequence[0].CodeMeaning = "Conclusion"
conclusion.TextValue = "Further investigation required."

# Build the hierarchy
measurement.ContentSequence = [conclusion]  # Depth 4 under Depth 3
finding.ContentSequence = [measurement]     # Depth 3 under Depth 2
measurement_group.ContentSequence = [finding]  # Depth 2 under Depth 1
root_container.ContentSequence = [measurement_group]  # Depth 1 under Root

# Add the root container to the dataset
ds.ContentSequence = [root_container]

# Save the DICOM SR file
ds.save_as("dicomSR.dcm")
print("DICOM SR file created: dicomSR.dcm")