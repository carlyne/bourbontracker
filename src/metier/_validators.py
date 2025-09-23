from typing import Optional, Any
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

def _xmlish_to_scalar(v: Any):
    if isinstance(v, dict):
        if str(v.get("@xsi:nil", "")).lower() == "true":
            return None
        if "#text" in v:
            return v["#text"]
    return v

NilableStr = Annotated[Optional[str], BeforeValidator(_xmlish_to_scalar)]
