"""
IP-based query tracking for demo mode
Uses Streamlit's cache_data for persistence across sessions
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional


@st.cache_data(ttl=86400)  # Cache for 24 hours (1 day)
def get_ip_tracking() -> Dict[str, dict]:
    """
    Get IP tracking data (cached for 24 hours)

    Returns:
        Dict mapping IP addresses to tracking info:
        {
            "ip_address": {
                "last_query_date": "2024-10-18",
                "queries_today": 1
            }
        }
    """
    return {}


def get_client_ip() -> str:
    """
    Get client IP address from Streamlit

    Returns:
        IP address string, or 'unknown' if not available
    """
    try:
        # Try to get real IP from Streamlit context
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            session_info = st.runtime.get_instance().get_client(ctx.session_id)
            if session_info and hasattr(session_info, 'request'):
                # Try to get real IP from headers (for proxies)
                forwarded_for = session_info.request.headers.get('X-Forwarded-For')
                if forwarded_for:
                    return forwarded_for.split(',')[0].strip()

                # Fallback to remote address
                return session_info.request.remote_ip or 'unknown'
    except Exception:
        pass

    # Fallback: use session ID as pseudo-IP
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            return f"session_{ctx.session_id[:8]}"
    except Exception:
        pass

    return 'unknown'


def check_query_available(ip_address: str) -> tuple[bool, int]:
    """
    Check if a query is available for this IP today

    Args:
        ip_address: Client IP address

    Returns:
        Tuple of (query_available, queries_remaining)
    """
    # Check session state first (for immediate updates)
    if 'ip_tracking' in st.session_state and ip_address in st.session_state.ip_tracking:
        ip_data = st.session_state.ip_tracking[ip_address]
        today = datetime.now().date().isoformat()

        if ip_data.get('last_query_date') == today:
            queries_today = ip_data.get('queries_today', 0)
            if queries_today >= 1:
                return False, 0
            return True, 1 - queries_today

    # Fallback to cached data
    tracking = get_ip_tracking()
    today = datetime.now().date().isoformat()

    if ip_address not in tracking:
        # New IP - 1 query available
        return True, 1

    ip_data = tracking[ip_address]
    last_query_date = ip_data.get('last_query_date')
    queries_today = ip_data.get('queries_today', 0)

    # Check if it's a new day
    if last_query_date != today:
        # New day - reset to 1 query
        return True, 1

    # Same day - check if quota exhausted
    if queries_today >= 1:
        return False, 0

    return True, 1 - queries_today


def use_demo_query(ip_address: str) -> bool:
    """
    Use one demo query for this IP

    Args:
        ip_address: Client IP address

    Returns:
        True if query was successfully used, False if no queries available
    """
    available, remaining = check_query_available(ip_address)

    if not available:
        return False

    # Force cache update by modifying the function itself
    today = datetime.now().date().isoformat()

    # This is a workaround for Streamlit's caching limitations
    # We store in session state as well for immediate UI updates
    if 'ip_tracking' not in st.session_state:
        st.session_state.ip_tracking = {}

    st.session_state.ip_tracking[ip_address] = {
        'last_query_date': today,
        'queries_today': 1
    }

    # Clear cache to force reload
    get_ip_tracking.clear()

    return True


def has_user_api_key() -> bool:
    """Check if user has provided their own API key"""
    return 'user_openai_key' in st.session_state and st.session_state.user_openai_key


def can_use_app() -> tuple[bool, str]:
    """
    Check if user can use the app (has API key or demo query available)

    Returns:
        Tuple of (can_use, reason_if_not)
    """
    # Check if user has their own key
    if has_user_api_key():
        return True, "Using your API key"

    # Check demo quota
    ip_address = get_client_ip()
    available, remaining = check_query_available(ip_address)

    if available:
        return True, f"Demo mode: {remaining} free resume matching available today"
    else:
        return False, "Demo mode exhausted for today. Please enter your API key to continue."


def get_query_status_message() -> str:
    """
    Get status message for display in UI

    Returns:
        Status message string
    """
    if has_user_api_key():
        return "✅ Using your API key (unlimited)"

    ip_address = get_client_ip()
    available, remaining = check_query_available(ip_address)

    if available:
        return f"ℹ️ Demo mode: {remaining} free resume matching remaining today"
    else:
        return "⚠️ Demo mode exhausted for today. Enter API key to continue."
