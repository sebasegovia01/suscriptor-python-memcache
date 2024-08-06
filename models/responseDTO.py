from pydantic import BaseModel, Field
from datetime import time
from typing import Optional, Tuple


class AutomatedTellerMachines(BaseModel):
    ATMIdentifier: Optional[str] = Field(default=None, example="ATM0003")
    ATMAddress_StreetName: Optional[str] = Field(
        default=None, example="Av. Vicuña Mackenna Ote"
    )
    ATMAddress_BuildingNumber: Optional[str] = Field(default=None, example="6100")
    ATMTownName: Optional[str] = Field(default=None, example="Talca")
    ATMDistrictName: Optional[str] = Field(default=None, example="Las Condes")
    ATMCountrySubDivisionMajorName: Optional[str] = Field(
        default=None, example="Región de Los Ríos"
    )
    ATMFromDatetime: Optional[time] = Field(default=None, example="08:00:00")
    ATMToDatetime: Optional[time] = Field(default=None, example="15:00:00")
    ATMTimeType: Optional[str] = Field(default=None, example="CONT")
    ATMAttentionHour: Optional[Tuple[time, time]] = Field(
        default=None, example="08:00:00 - 15:00:00"
    )
    ATMServiceType: Optional[str] = Field(default=None, example="DPST")
    ATMAccessType: Optional[str] = Field(default=None, example="BRAN")


class ResponseDTO(BaseModel):
    AutomatedTellerMachines: AutomatedTellerMachines
