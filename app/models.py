"""
Models và Schemas cho Medical Device Management System
"""
from enum import Enum
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ResultStatus(str, Enum):
    OK = "OK"
    NG = "NG"
    PENDING = "PENDING"


class MaintenanceStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class MaintenanceType(str, Enum):
    CALIBRATION = "CALIBRATION"
    REPAIR = "REPAIR"
    PREVENTIVE = "PREVENTIVE"
    INSPECTION = "INSPECTION"
    HANDOVER = "HANDOVER"


class DeviceStatusEnum(str, Enum):
    IN_SERVICE = "IN_SERVICE"
    CALIBRATION_DUE = "CALIBRATION_DUE"
    MAINTENANCE = "MAINTENANCE"
    REPAIR = "REPAIR"
    RETIRED = "RETIRED"


# Schema cho thiết bị
class DeviceBase(BaseModel):
    device_name: str
    model: str
    serial_no: str
    certification_no: Optional[str] = None
    calibration_stamp_no: Optional[str] = None
    facility_id: Optional[int] = None
    category_id: Optional[int] = None
    manufacturer: Optional[str] = None
    country_of_manufacturer: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = "IN_SERVICE"
    installation_date: Optional[date] = None
    calibration_date: Optional[date] = None
    recalibration_date: Optional[date] = None
    source_pdf: Optional[str] = None
    pdf_path: Optional[str] = None
    md_path: Optional[str] = None
    notes: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    model: Optional[str] = None
    serial_no: Optional[str] = None
    certification_no: Optional[str] = None
    calibration_stamp_no: Optional[str] = None
    facility_id: Optional[int] = None
    category_id: Optional[int] = None
    manufacturer: Optional[str] = None
    country_of_manufacturer: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    calibration_date: Optional[date] = None
    recalibration_date: Optional[date] = None
    notes: Optional[str] = None


class Device(DeviceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    facility: Optional[str] = None
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Schema cho giấy chứng nhận
class CalibrationCertificateBase(BaseModel):
    certificate_no: str
    calibration_date: date
    recalibration_date: Optional[date] = None
    stamp_no: Optional[str] = None
    result_status: ResultStatus = ResultStatus.OK
    uncertainty: Optional[float] = None
    standard_reference: Optional[str] = None
    calibrated_by: Optional[str] = None
    source_pdf: Optional[str] = None
    pdf_path: Optional[str] = None
    notes: Optional[str] = None


class CalibrationCertificateCreate(CalibrationCertificateBase):
    device_id: int


class CalibrationCertificate(CalibrationCertificateBase):
    id: int
    device_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Schema cho dashboard
class DeviceSummary(BaseModel):
    total_devices: int
    overdue_count: int
    warning_count: int
    ok_count: int
    in_service_count: int = 0
    repair_count: int = 0


class DeviceStatus(BaseModel):
    id: int
    device_name: str
    model: str
    serial_no: str
    manufacturer: Optional[str] = None
    country_of_manufacturer: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = "IN_SERVICE"
    facility: Optional[str] = None
    category: Optional[str] = None
    calibration_date: Optional[date] = None
    recalibration_date: Optional[date] = None
    certificate_no: Optional[str] = None
    stamp_no: Optional[str] = None
    result_status: Optional[str] = None
    alert_status: str  # OVERDUE, WARNING, OK, NO_DATA
    source_pdf: Optional[str] = None
    pdf_path: Optional[str] = None


# Schema cho điều chuyển thiết bị (QT.08)
class DeviceTransferCreate(BaseModel):
    device_id: int
    to_facility_id: int
    from_facility_id: Optional[int] = None
    giver_name: Optional[str] = ""
    receiver_name: Optional[str] = ""
    transfer_reason: Optional[str] = ""
    transfer_date: Optional[str] = None
    form_code: Optional[str] = "BM08_TA5.TTBYT.QT.08"