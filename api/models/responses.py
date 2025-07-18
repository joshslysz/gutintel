"""
Standard response models for GutIntel API.

This module provides consistent response formats with proper error handling,
metadata, and pagination support for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Type variable for generic response data
T = TypeVar('T')


class ResponseMetadata(BaseModel):
    """Metadata included in all API responses."""
    
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorDetail(BaseModel):
    """Error detail structure for API responses."""
    
    code: str
    message: str
    field: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "field": "name"
            }
        }


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API responses."""
    
    success: bool
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    
    @classmethod
    def success_response(cls, data: T, metadata: Optional[ResponseMetadata] = None):
        """Create a successful response."""
        return cls(
            success=True,
            data=data,
            metadata=metadata or ResponseMetadata()
        )
    
    @classmethod
    def error_response(cls, errors: List[ErrorDetail], metadata: Optional[ResponseMetadata] = None):
        """Create an error response."""
        return cls(
            success=False,
            errors=errors,
            metadata=metadata or ResponseMetadata()
        )
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "metadata": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2023-12-07T10:30:00Z",
                    "version": "1.0.0"
                }
            }
        }


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=1, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")
    
    @classmethod
    def create(cls, total: int, page: int, per_page: int) -> 'PaginationInfo':
        """Create pagination info from total, page, and per_page."""
        total_pages = max(1, (total + per_page - 1) // per_page)
        
        return cls(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    
    class Config:
        schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "per_page": 20,
                "total_pages": 8,
                "has_next": True,
                "has_prev": False
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model for list endpoints."""
    
    success: bool = True
    data: List[T] = Field(default_factory=list)
    pagination: PaginationInfo
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        per_page: int,
        metadata: Optional[ResponseMetadata] = None
    ) -> 'PaginatedResponse[T]':
        """Create a paginated response."""
        return cls(
            data=data,
            pagination=PaginationInfo.create(total, page, per_page),
            metadata=metadata or ResponseMetadata()
        )
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "per_page": 20,
                    "total_pages": 8,
                    "has_next": True,
                    "has_prev": False
                },
                "metadata": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2023-12-07T10:30:00Z",
                    "version": "1.0.0"
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: str = "connected"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-12-07T10:30:00Z",
                "version": "1.0.0",
                "database": "connected"
            }
        }


# Common error responses
class ValidationErrorResponse(BaseResponse[None]):
    """Response for validation errors."""
    
    @classmethod
    def create(cls, field_errors: Dict[str, str]) -> 'ValidationErrorResponse':
        """Create validation error response from field errors."""
        errors = [
            ErrorDetail(
                code="VALIDATION_ERROR",
                message=message,
                field=field
            )
            for field, message in field_errors.items()
        ]
        return cls.error_response(errors)


class NotFoundErrorResponse(BaseResponse[None]):
    """Response for not found errors."""
    
    @classmethod
    def create(cls, resource: str, identifier: str) -> 'NotFoundErrorResponse':
        """Create not found error response."""
        error = ErrorDetail(
            code="NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' not found"
        )
        return cls.error_response([error])


class InternalServerErrorResponse(BaseResponse[None]):
    """Response for internal server errors."""
    
    @classmethod
    def create(cls, message: str = "Internal server error") -> 'InternalServerErrorResponse':
        """Create internal server error response."""
        error = ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message=message
        )
        return cls.error_response([error])


class ConflictErrorResponse(BaseResponse[None]):
    """Response for conflict errors."""
    
    @classmethod
    def create(cls, resource: str, reason: str) -> 'ConflictErrorResponse':
        """Create conflict error response."""
        error = ErrorDetail(
            code="CONFLICT",
            message=f"Conflict with existing {resource}: {reason}"
        )
        return cls.error_response([error])


# Response type aliases for common use cases
SuccessResponse = BaseResponse[Dict[str, Any]]
ErrorResponse = BaseResponse[None]
ListResponse = PaginatedResponse[Dict[str, Any]]