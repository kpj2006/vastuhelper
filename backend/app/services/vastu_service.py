"""
Vastu Shastra Compliance Service

This service implements Vastu Shastra principles for floor plan analysis including:
- Room direction and placement rules
- Main entrance positioning
- Kitchen and bathroom placement
- Pooja room compliance
- Energy flow optimization

Based on traditional Vastu principles with modern adaptations.
"""

from typing import List, Dict, Optional
from app.models.schemas import (
    FloorPlan, Room, VastuAnalysis, ComplianceIssue,
    ComplianceStatus, RoomType, Direction
)
import uuid

class VastuService:
    """Service class for Vastu Shastra compliance analysis"""
    
    def __init__(self):
        """Initialize with Vastu Shastra rules and preferences"""
        
        # Ideal directions for different room types
        self.ideal_room_directions = {
            RoomType.BEDROOM: [Direction.SOUTH_WEST, Direction.SOUTH, Direction.WEST],
            RoomType.LIVING_ROOM: [Direction.NORTH, Direction.NORTH_EAST, Direction.EAST],
            RoomType.KITCHEN: [Direction.SOUTH_EAST, Direction.SOUTH],
            RoomType.BATHROOM: [Direction.SOUTH, Direction.WEST, Direction.SOUTH_WEST],
            RoomType.DINING_ROOM: [Direction.WEST, Direction.NORTH_WEST, Direction.NORTH],
            RoomType.STUDY: [Direction.NORTH_EAST, Direction.NORTH, Direction.EAST],
            RoomType.POOJA_ROOM: [Direction.NORTH_EAST, Direction.NORTH, Direction.EAST],
            RoomType.STORAGE: [Direction.SOUTH_WEST, Direction.WEST, Direction.SOUTH],
            RoomType.STAIRCASE: [Direction.SOUTH_WEST, Direction.SOUTH, Direction.WEST],
        }
        
        # Directions to avoid for specific rooms
        self.avoid_directions = {
            RoomType.KITCHEN: [Direction.NORTH, Direction.NORTH_EAST, Direction.NORTH_WEST],
            RoomType.BATHROOM: [Direction.NORTH_EAST, Direction.NORTH],
            RoomType.POOJA_ROOM: [Direction.SOUTH, Direction.SOUTH_WEST, Direction.WEST],
            RoomType.BEDROOM: [Direction.NORTH_EAST],  # Avoid NE for master bedroom
        }
        
        # Main entrance preferences (in order of preference)
        self.entrance_preferences = [
            Direction.NORTH_EAST, Direction.NORTH, Direction.EAST,
            Direction.WEST, Direction.SOUTH, Direction.SOUTH_EAST
        ]

    def analyze_vastu_compliance(self, floor_plan: FloorPlan) -> VastuAnalysis:
        """
        Main method to analyze Vastu Shastra compliance
        
        Args:
            floor_plan: Complete floor plan data
            
        Returns:
            VastuAnalysis with compliance status and issues
        """
        issues = []
        
        # Analyze different Vastu aspects
        entrance_issues = self._check_main_entrance(floor_plan.rooms)
        kitchen_issues = self._check_kitchen_placement(floor_plan.rooms)
        bedroom_issues = self._check_bedroom_directions(floor_plan.rooms)
        pooja_room_issues = self._check_pooja_room_compliance(floor_plan.rooms)
        general_placement_issues = self._check_general_room_placements(floor_plan.rooms)
        
        # Combine all issues
        issues.extend(entrance_issues)
        issues.extend(kitchen_issues)
        issues.extend(bedroom_issues)
        issues.extend(pooja_room_issues)
        issues.extend(general_placement_issues)
        
        # Calculate compliance status for each aspect
        main_entrance_status = self._determine_entrance_status(entrance_issues)
        kitchen_status = self._determine_kitchen_status(kitchen_issues)
        bedroom_status = self._determine_bedroom_status(bedroom_issues)
        pooja_status = self._determine_pooja_status(pooja_room_issues)
        
        # Calculate overall Vastu score
        vastu_score = self._calculate_vastu_score(floor_plan.rooms, issues)
        
        # Determine overall compliance status
        if vastu_score >= 85:
            overall_status = ComplianceStatus.COMPLIANT
        elif vastu_score >= 65:
            overall_status = ComplianceStatus.WARNING
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        return VastuAnalysis(
            overall_status=overall_status,
            vastu_score=vastu_score,
            issues=issues,
            main_entrance_direction=main_entrance_status,
            kitchen_placement=kitchen_status,
            bedroom_directions=bedroom_status,
            pooja_room_compliance=pooja_status
        )

    def _check_main_entrance(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check main entrance direction compliance"""
        issues = []
        
        # Find the main entrance (assume living room represents main entrance area)
        living_rooms = [room for room in rooms if room.type == RoomType.LIVING_ROOM]
        
        if not living_rooms:
            # No clear main entrance area identified
            issue = ComplianceIssue(
                id=f"entrance_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NEEDS_REVIEW,
                category="Main Entrance",
                title="Main Entrance Not Clearly Defined",
                description="Unable to identify main entrance area for Vastu analysis.",
                affected_rooms=[],
                suggestions=[
                    "Clearly define main entrance location",
                    "Consider entrance in North-East direction",
                    "Ensure entrance is well-lit and welcoming"
                ]
            )
            issues.append(issue)
            return issues
        
        main_entrance_room = living_rooms[0]  # Use first living room as reference
        entrance_direction = main_entrance_room.direction
        
        # Check if entrance direction is optimal
        if entrance_direction in self.entrance_preferences[:3]:  # Top 3 preferences
            # Good entrance direction - no issues
            pass
        elif entrance_direction in self.entrance_preferences[3:]:  # Acceptable but not ideal
            issue = ComplianceIssue(
                id=f"entrance_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.WARNING,
                category="Main Entrance",
                title="Entrance Direction Could Be Better",
                description=f"Main entrance faces {entrance_direction.value}, which is acceptable but not optimal.",
                affected_rooms=[main_entrance_room.id],
                suggestions=[
                    "Consider North-East entrance for best Vastu compliance",
                    "North or East entrances are also favorable",
                    "Enhance entrance with proper lighting and decor"
                ]
            )
            issues.append(issue)
        else:
            # Avoid South-West entrance
            issue = ComplianceIssue(
                id=f"entrance_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NON_COMPLIANT,
                category="Main Entrance",
                title="Unfavorable Entrance Direction",
                description=f"Main entrance faces {entrance_direction.value}, which is not recommended in Vastu.",
                affected_rooms=[main_entrance_room.id],
                suggestions=[
                    "If possible, create entrance in North-East direction",
                    "Use Vastu remedies like proper lighting and symbols",
                    "Consider relocating main entrance"
                ]
            )
            issues.append(issue)
        
        return issues

    def _check_kitchen_placement(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check kitchen placement and direction"""
        issues = []
        
        kitchens = [room for room in rooms if room.type == RoomType.KITCHEN]
        
        if not kitchens:
            # No kitchen found - this might be intentional (e.g., apartment without kitchen)
            return issues
        
        for kitchen in kitchens:
            kitchen_direction = kitchen.direction
            
            # Check if kitchen is in ideal direction
            if kitchen_direction in self.ideal_room_directions[RoomType.KITCHEN]:
                # Perfect kitchen placement
                continue
            elif kitchen_direction in self.avoid_directions[RoomType.KITCHEN]:
                # Kitchen in unfavorable direction
                issue = ComplianceIssue(
                    id=f"kitchen_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Kitchen Placement",
                    title="Kitchen in Unfavorable Direction",
                    description=f"Kitchen faces {kitchen_direction.value}, which should be avoided according to Vastu.",
                    affected_rooms=[kitchen.id],
                    suggestions=[
                        "Ideal kitchen direction is South-East",
                        "South direction is also acceptable",
                        "Use Vastu remedies if relocation is not possible",
                        "Ensure proper ventilation and lighting"
                    ]
                )
                issues.append(issue)
            else:
                # Kitchen in acceptable but not ideal direction
                issue = ComplianceIssue(
                    id=f"kitchen_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Kitchen Placement",
                    title="Kitchen Direction Not Optimal",
                    description=f"Kitchen faces {kitchen_direction.value}, which is acceptable but not ideal.",
                    affected_rooms=[kitchen.id],
                    suggestions=[
                        "South-East is the most favorable direction for kitchen",
                        "Ensure cooking is done facing East while preparing food",
                        "Keep kitchen clean and well-organized"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_bedroom_directions(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check bedroom placement and directions"""
        issues = []
        
        bedrooms = [room for room in rooms if room.type == RoomType.BEDROOM]
        
        for bedroom in bedrooms:
            bedroom_direction = bedroom.direction
            
            # Check for master bedroom (assume largest bedroom is master)
            is_master_bedroom = bedroom.area == max(r.area for r in bedrooms if r.type == RoomType.BEDROOM)
            
            # Check direction compliance
            if bedroom_direction in self.ideal_room_directions[RoomType.BEDROOM]:
                # Good bedroom placement
                continue
            elif bedroom_direction in self.avoid_directions[RoomType.BEDROOM]:
                # Bedroom in direction to avoid
                severity = ComplianceStatus.NON_COMPLIANT if is_master_bedroom else ComplianceStatus.WARNING
                
                issue = ComplianceIssue(
                    id=f"bedroom_{uuid.uuid4().hex[:8]}",
                    severity=severity,
                    category="Bedroom Placement",
                    title=f"{'Master ' if is_master_bedroom else ''}Bedroom in Unfavorable Direction",
                    description=f"Bedroom faces {bedroom_direction.value}, which should be avoided for bedrooms.",
                    affected_rooms=[bedroom.id],
                    suggestions=[
                        "South-West is ideal for master bedroom",
                        "South and West are also favorable",
                        "Avoid North-East for bedrooms, especially master bedroom",
                        "Place bed with head towards South or West"
                    ]
                )
                issues.append(issue)
            else:
                # Acceptable but not ideal
                issue = ComplianceIssue(
                    id=f"bedroom_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Bedroom Placement",
                    title="Bedroom Direction Not Optimal",
                    description=f"Bedroom faces {bedroom_direction.value}, which is acceptable but not ideal.",
                    affected_rooms=[bedroom.id],
                    suggestions=[
                        "South-West is most favorable for master bedroom",
                        "Ensure bed placement follows Vastu guidelines",
                        "Use appropriate colors and decor for the direction"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_pooja_room_compliance(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check Pooja (prayer) room placement"""
        issues = []
        
        pooja_rooms = [room for room in rooms if room.type == RoomType.POOJA_ROOM]
        
        if not pooja_rooms:
            # No dedicated pooja room - suggest creating one
            issue = ComplianceIssue(
                id=f"pooja_{uuid.uuid4().hex[:8]}",
                severity=ComplianceStatus.NEEDS_REVIEW,
                category="Pooja Room",
                title="No Dedicated Pooja Room",
                description="Consider creating a dedicated space for prayers and meditation.",
                affected_rooms=[],
                suggestions=[
                    "Create pooja area in North-East direction",
                    "Small corner in North-East can serve as prayer space",
                    "Ensure the area is clean and peaceful"
                ]
            )
            issues.append(issue)
            return issues
        
        for pooja_room in pooja_rooms:
            pooja_direction = pooja_room.direction
            
            if pooja_direction in self.ideal_room_directions[RoomType.POOJA_ROOM]:
                # Perfect pooja room placement
                continue
            elif pooja_direction in self.avoid_directions[RoomType.POOJA_ROOM]:
                # Pooja room in unfavorable direction
                issue = ComplianceIssue(
                    id=f"pooja_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NON_COMPLIANT,
                    category="Pooja Room",
                    title="Pooja Room in Unfavorable Direction",
                    description=f"Pooja room faces {pooja_direction.value}, which is not recommended for prayer space.",
                    affected_rooms=[pooja_room.id],
                    suggestions=[
                        "North-East is the most auspicious direction for pooja room",
                        "North and East are also favorable",
                        "Avoid South, South-West, and West for pooja room",
                        "Consider relocating prayer space if possible"
                    ]
                )
                issues.append(issue)
            else:
                # Acceptable but not ideal
                issue = ComplianceIssue(
                    id=f"pooja_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Pooja Room",
                    title="Pooja Room Direction Not Ideal",
                    description=f"Pooja room faces {pooja_direction.value}, consider better positioning.",
                    affected_rooms=[pooja_room.id],
                    suggestions=[
                        "North-East direction is most favorable for pooja room",
                        "Face East or North while praying",
                        "Keep the space clean and well-ventilated"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _check_general_room_placements(self, rooms: List[Room]) -> List[ComplianceIssue]:
        """Check general room placements for other room types"""
        issues = []
        
        for room in rooms:
            # Skip rooms already checked in specific methods
            if room.type in [RoomType.KITCHEN, RoomType.BEDROOM, RoomType.POOJA_ROOM]:
                continue
            
            # Skip rooms without specific Vastu requirements
            if room.type not in self.ideal_room_directions:
                continue
            
            room_direction = room.direction
            ideal_directions = self.ideal_room_directions[room.type]
            avoid_directions = self.avoid_directions.get(room.type, [])
            
            if room_direction in avoid_directions:
                # Room in direction to avoid
                issue = ComplianceIssue(
                    id=f"room_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.WARNING,
                    category="Room Placement",
                    title=f"{room.type.value.replace('_', ' ').title()} in Less Favorable Direction",
                    description=f"{room.type.value.replace('_', ' ').title()} faces {room_direction.value}, which could be better positioned.",
                    affected_rooms=[room.id],
                    suggestions=[
                        f"Ideal directions: {', '.join([d.value for d in ideal_directions])}",
                        "Consider room function when planning layout",
                        "Use appropriate colors and lighting for the direction"
                    ]
                )
                issues.append(issue)
            elif room_direction not in ideal_directions:
                # Room not in ideal direction but not necessarily bad
                issue = ComplianceIssue(
                    id=f"room_{uuid.uuid4().hex[:8]}",
                    severity=ComplianceStatus.NEEDS_REVIEW,
                    category="Room Placement",
                    title=f"{room.type.value.replace('_', ' ').title()} Direction Review",
                    description=f"{room.type.value.replace('_', ' ').title()} could benefit from better directional placement.",
                    affected_rooms=[room.id],
                    suggestions=[
                        f"Consider directions: {', '.join([d.value for d in ideal_directions])}",
                        "Current placement is acceptable if other factors are favorable",
                        "Focus on proper lighting and ventilation"
                    ]
                )
                issues.append(issue)
        
        return issues

    def _determine_entrance_status(self, entrance_issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine entrance compliance status"""
        if not entrance_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in entrance_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.WARNING in severities:
            return ComplianceStatus.WARNING
        else:
            return ComplianceStatus.NEEDS_REVIEW

    def _determine_kitchen_status(self, kitchen_issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine kitchen compliance status"""
        if not kitchen_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in kitchen_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.WARNING

    def _determine_bedroom_status(self, bedroom_issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine bedroom compliance status"""
        if not bedroom_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in bedroom_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.WARNING in severities:
            return ComplianceStatus.WARNING
        else:
            return ComplianceStatus.NEEDS_REVIEW

    def _determine_pooja_status(self, pooja_issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine pooja room compliance status"""
        if not pooja_issues:
            return ComplianceStatus.COMPLIANT
        
        severities = [issue.severity for issue in pooja_issues]
        
        if ComplianceStatus.NON_COMPLIANT in severities:
            return ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.WARNING in severities:
            return ComplianceStatus.WARNING
        else:
            return ComplianceStatus.NEEDS_REVIEW

    def _calculate_vastu_score(self, rooms: List[Room], issues: List[ComplianceIssue]) -> float:
        """Calculate overall Vastu compliance score"""
        
        # Base score starts at 100
        score = 100.0
        
        # Deduct points based on issue severity
        for issue in issues:
            if issue.severity == ComplianceStatus.NON_COMPLIANT:
                score -= 15  # Major deduction for non-compliance
            elif issue.severity == ComplianceStatus.WARNING:
                score -= 8   # Moderate deduction for warnings
            elif issue.severity == ComplianceStatus.NEEDS_REVIEW:
                score -= 3   # Minor deduction for review items
        
        # Add bonus points for ideal placements
        bonus_points = 0
        for room in rooms:
            if room.type in self.ideal_room_directions:
                ideal_directions = self.ideal_room_directions[room.type]
                if room.direction in ideal_directions:
                    # Give bonus for ideal placement
                    if room.type in [RoomType.KITCHEN, RoomType.POOJA_ROOM]:
                        bonus_points += 3  # Important rooms get more bonus
                    else:
                        bonus_points += 1
        
        score += bonus_points
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))

    def get_vastu_summary(self, analysis: VastuAnalysis) -> Dict[str, any]:
        """Generate a summary of Vastu analysis for dashboard display"""
        
        # Count issues by severity
        critical_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NON_COMPLIANT])
        warning_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.WARNING])
        review_issues = len([i for i in analysis.issues if i.severity == ComplianceStatus.NEEDS_REVIEW])
        
        return {
            "overall_status": analysis.overall_status.value,
            "vastu_score": analysis.vastu_score,
            "total_issues": len(analysis.issues),
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "review_issues": review_issues,
            "aspect_status": {
                "entrance": analysis.main_entrance_direction.value,
                "kitchen": analysis.kitchen_placement.value,
                "bedrooms": analysis.bedroom_directions.value,
                "pooja_room": analysis.pooja_room_compliance.value
            }
        }
