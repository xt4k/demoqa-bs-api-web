from functools import wraps
from typing import Callable, Any

import pytest

from core.util.logging import Logger

ATTRIBUTES__ = """
    Decorator to add test steps to the Pytest report.
    Supports dynamic variable substitution, including nested attributes.
    """
log = Logger.get_logger()



def html_title(title: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to attach a title to the test function. Supports dynamic formatting with test parameters.
    """

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


def resolve_placeholders(template: str, context: dict) -> str:
    """
    Resolves placeholders in the step description.
    Supports direct variables and nested attributes (e.g., {slot.ps_name}).
    """
    try:
        return template.format_map(AttributeResolver(context))
    except KeyError as e:
        return f"{template} [MISSING VAR: {e}]"

class AttributeResolver(dict):
    """Helper class to resolve nested attributes in placeholders."""

    def __missing__(self, key):
        return f"[UNKNOWN: {key}]"

    def __getitem__(self, key):
        value = dict.get(self, key, f"[UNKNOWN: {key}]")
        # If value is an object, return its __dict__ for nested formatting
        return value.__dict__ if hasattr(value, "__dict__") else value


def html_step(step_description: str):
    """
    Decorator to add test steps to the Pytest report.
    Supports dynamic variable substitution, including nested attributes.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Retrieve the current Pytest request context
            request = getattr(pytest, "current_request", None)
            # Merge function arguments into a dictionary
            arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
            all_args = {**dict(zip(arg_names, args)), **kwargs}
            # Resolve placeholders in the step description
            formatted_description = resolve_placeholders(step_description, all_args)
            # Store the formatted step in the test's metadata
            if request and hasattr(request, "node"):
                steps_list = getattr(request.node, "html_steps", [])
                steps_list.append(formatted_description)
                setattr(request.node, "html_steps", steps_list)
                # log.info(logger, f"Step added: {formatted_description} to {request.node.name}")
            else:
                log.info("No request object found in arguments.")
            # Execute the original function
            return func(*args, **kwargs)

        wrapper._html_step = step_description  # Preserve the original template
        return wrapper

    return decorator
