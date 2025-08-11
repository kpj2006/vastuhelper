"""
Analysis Router

API endpoints for floor plan compliance analysis including:
- Building code compliance checks
- Vastu Shastra analysis  
- Sunlight optimization analysis
- Complete multi-aspect analysis

All endpoints accept floor plan data and return detailed compliance reports.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
import time
from datetime import datetime
import uuid

# Import data models
from app.models.schemas import (
    FloorPlan, AnalysisRequest, AnalysisResponse, CompleteAnalysis,
    BuildingCodeAnalysis, VastuAnalysis, SunlightAnalysis,
    ComplianceIssue, ComplianceStatus
)

# Import service classes
from app.services.building_code_service import BuildingCodeService
from app.services.vastu_service import VastuService  
from app.services.sunlight_service import SunlightService

# Create router instance
router = APIRouter()

# Initialize service instances
building_code_service = BuildingCodeService()
vastu_service = VastuService()
sunlight_service = SunlightService()

@router.post("/building-codes", response_model=Dict)
async def analyze_building_codes(request: AnalysisRequest):
    """
    Analyze floor plan for building code compliance
    
    Args:
        request: Floor plan data and analysis parameters
        
    Returns:
        Building code compliance analysis results
    """
    try:
        start_time = time.time()
        
        # Perform building code analysis
        analysis = building_code_service.analyze_building_code_compliance(request.floor_plan)
        
        processing_time = time.time() - start_time
        
        # Generate summary for easier frontend consumption
        summary = building_code_service.get_building_code_summary(analysis)
        
        return {
            "success": True,
            "message": "Building code analysis completed successfully",
            "data": {
                "analysis": analysis.dict(),
                "summary": summary
            },
            "processing_time": round(processing_time, 3)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Building code analysis failed: {str(e)}"
        )

@router.post("/vastu", response_model=Dict)
async def analyze_vastu_compliance(request: AnalysisRequest):
    """
    Analyze floor plan for Vastu Shastra compliance
    
    Args:
        request: Floor plan data and analysis parameters
        
    Returns:
        Vastu Shastra compliance analysis results
    """
    try:
        start_time = time.time()
        
        # Perform Vastu analysis
        analysis = vastu_service.analyze_vastu_compliance(request.floor_plan)
        
        processing_time = time.time() - start_time
        
        # Generate summary for easier frontend consumption  
        summary = vastu_service.get_vastu_summary(analysis)
        
        return {
            "success": True,
            "message": "Vastu Shastra analysis completed successfully",
            "data": {
                "analysis": analysis.dict(),
                "summary": summary
            },
            "processing_time": round(processing_time, 3)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vastu analysis failed: {str(e)}"
        )

@router.post("/sunlight", response_model=Dict)
async def analyze_sunlight_optimization(request: AnalysisRequest):
    """
    Analyze floor plan for sunlight optimization
    
    Args:
        request: Floor plan data and analysis parameters
        
    Returns:
        Sunlight optimization analysis results
    """
    try:
        start_time = time.time()
        
        # Perform sunlight analysis
        analysis = sunlight_service.analyze_sunlight_optimization(request.floor_plan)
        
        processing_time = time.time() - start_time
        
        # Generate summary for easier frontend consumption
        summary = sunlight_service.get_sunlight_summary(analysis)
        
        return {
            "success": True,
            "message": "Sunlight optimization analysis completed successfully", 
            "data": {
                "analysis": analysis.dict(),
                "summary": summary
            },
            "processing_time": round(processing_time, 3)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sunlight analysis failed: {str(e)}"
        )

@router.post("/complete", response_model=AnalysisResponse)
async def analyze_complete_compliance(request: AnalysisRequest):
    """
    Perform comprehensive analysis including all compliance checks
    
    Args:
        request: Floor plan data and analysis parameters
        
    Returns:
        Complete analysis results with all compliance aspects
    """
    try:
        start_time = time.time()
        
        # Perform all analysis types
        building_code_analysis = building_code_service.analyze_building_code_compliance(request.floor_plan)
        vastu_analysis = vastu_service.analyze_vastu_compliance(request.floor_plan)  
        sunlight_analysis = sunlight_service.analyze_sunlight_optimization(request.floor_plan)
        
        # Calculate overall compliance score
        overall_score = _calculate_overall_score(
            building_code_analysis, vastu_analysis, sunlight_analysis
        )
        
        # Collect priority issues (critical and high-severity issues)
        priority_issues = _collect_priority_issues(
            building_code_analysis, vastu_analysis, sunlight_analysis
        )
        
        # Generate top recommendations
        recommendations = _generate_top_recommendations(
            building_code_analysis, vastu_analysis, sunlight_analysis
        )
        
        # Create complete analysis object
        complete_analysis = CompleteAnalysis(
            floor_plan_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            building_code=building_code_analysis,
            vastu=vastu_analysis,
            sunlight=sunlight_analysis,
            overall_compliance_score=overall_score,
            priority_issues=priority_issues,
            recommendations=recommendations
        )
        
        processing_time = time.time() - start_time
        
        return AnalysisResponse(
            success=True,
            message="Complete floor plan analysis completed successfully",
            data=complete_analysis,
            processing_time=round(processing_time, 3)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complete analysis failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for analysis services
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "message": "Analysis services are operational",
        "services": {
            "building_code": "active",
            "vastu": "active", 
            "sunlight": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/analysis-types")
async def get_analysis_types():
    """
    Get available analysis types and their descriptions
    
    Returns:
        List of available analysis types with descriptions
    """
    return {
        "analysis_types": [
            {
                "id": "building_code",
                "name": "Building Code Compliance",
                "description": "Checks room sizes, ventilation, exits, and structural requirements",
                "categories": ["Room Size", "Ventilation", "Emergency Egress", "Structural"]
            },
            {
                "id": "vastu",
                "name": "Vastu Shastra",
                "description": "Analyzes directional placement according to Vastu principles",
                "categories": ["Main Entrance", "Kitchen Placement", "Bedroom Directions", "Pooja Room"]
            },
            {
                "id": "sunlight",
                "name": "Sunlight Optimization", 
                "description": "Evaluates natural light access and seasonal considerations",
                "categories": ["Morning Light", "Kitchen Lighting", "Living Area Brightness", "Seasonal Comfort"]
            }
        ]
    }

# Helper functions for complete analysis

def _calculate_overall_score(
    building_code: BuildingCodeAnalysis,
    vastu: VastuAnalysis, 
    sunlight: SunlightAnalysis
) -> float:
    """Calculate weighted overall compliance score"""
    
    # Weight different analysis types (can be made configurable)
    building_code_weight = 0.5  # Building codes are most critical
    vastu_weight = 0.3         # Vastu is important but more flexible
    sunlight_weight = 0.2      # Sunlight is optimization-focused
    
    # Calculate weighted score
    overall_score = (
        building_code.compliance_percentage * building_code_weight +
        vastu.vastu_score * vastu_weight +
        sunlight.sunlight_score * sunlight_weight
    )
    
    return round(overall_score, 1)

def _collect_priority_issues(
    building_code: BuildingCodeAnalysis,
    vastu: VastuAnalysis,
    sunlight: SunlightAnalysis  
) -> List[ComplianceIssue]:
    """Collect high-priority issues across all analysis types"""
    
    priority_issues = []
    
    # Add critical building code issues (highest priority)
    for issue in building_code.issues:
        if issue.severity == ComplianceStatus.NON_COMPLIANT:
            priority_issues.append(issue)
    
    # Add critical Vastu issues  
    for issue in vastu.issues:
        if issue.severity == ComplianceStatus.NON_COMPLIANT:
            priority_issues.append(issue)
    
    # Add critical sunlight issues
    for issue in sunlight.issues:
        if issue.severity == ComplianceStatus.NON_COMPLIANT:
            priority_issues.append(issue)
    
    # Add important warning issues if we don't have too many critical ones
    if len(priority_issues) < 5:
        for issue in building_code.issues + vastu.issues + sunlight.issues:
            if issue.severity == ComplianceStatus.WARNING and len(priority_issues) < 8:
                priority_issues.append(issue)
    
    # Sort by severity and limit to top 10 issues
    severity_order = {
        ComplianceStatus.NON_COMPLIANT: 0,
        ComplianceStatus.WARNING: 1,
        ComplianceStatus.NEEDS_REVIEW: 2,
        ComplianceStatus.COMPLIANT: 3
    }
    
    priority_issues.sort(key=lambda x: severity_order[x.severity])
    
    return priority_issues[:10]

def _generate_top_recommendations(
    building_code: BuildingCodeAnalysis,
    vastu: VastuAnalysis,
    sunlight: SunlightAnalysis
) -> List[str]:
    """Generate top-level recommendations based on analysis results"""
    
    recommendations = []
    
    # Building code recommendations (highest priority)
    if building_code.compliance_percentage < 70:
        recommendations.append("Address critical building code violations for safety compliance")
        
    if not building_code.minimum_room_sizes_met:
        recommendations.append("Expand undersized rooms to meet minimum area requirements")
        
    if not building_code.ventilation_adequate:
        recommendations.append("Add windows or ventilation systems for adequate air circulation")
    
    # Vastu recommendations
    if vastu.vastu_score < 70:
        if vastu.kitchen_placement == ComplianceStatus.NON_COMPLIANT:
            recommendations.append("Consider relocating kitchen to South-East direction for better Vastu")
            
        if vastu.main_entrance_direction == ComplianceStatus.NON_COMPLIANT:
            recommendations.append("Optimize main entrance direction for positive energy flow")
    
    # Sunlight recommendations
    if sunlight.sunlight_score < 60:
        if sunlight.morning_light_access == ComplianceStatus.NON_COMPLIANT:
            recommendations.append("Add East-facing windows for better morning light in bedrooms")
            
        if sunlight.kitchen_natural_light == ComplianceStatus.NON_COMPLIANT:
            recommendations.append("Improve natural lighting in kitchen for better food preparation")
    
    # General recommendations
    if len(recommendations) == 0:
        recommendations.append("Floor plan shows good overall compliance - consider minor optimizations")
    elif len(recommendations) > 6:
        # If too many issues, provide general guidance
        recommendations = [
            "Focus on building code compliance first for safety",
            "Address room sizing and ventilation issues",
            "Optimize room directions for better functionality",
            "Improve natural lighting throughout the home"
        ]
    
    return recommendations[:5]  # Limit to top 5 recommendations
