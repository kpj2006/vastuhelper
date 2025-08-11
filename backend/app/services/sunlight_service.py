"""
Sunlight Analysis Service

This service analyzes floor plans for optimal sunlight utilization including:
- Morning light access in bedrooms
- Natural light in kitchens and living areas  
- Seasonal sunlight considerations
- Window placement optimization

Currently uses mock solar calculations but can be extended with real solar data.
"""

from typing import List, Dict, Tuple
from app.models.schemas import (
    FloorPlan, Room, SunlightAnalysis, ComplianceIssue,
    ComplianceStatus, RoomType, Direction
)
import uuid
import math

class SunlightService:
    """Service class for sunlight optimization analysis"""
    
    def __init__(self):
        """Initialize with sunlight preferences and solar data"""
        
        # Ideal sunlight directions for different times of day
        self.morning_light_directions = [Direction.EAST, Direction.NORTH_EAST, Direction.SOUTH_EAST]
        self.afternoon_light_directions = [Direction.SOUTH, Direction.SOUTH_WEST, Direction.WEST]
        self.evening_light_directions = [Direction.WEST, Direction.NORTH_WEST, Direction.SOUTH_WEST]
        
        # Room types that benefit most from morning light
        self.morning_light_rooms = [RoomType.BEDROOM, RoomType.DINING_ROOM, RoomType.STUDY]
        
        # Room types that benefit from consistent daylight
        self.daylight_priority_rooms = [RoomType.LIVING_ROOM, RoomType.KITCHEN, RoomType.STUDY]
        
        # Room types that can have less natural light
        self.low_light_tolerance = [RoomType.BATHROOM, RoomType.STORAGE, RoomType.CORRIDOR]
        
        # Mock solar intensity by direction (0-100 scale)
        self.solar_intensity = {
            Direction.NORTH: 30,      # Consistent but lower intensity
            Direction.NORTH_EAST: 60, # Good morning light
            Direction.EAST: 80,       # Strong morning light
            Direction.SOUTH_EAST: 90, # Excellent morning to midday
            Direction.SOUTH: 100,     # Maximum solar exposure
            Direction.SOUTH_WEST: 95, # Strong afternoon light
            Direction.WEST: 85,       # Strong evening light
            Direction.NORTH_WEST: 50, # Moderate evening light
        }

    def analyze_sunlight_optimization(self, floor_plan: FloorPlan) -> SunlightAnalysis:
        """
        Main method to analyze sunlight optimization
        
        Args:
            floor_plan: Complete floor plan data
            
        Returns:
            SunlightAnalysis with optimization status and recommendations
        """
        issues = []
        
        # Analyze different sunlight aspects
        morning_light_issues = self._check_morning_light_access(floor_plan.rooms)
        kitchen_light_issues = self._check_kitchen_natural_light(floor_plan.rooms)
        living_area_issues = self._check_living_area_brightness(floor_plan.rooms)
        window_optimization_issues = self._check_window_optimization(floor_plan.rooms)
        seasonal_issues = self._analyze_seasonal_considerations(floor_plan)
        
        # Combine all issues
        issues.extend(morning_light_issues)
        issues.extend(kitchen_light_issues)
        issues.extend(living_area_issues)
        issues.extend(window_optimization_issues)
        issues.extend(seasonal_issues)
        
        # Calculate compliance status for each aspect
        morning_light_status = self._determine_morning_light_status(morning_light_issues)
        kitchen_light_status = self._determine_kitchen_light_status(kitchen_light_issues)
        living_brightness_status = self._determine_living_brightness_status(living_area_issues)
        
        # Calculate overall sunlight score
        sunlight_score = self._calculate_sunlight_score(floor_plan.rooms, issues)
        
        # Generate seasonal considerations
        seasonal_considerations = self._generate_seasonal_recommendations(floor_plan)
        
        # Determine overall compliance status
        if sunlight_score >= 80:
            overall_status = ComplianceStatus.COMPLIANT
        elif sunlight_score >= 60:
            overall_status = ComplianceStatus.WARNING
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        return SunlightAnalysis(
            overall_status=overall_status,
            sunlight_score=sunlight_score,
            issues=issues,
            morning_light_access=morning_light_status,
            kitchen_natural_light=kitchen_light_status,
            living_area_brightness=living_brightness_status,
            seasonal_considerations=seasonal_considerations
        )

    def _check_morning_light_access(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check morning light access in priority rooms"""
        issues = []
        
        # Check bedrooms for morning light
        bedrooms = [room for room in rooms if room.type == RoomType.BEDROOM]
        
        for bedroom in bedrooms:
            has_morning_light = bedroom.direction in self.morning_light_directions
            
            if not has_morning_light and bedroom.windows > 0:
                # Bedroom has windows but not oriented for morning light
                issue = ComplianceIssue(
                    id=f"morning_light_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Morning Light",
                    title="Limited Morning Light in Bedroom",
                    description=f"Bedroom faces {bedroom.direction.value}, missing optimal morning sunlight.",
                    affected_rooms=[bedroom.id],
                    suggestions=[
                        "Consider adding windows facing East or North-East",
                        "Use light colors and mirrors to enhance natural light",
                        "Install skylights if side windows are not feasible",
                        "Consider wake-up lighting systems for darker rooms"
                    ]
                )
                issues.append(issue)
            elif bedroom.windows == 0:
                # Bedroom with no windows at all
                issue = ComplianceIssue(
                    id=f"no_windows_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Natural Light",
                    title="Bedroom Lacks Windows",
                    description="Bedroom has no windows for natural light or ventilation.",
                    affected_rooms=[bedroom.id],
                    suggestions=[
                        "Add windows for natural light and ventilation",
                        "East-facing windows provide excellent morning light",
                        "Ensure windows meet minimum size requirements",
                        "Consider ventilation if windows are not possible"
                    ]
                )
                issues.append(issue)
        
        # Check dining room for morning light
        dining_rooms = [room for room in rooms if room.type == RoomType.DINING_ROOM]
        
        for dining_room in dining_rooms:
            if not (dining_room.direction in self.morning_light_directions) and dining_room.windows > 0:
                issue = ComplianceIssue(
                    id=f"dining_morning_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NEEDS_REVIEW,
                    category="Morning Light",
                    title="Dining Room Could Benefit from Morning Light",
                    description=f"Dining room faces {dining_room.direction.value}, missing pleasant morning light for breakfast.",
                    affected_rooms=[dining_room.id],
                    suggestions=[
                        "Morning light enhances dining experience",
                        "Consider East-facing windows if possible",
                        "Ensure adequate artificial lighting for evenings"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_kitchen_natural_light(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check natural light adequacy in kitchen"""
        issues = []
        
        kitchens = [room for room in rooms if room.type == RoomType.KITCHEN]
        
        for kitchen in kitchens:
            # Calculate expected light quality based on direction and windows
            light_quality = self._calculate_light_quality(kitchen)
            
            if kitchen.windows == 0:
                # Kitchen with no natural light
                issue = ComplianceIssue(
                    id=f"kitchen_no_light_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Kitchen Lighting",
                    title="Kitchen Lacks Natural Light",
                    description="Kitchen has no windows for natural light, making food preparation difficult.",
                    affected_rooms=[kitchen.id],
                    suggestions=[
                        "Add windows for natural light during cooking",
                        "South-East windows provide excellent morning light",
                        "Ensure adequate task lighting for food preparation",
                        "Consider skylights if wall windows are limited"
                    ]
                )
                issues.append(issue)
            elif light_quality < 40:
                # Kitchen with poor natural light
                issue = ComplianceIssue(
                    id=f"kitchen_poor_light_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Kitchen Lighting",
                    title="Kitchen Has Limited Natural Light",
                    description=f"Kitchen faces {kitchen.direction.value} with {kitchen.windows} window(s), providing limited natural light.",
                    affected_rooms=[kitchen.id],
                    suggestions=[
                        "Add additional windows if possible",
                        "Use light-colored surfaces to reflect available light",
                        "Install under-cabinet lighting for task illumination",
                        "Consider larger windows for better light penetration"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_living_area_brightness(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check brightness in main living areas"""
        issues = []
        
        living_rooms = [room for room in rooms if room.type == RoomType.LIVING_ROOM]
        
        for living_room in living_rooms:
            light_quality = self._calculate_light_quality(living_room)
            
            # Living rooms should have good natural light throughout the day
            if living_room.windows == 0:
                issue = ComplianceIssue(
                    id=f"living_no_light_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Living Area Lighting",
                    title="Living Room Lacks Windows",
                    description="Main living area has no natural light sources.",
                    affected_rooms=[living_room.id],
                    suggestions=[
                        "Add multiple windows for cross-ventilation and light",
                        "South-facing windows provide consistent daylight",
                        "Consider large windows or sliding doors",
                        "Plan artificial lighting for evening use"
                    ]
                )
                issues.append(issue)
            elif light_quality < 50:
                issue = ComplianceIssue(
                    id=f"living_dim_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Living Area Lighting",
                    title="Living Room Could Be Brighter",
                    description=f"Living room has limited natural light (quality: {light_quality}%).",
                    affected_rooms=[living_room.id],
                    suggestions=[
                        "Add more windows for better daylight",
                        "Consider larger window sizes",
                        "Use light colors for walls and furniture",
                        "Add mirrors to reflect and amplify natural light"
                    ]
                )
                issues.append(issue)
            elif living_room.windows < 2 and living_room.area > 150:
                # Large living rooms should have multiple light sources
                issue = ComplianceIssue(
                    id=f"living_insufficient_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NEEDS_REVIEW,
                    category="Living Area Lighting",
                    title="Large Living Room May Need More Windows",
                    description=f"Living room area ({living_room.area} sq ft) may benefit from additional windows.",
                    affected_rooms=[living_room.id],
                    suggestions=[
                        "Consider multiple windows for even light distribution",
                        "Add windows on different walls for cross-lighting",
                        "Ensure adequate lighting for different seating areas"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_window_optimization(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check overall window placement optimization"""
        issues = []
        
        # Check for rooms with excessive sun exposure
        for room in rooms:
            if room.direction in [Direction.SOUTH, Direction.SOUTH_WEST, Direction.WEST]:
                if room.windows > 2 and room.type not in [RoomType.LIVING_ROOM]:
                    # Rooms with excessive west/south windows may overheat
                    issue = ComplianceIssue(
                        id=f"excessive_sun_{uuid.uuid4().hex[:8]}",
                        severity=ComplianceStatus.NEEDS_REVIEW,
                        category="Sun Exposure",
                        title="Potential Overheating Risk",
                        description=f"{room.type.value.replace('_', ' ').title()} faces {room.direction.value} with {room.windows} windows.",
                        affected_rooms=[room.id],
                        suggestions=[
                            "Consider window shading or overhangs",
                            "Use low-E glass to reduce heat gain",
                            "Install window treatments for sun control",
                            "Ensure adequate ventilation for cooling"
                        ]
                    )
                    issues.append(issue)
        
        # Check for north-facing rooms that might be too dark
        north_facing_rooms = [room for room in rooms if room.direction == Direction.NORTH]
        
        for room in north_facing_rooms:
            if room.type in self.daylight_priority_rooms and room.windows <= 1:
                issue = ComplianceIssue(
                    id=f"north_dark_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Natural Light",
                    title="North-Facing Room May Be Dark",
                    description=f"{room.type.value.replace('_', ' ').title()} faces north with limited windows.",
                    affected_rooms=[room.id],
                    suggestions=[
                        "Add additional windows for north light",
                        "North light is consistent and good for work areas",
                        "Ensure adequate artificial lighting",
                        "Use light colors to maximize available light"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _analyze_seasonal_considerations(self, floor_plan: FloorPlan) -> List[ComplianceIssue]:
        """Analyze seasonal sunlight patterns"""
        issues = []
        
        # Check for potential summer overheating
        south_west_rooms = [
            room for room in floor_plan.rooms 
            if room.direction in [Direction.SOUTH_WEST, Direction.WEST] 
            and room.windows >= 2
        ]
        
        if south_west_rooms:
            room_names = [room.type.value.replace('_', ' ').title() for room in south_west_rooms]
            issue = ComplianceIssue(
                id=f"summer_heat_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NEEDS_REVIEW,
                category="Seasonal Comfort",
                title="Summer Cooling Consideration",
                description=f"Rooms facing south-west may experience excessive heat in summer: {', '.join(room_names)}",
                affected_rooms=[room.id for room in south_west_rooms],
                suggestions=[
                    "Plan for summer shading solutions",
                    "Consider deciduous trees for seasonal shade",
                    "Install window overhangs or awnings",
                    "Ensure adequate ventilation and cooling"
                ]
            )
            issues.append(issue)
        
        # Check for winter light access
        limited_winter_light = [
            room for room in floor_plan.rooms
            if room.direction in [Direction.NORTH, Direction.NORTH_WEST]
            and room.type in self.daylight_priority_rooms
        ]
        
        if limited_winter_light:
            issue = ComplianceIssue(
                id=f"winter_light_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NEEDS_REVIEW,
                category="Seasonal Comfort",
                title="Winter Light Planning",
                description="Some rooms may have limited natural light during winter months.",
                affected_rooms=[room.id for room in limited_winter_light],
                suggestions=[
                    "Plan adequate artificial lighting for winter",
                    "Use warm light colors during darker months",
                    "Consider light therapy options",
                    "Maximize available daylight with light colors"
                ]
            )
            issues.append(issue)
        
        return issues

    def _calculate_light_quality(self, room: Room) -> float:
        """Calculate light quality score for a room"""
        if room.windows == 0:
            return 0
        
        # Base score from solar intensity
        base_intensity = self.solar_intensity.get(room.direction, 30)
        
        # Adjust for number of windows (diminishing returns)
        window_multiplier = min(1.0 + (room.windows - 1) * 0.3, 2.0)
        
        # Adjust for room size (larger rooms need more light)
        area_factor = min(room.area / 100.0, 1.5)  # Normalize to 100 sq ft baseline
        size_adjustment = 1.0 / area_factor if area_factor > 1.0 else 1.0
        
        quality_score = base_intensity * window_multiplier * size_adjustment
        
        return min(quality_score, 100.0)

    def _determine_morning_light_status(self, issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine morning light compliance status"""
        if not issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.WARNING in severities:
            return ComplianceStatus.WARNING
        else:
            return ComplianceStatus.NEEDS_REVIEW

    def _determine_kitchen_light_status(self, issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine kitchen lighting status"""
        kitchen_issues = [issue for issue in issues if "kitchen" in issue.title.lower()]
        
        if not kitchen_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in kitchen_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.WARNING

    def _determine_living_brightness_status(self, issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine living area brightness status"""
        living_issues = [issue for issue in issues if "living" in issue.title.lower()]
        
        if not living_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in living_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.WARNING in severities:
            return ComplianceStatus.WARNING
        else:
            return ComplianceStatus.NEEDS_REVIEW

    def _calculate_sunlight_score(self, rooms: List[Room], issues: List[ComplianceIssue]) -> float:
        """Calculate overall sunlight optimization score"""
        
        # Start with base score
        score = 80.0
        
        # Add points for good natural light
        for room in rooms:
            light_quality = self._calculate_light_quality(room)
            
            # Reward high-quality natural light
            if light_quality >= 80:
                score += 3
            elif light_quality >= 60:
                score += 2
            elif light_quality >= 40:
                score += 1
            
            # Bonus for optimal room-direction pairing
            if room.type in self.morning_light_rooms and room.direction in self.morning_light_directions:
                score += 2
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == ComplianceStatus.NON_COMPLIANT:
                score -= 12
            elif issue.severity == ComplianceStatus.WARNING:
                score -= 6
            elif issue.severity == ComplianceStatus.NEEDS_REVIEW:
                score -= 2
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))

    def _generate_seasonal_recommendations(self, floor_plan: FloorPlan) -> List[str]:
        """Generate seasonal sunlight recommendations"""
        recommendations = []
        
        # Check building orientation
        south_facing_rooms = len([r for r in floor_plan.rooms if r.direction == Direction.SOUTH])
        west_facing_rooms = len([r for r in floor_plan.rooms if r.direction == Direction.WEST])
        
        if south_facing_rooms > west_facing_rooms:
            recommendations.append("Good south-facing orientation provides consistent winter light")
            recommendations.append("Consider summer shading for south windows")
        
        if west_facing_rooms >= 2:
            recommendations.append("West-facing windows may cause afternoon overheating in summer")
            recommendations.append("Plan for evening glare control with appropriate window treatments")
        
        # General seasonal advice
        recommendations.extend([
            "Use deciduous landscaping for seasonal shade control",
            "Consider adjustable window treatments for year-round comfort",
            "Plan artificial lighting to supplement natural light in winter"
        ])
        
        return recommendations[:4]  # Limit to most relevant recommendations

    def get_sunlight_summary(self, analysis: SunlightAnalysis) -> Dict[str, any]:
        """Generate a summary of sunlight analysis for dashboard display"""
        
        # Count issues by severity
        critical_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NON_COMPLIANT])
        warning_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.WARNING])
        review_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NEEDS_REVIEW])
        
        return {
            "overall_status": analysis.overall_status.value,
            "sunlight_score": analysis.sunlight_score,
            "total_issues": len(analysis.issues),
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "review_issues": review_issues,
            "aspect_status": {
                "morning_light": analysis.morning_light_access.value,
                "kitchen_light": analysis.kitchen_natural_light.value,
                "living_brightness": analysis.living_area_brightness.value
            },
            "seasonal_tips": len(analysis.seasonal_considerations)
        }
