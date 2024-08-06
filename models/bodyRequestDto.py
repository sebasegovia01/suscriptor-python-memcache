from pydantic import BaseModel, Field
from datetime import time
from typing import Optional, Tuple


class AutomatedTellerMachines(BaseModel):
    ATMIdentifier: Optional[str] = Field(examples="ATM0003", default=None)
    ATMAddress_StreetName: Optional[str] = Field(
        examples="Av. Vicuña Mackenna Ote", default=None
    )
    ATMAddress_BuildingNumber: Optional[str] = Field(examples="6100", default=None)
    ATMTownName: Optional[str] = Field(examples="Talca", default=None)
    ATMDistrictName: Optional[str] = Field(examples="Las Condes", default=None)
    ATMCountrySubDivisionMajorName: Optional[str] = Field(
        examples="Región de Los Ríos", default=None
    )
    ATMFromDatetime: Optional[time] = Field(examples="08:00:00", default=None)
    ATMToDatetime: Optional[time] = Field(examples="15:00:00", default=None)
    ATMTimeType: Optional[str] = Field(examples="CONT", default=None)
    ATMAttentionHour: Optional[Tuple[time, time]] = Field(
        examples="08:00:00 - 15:00:00", default=None
    )
    ATMServiceType: Optional[str] = Field(examples="DPST", default=None)
    ATMAccessType: Optional[str] = Field(examples="BRAN", default=None)


class bodyRequestDto(BaseModel):
    AutomatedTellerMachines: AutomatedTellerMachines
