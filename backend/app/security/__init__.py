"""Security checks that produce findings for later decision logic."""

from .prompt_injection import detect_prompt_injection

__all__ = ["detect_prompt_injection"]