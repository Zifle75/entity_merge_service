from typing import Optional

from pydantic import BaseModel, Field

# Address model as described in initial scenario.
class Address(BaseModel):
    line_1: str
    line_2: Optional[str] = None
    state: str
    city: str
    postal_code: str

# Address model as described in initial scenario, with the additional credit_limit field mentioned down the line.
class Company(BaseModel):
    id: str
    name: str
    address: Address
    credit_limit: Optional[int] = None
    is_deleted: bool = False

# User model as described in initial scenario.
class User(BaseModel):
    id: str
    first_name: str
    last_name: str
    company_id: str

# Branch model as described in intial scenario.
class Branch(BaseModel):
    id: str
    name: str
    company_id: str

# Dumbed down draft so the user can't specify fields like id or is_deleted.
class CompanyDraft(BaseModel):
    name: str
    address: Address
    credit_limit: Optional[int] = None

# Request model for backend merge endpoint
class MergeCompaniesRequest(BaseModel):
    source_company_1_id: str = Field(min_length=1)
    source_company_2_id: str = Field(min_length=1)
    resolved_company: CompanyDraft

# Response model for backend merge endpoint
class MergeCompaniesResponse(BaseModel):
    merged_company_id: str
    source_company_1_id: str
    source_company_2_id: str
    status: str
