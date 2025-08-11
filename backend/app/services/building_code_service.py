"""
Building Code Compliance Service

This service implements building code compliance checks including:
- Minimum room size requirements
- Ventilation standards  
- Emergency exit path analysis
- Structural safety assessments

Currently uses mock rules but can be extended with real building codes.
"""

from typing import List, Dict
from app.models.schemas import (
    FloorPlan, Room, BuildingCodeAnalysis, ComplianceIssue, 
    ComplianceStatus, RoomType
)
import uuid
from datetime import datetime

class BuildingCodeService:
    """Service class for building code compliance analysis"""
    
    def __init__(self):
        """Initialize with standard building code requirements"""
        # Minimum room areas in square feet (can be made configurable)
        self.min_room_areas = {
            RoomType.BEDROOM: 80,      # 80 sq ft minimum for bedroom
            RoomType.LIVING_ROOM: 120,  # 120 sq ft minimum for living room
            RoomType.KITCHEN: 50,      # 50 sq ft minimum for kitchen
            RoomType.BATHROOM: 25,     # 25 sq ft minimum for bathroom
            RoomType.DINING_ROOM: 80,  # 80 sq ft minimum for dining room
            RoomType.STUDY: 60,        # 60 sq ft minimum for study
        }
        
        # Ventilation requirements (windows per room type)
        self.min_windows = {
            RoomType.BEDROOM: 1,       # At least 1 window for bedroom
            RoomType.LIVING_ROOM: 2,   # At least 2 windows for living room
            RoomType.KITCHEN: 1,       # At least 1 window for kitchen
            RoomType.DINING_ROOM: 1,   # At least 1 window for dining room
            RoomType.STUDY: 1,         # At least 1 window for study
        }

    def analyze_building_code_compliance(self, floor_plan: FloorPlan) -> BuildingCodeAnalysis:
        """
        Main method to analyze building code compliance
        
        Args:
            floor_plan: Complete floor plan data
            
        Returns:
            BuildingCodeAnalysis with compliance status and issues
        """
        issues = []
        
        # Check individual room requirements
        room_size_issues = self._check_minimum_room_sizes(floor_plan.rooms)
        ventilation_issues = self._check_ventilation_requirements(floor_plan.rooms)
        exit_path_issues = self._check_exit_paths(floor_plan.rooms)
        structural_issues = self._check_structural_integrity(floor_plan)
        
        # Combine all issues
        issues.extend(room_size_issues)
        issues.extend(ventilation_issues)  
        issues.extend(exit_path_issues)
        issues.extend(structural_issues)
        
        # Calculate compliance metrics
        room_sizes_met = len(room_size_issues) == 0
        ventilation_adequate = len(ventilation_issues) == 0
        exit_paths_clear = len(exit_path_issues) == 0
        
        # Determine structural integrity status
        critical_structural_issues = [
            issue for issue in structural_issues 
            if issue.severity == ComplianceStatus.NON_COMPLIANT
        ]
        structural_integrity = (
            ComplianceStatus.COMPLIANT if len(critical_structural_issues) == 0
            else ComplianceStatus.NON_COMPLIANT
        )
        
        # Calculate overall compliance
        total_checks = 4  # room sizes, ventilation, exits, structure
        passed_checks = sum([
            room_sizes_met,
            ventilation_adequate, 
            exit_paths_clear,
            structural_integrity == ComplianceStatus.COMPLIANT
        ])
        compliance_percentage = (passed_checks / total_checks) * 100
        
        # Determine overall status
        if compliance_percentage >= 90:
            overall_status = ComplianceStatus.COMPLIANT
        elif compliance_percentage >= 70:
            overall_status = ComplianceStatus.WARNING
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        return BuildingCodeAnalysis(
            overall_status=overall_status,
            compliance_percentage=compliance_percentage,
            issues=issues,
            minimum_room_sizes_met=room_sizes_met,
            ventilation_adequate=ventilation_adequate,
            exit_paths_clear=exit_paths_clear,
            structural_integrity=structural_integrity
        )

    def _check_minimum_room_sizes(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check if rooms meet minimum size requirements"""
        issues = []
        
        for room in rooms:
            # Skip rooms that don't have size requirements
            if room.type not in self.min_room_areas:
                continue
                
            min_area = self.min_room_areas[room.type]
            
            if room.area < min_area:
                issue = ComplianceIssue(
                    id=f"room_size_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Room Size",
                    title=f"{room.type.value.replace('_', ' ').title()} Too Small",
                    description=f"Room '{room.name or room.type.value}' is {room.area} sq ft, but minimum required is {min_area} sq ft.",
                    affected_rooms=[room.id],
                    suggestions=[
                        f"Expand room area to at least {min_area} sq ft",
                        "Consider combining with adjacent spaces",
                        "Remove non-essential fixtures to create more space"
                    ],
                    code_reference="IBC Section 1208 - Interior Space Dimensions"
                )
                issues.append(issue)
        
        return issues

    def _check_ventilation_requirements(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check if rooms have adequate natural ventilation"""
        issues = []
        
        for room in rooms:
            # Skip rooms that don't require windows
            if room.type not in self.min_windows:
                continue
                
            required_windows = self.min_windows[room.type]
            
            # Check window count
            if room.windows < required_windows:
                issue = ComplianceIssue(
                    id=f"ventilation_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Ventilation",
                    title=f"Insufficient Windows in {room.type.value.replace('_', ' ').title()}",
                    description=f"Room has {room.windows} window(s), but {required_windows} required for adequate ventilation.",
                    affected_rooms=[room.id],
                    suggestions=[
                        f"Add {required_windows - room.windows} additional window(s)",
                        "Install mechanical ventilation system",
                        "Consider skylights if wall windows are not feasible"
                    ],
                    code_reference="IBC Section 1204 - Natural Ventilation"
                )
                issues.append(issue)
            
            # Check natural ventilation status
            if not room.has_natural_ventilation:
                issue = ComplianceIssue(
                    id=f"natural_vent_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Ventilation",
                    title="No Natural Ventilation",
                    description=f"Room '{room.name or room.type.value}' lacks natural ventilation sources.",
                    affected_rooms=[room.id],
                    suggestions=[
                        "Add operable windows or vents",
                        "Install exhaust fans",
                        "Connect to central ventilation system"
                    ],
                    code_reference="IBC Section 1204 - Natural Ventilation"
                )
                issues.append(issue)
        
        return issues

    def _check_exit_paths(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check emergency exit path accessibility"""
        issues = []
        
        # Find rooms that could be bedrooms (sleeping areas need egress)
        bedrooms = [room for room in rooms if room.type == RoomType.BEDROOM]
        
        for bedroom in bedrooms:
            # Bedrooms need at least 1 window for egress (in addition to door)
            if bedroom.windows == 0:
                issue = ComplianceIssue(
                    id=f"egress_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Emergency Egress",
                    title="Bedroom Lacks Emergency Exit",
                    description=f"Bedroom '{bedroom.name or bedroom.id}' has no window for emergency egress.",
                    affected_rooms=[bedroom.id],
                    suggestions=[
                        "Add egress window meeting size requirements",
                        "Ensure window sill height is appropriate",
                        "Install window hardware for easy opening"
                    ],
                    code_reference="IBC Section 1030 - Emergency Egress"
                )
                issues.append(issue)
        
        # Check for potential corridor/hallway width issues
        corridors = [room for room in rooms if room.type == RoomType.CORRIDOR]
        
        for corridor in corridors:
            # Assume corridors should be at least 3 feet wide (36 inches)
            min_width = min(corridor.coordinates.width, corridor.coordinates.height)
            
            if min_width < 36:  # 36 units assumed to be inches
                issue = ComplianceIssue(
                    id=f"corridor_width_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Accessibility",
                    title="Narrow Corridor",
                    description=f"Corridor width of {min_width} units may be too narrow for safe passage.",
                    affected_rooms=[corridor.id],
                    suggestions=[
                        "Widen corridor to at least 36 inches",
                        "Remove obstacles in corridor path",
                        "Ensure clear height of at least 80 inches"
                    ],
                    code_reference="IBC Section 1005 - Egress Width"
                )
                issues.append(issue)
        
        return issues

    def _check_structural_integrity(self, floor_plan: FloorPlan) -> List[ComplianceIssue]:
        """Check structural integrity and safety concerns"""
        issues = []
        
        # Check for load-bearing wall considerations
        load_bearing_rooms = [
            room for room in floor_plan.rooms 
            if room.is_load_bearing is True
        ]
        
        # Mock structural analysis - in real implementation, this would be much more complex
        total_area = floor_plan.building_info.total_area
        
        # Check if building is unusually large for single floor
        if floor_plan.building_info.floors == 1 and total_area > 2000:
            issue = ComplianceIssue(
                id=f"structure_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NEEDS_REVIEW,
                category="Structural",
                title="Large Single-Floor Structure",
                description=f"Building area of {total_area} sq ft may require additional structural analysis.",
                affected_rooms=[],
                suggestions=[
                    "Consult structural engineer for load calculations",
                    "Verify foundation requirements",
                    "Consider additional support columns"
                ],
                code_reference="IBC Chapter 16 - Structural Design"
            )
            issues.append(issue)
        
        # Check room proportions for structural stability
        for room in floor_plan.rooms:
            aspect_ratio = max(room.coordinates.width, room.coordinates.height) / min(room.coordinates.width, room.coordinates.height)
            
            # Flag rooms with extreme aspect ratios
            if aspect_ratio > 5:  # Very long and narrow rooms
                issue = ComplianceIssue(
                    id=f"proportion_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Structural",
                    title="Unusual Room Proportions",
                    description=f"Room '{room.name or room.type.value}' has extreme proportions (ratio: {aspect_ratio:.1f}:1).",
                    affected_rooms=[room.id],
                    suggestions=[
                        "Consider structural support for long spans",
                        "Add intermediate columns if necessary",
                        "Verify beam sizing requirements"
                    ],
                    code_reference="IBC Section 1604 - General Design Requirements"
                )
                issues.append(issue)
        
        return issues

    def get_building_code_summary(self, analysis: BuildingCodeAnalysis) -> Dict[str, any]:
        """Generate a summary of building code analysis for dashboard display"""
        
        # Count issues by severity
        critical_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NON_COMPLIANT])
        warning_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.WARNING])
        review_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NEEDS_REVIEW])
        
        return {
            "overall_status": analysis.overall_status.value,
            "compliance_percentage": analysis.compliance_percentage,
            "total_issues": len(analysis.issues),
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "review_issues": review_issues,
            "key_metrics": {
                "room_sizes_compliant": analysis.minimum_room_sizes_met,
                "ventilation_adequate": analysis.ventilation_adequate,
                "exit_paths_clear": analysis.exit_paths_clear,
                "structural_integrity": analysis.structural_integrity.value
            }
        }
