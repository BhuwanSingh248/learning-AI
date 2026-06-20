import json
from typing import List, Optional
from src.config.logger import setup_logger
from src.signals.models import Signal, SignalExtractionResponse, SignalType

logger = setup_logger(__name__)

class SignalEngine:
    """
    Parses and sanitizes LLM-extracted signals, validating types and cleaning citation references.
    """
    @staticmethod
    def extract_signals(raw_response: str, available_citation_ids: Optional[List[int]] = None) -> SignalExtractionResponse:
        """
        Parses raw LLM JSON response into a validated SignalExtractionResponse structure,
        applying citation sanitation and fallback mechanisms.
        """
        logger.info("SignalEngine | Extracting signals from raw LLM response")
        allowed_citations = available_citation_ids or []
        
        try:
            parsed = json.loads(raw_response)
            
            # Extract reasoning
            reasoning = parsed.get("reasoning", "No summary reasoning provided by the analyst.")
            
            # Parse signals
            raw_signals = parsed.get("signals", [])
            valid_signals = []
            
            if isinstance(raw_signals, list):
                for rs in raw_signals:
                    try:
                        # Extract and validate signal type
                        sig_type_str = rs.get("signal_type", "").upper().strip()
                        if sig_type_str in [st.value for st in SignalType]:
                            sig_type = SignalType(sig_type_str)
                        else:
                            sig_type = SignalType.MARKET
                            
                        title = rs.get("title", "Untitled Signal")
                        description = rs.get("description", "No description provided.")
                        
                        # Handle either citation_ids or citations mapping
                        raw_cits = rs.get("citation_ids", rs.get("citations", []))
                        sig_citations = []
                        if isinstance(raw_cits, list):
                            for c in raw_cits:
                                try:
                                    c_int = int(c)
                                    if c_int in allowed_citations:
                                        sig_citations.append(c_int)
                                    else:
                                        logger.warning("SignalEngine | Hallucinated citation %d filtered out.", c_int)
                                except (ValueError, TypeError):
                                    continue
                                    
                        # Create valid Signal object
                        valid_signals.append(Signal(
                            signal_type=sig_type,
                            title=title,
                            description=description,
                            score=0.0,
                            citation_ids=sig_citations
                        ))
                    except Exception as err:
                        logger.warning("SignalEngine | Skipped parsing single signal item: %s", err)
                        continue
            
            return SignalExtractionResponse(
                signals=valid_signals,
                reasoning=reasoning
            )
            
        except json.JSONDecodeError as parse_err:
            logger.error("SignalEngine | JSON decoding failed: %s", parse_err)
            return SignalExtractionResponse(
                signals=[],
                reasoning=f"Parsing signals failed. Raw response: {raw_response[:200]}"
            )
        except Exception as err:
            logger.error("SignalEngine | Unexpected error during signal extraction: %s", err)
            return SignalExtractionResponse(
                signals=[],
                reasoning=f"An unexpected signal extraction error occurred: {err}"
            )
