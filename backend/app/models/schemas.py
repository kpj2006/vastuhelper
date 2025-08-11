"""
Pydantic Data Models for Floor Plan Analysis

This module defines all the data structures used throughout the application
for request/response validation and data consistency.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from enum import Enum

# Enums for standardized values
class RoomType(str, Enum):
    """Standardized room types for consistent classification"""
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    DINING_ROOM = "dining_room"
    STUDY = "study"
    BALCONY = "balcony"
    STAIRCASE = "staircase"
    CORRIDOR = "corridor"
    STORAGE = "storage"
    GARAGE = "garage"
    POOJA_ROOM = "pooja_room"  # For Vastu analysis

class Direction(str, Enum):
    """Cardinal directions for Vastu and sunlight analysis"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTH_EAST = "north_east"
    NORTH_WEST = "north_west"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"

class ComplianceStatus(str, Enum):
    """Status levels for compliance checks"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    NEEDS_REVIEW = "needs_review"

# Core data models
class Coordinates(BaseModel):
    """2D coordinates and dimensions for room positioning"""
    x: float = Field(..., ge=0, description="X coordinate (left edge)")
    y: float = Field(..., ge=0, description="Y coordinate (top edge)")
    width: float = Field(..., gt=0, description="Width in units")
    height: float = Field(..., gt=0, description="Height in units")

class Room(BaseModel):
    """Detailed room information with all necessary attributes"""
    id: str = Field(..., description="Unique room identifier")
    type: RoomType = Field(..., description="Room type classification")
    name: Optional[str] = Field(None, description="Custom room name")
    area: float = Field(..., gt=0, description="Room area in square units")
    direction: Direction = Field(..., description="Primary facing direction")
    windows: int = Field(0, ge=0, description="Number of windows")
    doors: int = Field(1, ge=1, description="Number of doors")
    coordinates: Coordinates = Field(..., description="Room position and size")
    
    # Optional attributes for advanced analysis
    ceiling_height: Optional[float] = Field(None, gt=0, description="Ceiling height")
    has_natural_ventilation: bool = Field(True, description="Has windows or vents")
    is_load_bearing: Optional[bool] = Field(None, description="Contains load-bearing walls")
    
    @validator('area')
    def validate_area_matches_coordinates(cls, v, values):
        """Ensure area roughly matches coordinate dimensions"""
        if 'coordinates' in values:
            coords = values['coordinates']
            calculated_area = coords.width * coords.height
            # Allow 10% tolerance for irregular rooms
            if abs(v - calculated_area) > calculated_area * 0.1:
                raise ValueError("Area should roughly match width × height")
        return v

class BuildingInfo(BaseModel):
    """Overall building characteristics and metadata"""
    total_area: float = Field(..., gt=0, description="Total building area")
    floors: int = Field(1, ge=1, le=10, description="Number of floors")
    building_type: str = Field("residential", description="Building type")
    construction_year: Optional[int] = Field(None, description="Year of construction")
    location_coordinates: Optional[Dict[str, float]] = Field(
        None, description="GPS coordinates for sunlight analysis"
    )
    
    # Building code specific information
    local_building_code: str = Field("generic", description="Applicable building code")
    zone_classification: Optional[str] = Field(None, description="Zoning classification")

class FloorPlan(BaseModel):
    """Complete floor plan data structure"""
    rooms: List[Room] = Field(..., min_items=1, description="List of all rooms")
    building_info: BuildingInfo = Field(..., description="Building metadata")
    image_metadata: Optional[Dict[str, Union[str, int, float]]] = Field(
        None, description="Original image processing metadata"
    )
    
    @validator('rooms')
    def validate_total_area(cls, v, values):
        """Ensure sum of room areas doesn't exceed building area"""
        if 'building_info' in values:
            total_room_area = sum(room.area for room in v)
            if total_room_area > values['building_info'].total_area * 1.2:  # 20% tolerance
                raise ValueError("Sum of room areas exceeds building area")
        return v

# Compliance analysis models
class ComplianceIssue(BaseModel):
    """Individual compliance violation or suggestion"""
    id: str = Field(..., description="Unique issue identifier")
    severity: ComplianceStatus = Field(..., description="Issue severity level")
    category: str = Field(..., description="Issue category")
    title: str = Field(..., description="Brief issue description")
    description: str = Field(..., description="Detailed issue explanation")
    affected_rooms: List[str] = Field(default=[], description="Room IDs affected")
    suggestions: List[str] = Field(default=[], description="Recommendations to fix")
    code_reference: Optional[str] = Field(None, description="Building code reference")

class BuildingCodeAnalysis(BaseModel):
    """Building code compliance analysis results"""
    overall_status: ComplianceStatus = Field(..., description="Overall compliance status")
    compliance_percentage: float = Field(..., ge=0, le=100, description="Compliance percentage")
    issues: List[ComplianceIssue] = Field(default=[], description="List of violations")
    
    # Specific building code metrics
    minimum_room_sizes_met: bool = Field(..., description="Room size requirements")
    ventilation_adequate: bool = Field(..., description="Ventilation requirements")
    exit_paths_clear: bool = Field(..., description="Emergency exit accessibility")
    structural_integrity: ComplianceStatus = Field(..., description="Structural safety")

class VastuAnalysis(BaseModel):
    """Vastu Shastra compliance analysis results"""
    overall_status: ComplianceStatus = Field(..., description="Overall Vastu compliance")
    vastu_score: float = Field(..., ge=0, le=100, description="Vastu score percentage")
    issues: List[ComplianceIssue] = Field(default=[], description="Vastu violations")
    
    # Specific Vastu principles
    main_entrance_direction: ComplianceStatus = Field(..., description="Entrance placement")
    kitchen_placement: ComplianceStatus = Field(..., description="Kitchen direction")
    bedroom_directions: ComplianceStatus = Field(..., description="Bedroom orientations")
    pooja_room_compliance: ComplianceStatus = Field(..., description="Prayer room placement")

class SunlightAnalysis(BaseModel):
    """Sunlight optimization analysis results"""
    overall_status: ComplianceStatus = Field(..., description="Overall sunlight optimization")
    sunlight_score: float = Field(..., ge=0, le=100, description="Sunlight utilization score")
    issues: List[ComplianceIssue] = Field(default=[], description="Sunlight optimization issues")
    
    # Specific sunlight metrics
    morning_light_access: ComplianceStatus = Field(..., description="Morning light in bedrooms")
    kitchen_natural_light: ComplianceStatus = Field(..., description="Kitchen lighting")
    living_area_brightness: ComplianceStatus = Field(..., description="Main living area light")
    seasonal_considerations: List[str] = Field(default=[], description="Seasonal light patterns")

class CompleteAnalysis(BaseModel):
    """Comprehensive analysis results combining all compliance checks"""
    floor_plan_id: str = Field(..., description="Unique analysis identifier")
    timestamp: str = Field(..., description="Analysis timestamp")
    
    # Individual analysis results
    building_code: BuildingCodeAnalysis = Field(..., description="Building code analysis")
    vastu: VastuAnalysis = Field(..., description="Vastu Shastra analysis")
    sunlight: SunlightAnalysis = Field(..., description="Sunlight analysis")
    
    # Overall summary
    overall_compliance_score: float = Field(..., ge=0, le=100, description="Combined score")
    priority_issues: List[ComplianceIssue] = Field(default=[], description="High priority issues")
    recommendations: List[str] = Field(default=[], description="Top recommendations")

# Request/Response models for API endpoints
class AnalysisRequest(BaseModel):
    """Request model for floor plan analysis"""
    floor_plan: FloorPlan = Field(..., description="Floor plan data to analyze")
    analysis_types: List[str] = Field(
        default=["building_code", "vastu", "sunlight"],
        description="Types of analysis to perform"
    )
    
    # Optional analysis parameters
    strict_mode: bool = Field(False, description="Use strict compliance checking")
    location: Optional[str] = Field(None, description="Building location for local codes")

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool = Field(True, description="Analysis success status")
    message: str = Field("Analysis completed successfully", description="Status message")
    data: CompleteAnalysis = Field(..., description="Analysis results")
    processing_time: float = Field(..., description="Processing time in seconds")

# Error response models
class ErrorResponse(BaseModel):
    """Standardized error response model"""
    error: bool = Field(True, description="Error indicator")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
