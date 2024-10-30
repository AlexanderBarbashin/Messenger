"""Responses file. Used to define HTTP responses."""
from python_advanced_diploma.src.schemas import (
    ErrorMessage,
    ValidationErrorMessage,
)

bad_request_error_response = {
    "model": ErrorMessage,
    "description": "Value Error",
}
not_found_error_response = {
    "model": ErrorMessage,
    "description": "No Result Found Error",
}
validation_error_response = {
    "model": ValidationErrorMessage,
    "description": "Validation Error",
}
