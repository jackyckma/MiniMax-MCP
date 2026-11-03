"""Minimax API client base class."""

import requests
from typing import Any, Dict, Optional
from minimax_mcp.exceptions import MinimaxAuthError, MinimaxRequestError


def _is_model_plan_rejection(status_code: Any, status_msg: str) -> bool:
    if status_code == 2061:
        return True
    text = (status_msg or "").lower()
    return (
        "not support model" in text
        or "not available on your plan" in text
        or "model not available" in text
    )


def model_plan_error_message(status_code: Any, status_msg: str, trace_id: Optional[str]) -> str:
    """Readable tool error for MiniMax status 2061 / plan model rejections.

    The message intentionally does not include the API key.
    """
    detail = status_msg or "model not available on your plan"
    trace = f" Trace-Id: {trace_id}." if trace_id else ""
    return (
        "This model is not available on your plan "
        f"(MiniMax status {status_code}: {detail}). "
        "A Token Plan or M Plan subscription key is separate from a pay-as-you-go API key "
        "and does not cover every model. Video, voice design, and rapid voice cloning are "
        "common gaps. Pass a model your key supports, or set MINIMAX_DEFAULT_SPEECH_MODEL, "
        "MINIMAX_DEFAULT_T2V_MODEL, or MINIMAX_DEFAULT_T2I_MODEL. "
        "To use models outside the subscription, switch MINIMAX_API_KEY to a pay-as-you-go key "
        "from the same region as MINIMAX_API_HOST."
        f"{trace}"
    )

class MinimaxAPIClient:
    """Base client for making requests to Minimax API."""
    
    def __init__(self, api_key: str, api_host: str):
        """Initialize the API client.
        
        Args:
            api_key: The API key for authentication
            api_host: The API host URL
        """
        self.api_key = api_key
        self.api_host = api_host
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'MM-API-Source': 'Minimax-MCP'
        })

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Minimax API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            API response data as dictionary
            
        Raises:
            MinimaxAuthError: If authentication fails
            MinimaxRequestError: If the request fails
        """
        url = f"{self.api_host}{endpoint}"
        
        # Set Content-Type based on whether files are being uploaded
        files = kwargs.get('files')
        if not files:
            self.session.headers['Content-Type'] = 'application/json'
        else:
            # Remove Content-Type header for multipart/form-data
            # requests library will set it automatically with the correct boundary
            self.session.headers.pop('Content-Type', None)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            data = response.json()
            
            # Check API-specific error codes
            base_resp = data.get("base_resp", {})
            status_code = base_resp.get("status_code")
            status_msg = base_resp.get("status_msg") or ""
            if status_code != 0:
                if _is_model_plan_rejection(status_code, status_msg):
                    raise MinimaxRequestError(
                        model_plan_error_message(
                            status_code,
                            status_msg,
                            response.headers.get("Trace-Id"),
                        )
                    )
                match status_code:
                    case 1004:
                        raise MinimaxAuthError(
                            f"API Error: {base_resp.get('status_msg')}, please check your API key and API host."
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                        )
                    case 2038:
                        raise MinimaxRequestError(
                            f"API Error: {base_resp.get('status_msg')}, should complete real-name verification on the open-platform(https://platform.minimaxi.com/user-center/basic-information)."
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                        )
                    case _:
                        raise MinimaxRequestError(
                            f"API Error: {base_resp.get('status_code')}-{base_resp.get('status_msg')} "
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                        )
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise MinimaxRequestError(f"Request failed: {str(e)}")
            
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, **kwargs)
        
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, **kwargs) 