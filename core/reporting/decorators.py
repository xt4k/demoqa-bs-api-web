from typing import Callable, Any
import pytest
from functools import wraps

def html_title(title: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_html_title_template", title)
        setattr(func, "_html_title", title)
        return func
    return decorator

def html_sub_suite(sub_suite: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_html_sub_suite", sub_suite)
        return func
    return decorator

def html_feature(feature: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_feature", feature)
        return func
    return decorator

def _resolve_placeholders(template: str, context: dict) -> str:
    try:
        return template.format(**context)
    except Exception:
        return template

def html_step(step_description: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = getattr(pytest, "current_request", None)
            arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
            arg_map = {**dict(zip(arg_names, args)), **kwargs}
            step_text = _resolve_placeholders(step_description, arg_map)
            if request and hasattr(request, "node"):
                steps_list = getattr(request.node, "html_steps", [])
                steps_list.append(step_text)
                setattr(request.node, "html_steps", steps_list)
            return func(*args, **kwargs)
        setattr(wrapper, "_html_step", step_description)
        return wrapper
    return decorator
