from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class SignalType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    RISK = "RISK"
    MARKET = "MARKET"

class Signal(BaseModel):
    """
    Structured model representing a parsed market or news signal.
    """
    signal_type: SignalType = Field(..., description="Category of the signal: POSITIVE, NEGATIVE, RISK, or MARKET")
    title: str = Field(..., description="Short name of the signal event")
    description: str = Field(..., description="Detailed explanation of the signal")
    score: float = Field(default=0.0, description="Calculated score weight assigned by the system")
    citation_ids: List[int] = Field(..., description="Source citation IDs referenced as evidence")

class SignalExtractionResponse(BaseModel):
    """
    Full JSON schema wrapper expected back from the LLM for signal extraction.
    """
    signals: List[Signal] = Field(..., description="List of signals extracted from the context")
    reasoning: str = Field(..., description="A concise summary of how the signals combine to describe the situation")
