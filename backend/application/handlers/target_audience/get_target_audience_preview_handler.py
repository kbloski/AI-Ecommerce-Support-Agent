from typing import Dict, Any
from fastapi import HTTPException
from di.container import Container

def get_target_audience_preview_handler( target_audience_id: int) -> Dict[str, Any]:
    try:
        return Container().target_audience_service().get_target_audience_details_by_id(target_audience_id).to_dict()
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
