"""
Upload Router

API endpoints for handling floor plan image uploads and processing including:
- File upload with validation
- Image preprocessing  
- Mock AI processing to extract room data
- Sample data generation for testing

Currently uses mock AI processing but structured for real AI integration.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, Dict, List
import os
import uuid
import shutil
from datetime import datetime
import json

# Import for image processing (when real AI is integrated)
from PIL import Image
import io

# Import data models
from app.models.schemas import FloorPlan, Room, BuildingInfo, Coordinates, RoomType, Direction

# Create router instance
router = APIRouter()

# Configuration
UPLOAD_DIR = "uploaded_files"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/floor-plan")
async def upload_floor_plan(
    file: UploadFile = File(...),
    building_type: str = Form("residential"),
    total_area: Optional[float] = Form(None)
):
    """
    Upload and process floor plan image
    
    Args:
        file: Floor plan image file
        building_type: Type of building (residential/commercial)
        total_area: Total building area (optional, will be estimated if not provided)
        
    Returns:
        Processed floor plan data with extracted room information
    """
    try:
        # Validate file
        validation_result = await _validate_uploaded_file(file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # Save uploaded file
        file_info = await _save_uploaded_file(file)
        
        # Process image and extract floor plan data (currently mocked)
        floor_plan_data = await _process_floor_plan_image(
            file_info["file_path"], 
            building_type,
            total_area
        )
        
        return {
            "success": True,
            "message": "Floor plan uploaded and processed successfully",
            "data": {
                "file_info": file_info,
                "floor_plan": floor_plan_data.dict()
            },
            "processing_time": 0.5  # Mock processing time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Floor plan processing failed: {str(e)}"
        )

@router.post("/sample-data")
async def generate_sample_data(
    building_type: str = "residential",
    complexity: str = "medium"
) -> Dict:
    """
    Generate sample floor plan data for testing
    
    Args:
        building_type: Type of building to simulate
        complexity: Complexity level (simple/medium/complex)
        
    Returns:
        Sample floor plan data
    """
    try:
        floor_plan = _generate_sample_floor_plan(building_type, complexity)
        
        return {
            "success": True,
            "message": f"Sample {complexity} {building_type} floor plan generated",
            "data": {
                "floor_plan": floor_plan.dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sample data generation failed: {str(e)}"
        )

@router.get("/sample-templates")
async def get_sample_templates():
    """
    Get available sample floor plan templates
    
    Returns:
        List of available sample templates
    """
    return {
        "templates": [
            {
                "id": "small_apartment",
                "name": "Small Apartment",
                "description": "2-bedroom apartment with basic amenities",
                "building_type": "residential",
                "complexity": "simple",
                "estimated_area": 800
            },
            {
                "id": "family_home",
                "name": "Family Home",
                "description": "3-bedroom house with living areas and kitchen",
                "building_type": "residential", 
                "complexity": "medium",
                "estimated_area": 1200
            },
            {
                "id": "large_house",
                "name": "Large House",
                "description": "4-bedroom house with multiple living areas",
                "building_type": "residential",
                "complexity": "complex",
                "estimated_area": 2000
            }
        ]
    }

@router.get("/upload-status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Check the status of a file upload and processing
    
    Args:
        file_id: Unique file identifier
        
    Returns:
        Upload and processing status
    """
    # In a real implementation, this would check a database or cache
    # For now, return a mock status
    return {
        "file_id": file_id,
        "status": "completed",
        "message": "File processed successfully",
        "timestamp": datetime.now().isoformat()
    }

# Helper functions

async def _validate_uploaded_file(file: UploadFile) -> Dict[str, any]:
    """Validate uploaded file for type, size, and content"""
    
    # Check file extension
    file_extension = os.path.splitext(file.filename.lower())[1]
    if file_extension not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"File type {file_extension} not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
        }
    
    # Read file content to check size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(content) > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File size ({len(content)} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)"
        }
    
    # Basic image validation
    try:
        image = Image.open(io.BytesIO(content))
        # Check if it's a valid image and has reasonable dimensions
        if image.width < 100 or image.height < 100:
            return {
                "valid": False,
                "error": "Image dimensions too small. Minimum 100x100 pixels required."
            }
        if image.width > 10000 or image.height > 10000:
            return {
                "valid": False, 
                "error": "Image dimensions too large. Maximum 10000x10000 pixels allowed."
            }
    except Exception:
        return {
            "valid": False,
            "error": "Invalid image file or corrupted image data"
        }
    
    return {"valid": True}

async def _save_uploaded_file(file: UploadFile) -> Dict[str, any]:
    """Save uploaded file and return file information"""
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file info
    file_size = os.path.getsize(file_path)
    
    return {
        "file_id": file_id,
        "original_filename": file.filename,
        "unique_filename": unique_filename,
        "file_path": file_path,
        "file_size": file_size,
        "upload_timestamp": datetime.now().isoformat()
    }

async def _process_floor_plan_image(
    file_path: str,
    building_type: str,
    total_area: Optional[float]
) -> FloorPlan:
    """
    Process floor plan image and extract room data
    
    Currently returns mock data, but structured for real AI integration
    """
    
    # Load and analyze image (mock implementation)
    image = Image.open(file_path)
    image_width, image_height = image.size
    
    # Estimate total area if not provided
    if total_area is None:
        # Mock area estimation based on image size and building type
        area_factor = 0.8 if building_type == "residential" else 1.2
        total_area = (image_width * image_height / 1000) * area_factor
    
    # Generate mock room data based on image analysis
    rooms = _generate_rooms_from_image_analysis(image_width, image_height, building_type, total_area)
    
    # Create building info
    building_info = BuildingInfo(
        total_area=total_area,
        floors=1,  # Mock: assume single floor
        building_type=building_type,
        construction_year=None,
        location_coordinates=None
    )
    
    # Create floor plan object
    floor_plan = FloorPlan(
        rooms=rooms,
        building_info=building_info,
        image_metadata={
            "original_width": image_width,
            "original_height": image_height,
            "format": image.format,
            "file_path": file_path
        }
    )
    
    return floor_plan

def _generate_rooms_from_image_analysis(
    image_width: int,
    image_height: int,
    building_type: str,
    total_area: float
) -> List[Room]:
    """
    Generate room data from mock image analysis
    
    In real implementation, this would use computer vision and ML models
    """
    
    rooms = []
    
    # Mock room generation based on building type and size
    if building_type == "residential":
        if total_area < 800:  # Small apartment
            room_configs = [
                {"type": RoomType.LIVING_ROOM, "area_ratio": 0.3, "direction": Direction.SOUTH},
                {"type": RoomType.BEDROOM, "area_ratio": 0.25, "direction": Direction.EAST},
                {"type": RoomType.KITCHEN, "area_ratio": 0.15, "direction": Direction.SOUTH_EAST},
                {"type": RoomType.BATHROOM, "area_ratio": 0.1, "direction": Direction.WEST},
                {"type": RoomType.CORRIDOR, "area_ratio": 0.2, "direction": Direction.NORTH}
            ]
        elif total_area < 1500:  # Medium house
            room_configs = [
                {"type": RoomType.LIVING_ROOM, "area_ratio": 0.2, "direction": Direction.SOUTH},
                {"type": RoomType.BEDROOM, "area_ratio": 0.18, "direction": Direction.SOUTH_WEST},
                {"type": RoomType.BEDROOM, "area_ratio": 0.15, "direction": Direction.WEST},
                {"type": RoomType.KITCHEN, "area_ratio": 0.12, "direction": Direction.SOUTH_EAST},
                {"type": RoomType.DINING_ROOM, "area_ratio": 0.1, "direction": Direction.NORTH},
                {"type": RoomType.BATHROOM, "area_ratio": 0.08, "direction": Direction.NORTH_WEST},
                {"type": RoomType.BATHROOM, "area_ratio": 0.05, "direction": Direction.WEST},
                {"type": RoomType.CORRIDOR, "area_ratio": 0.12, "direction": Direction.NORTH}
            ]
        else:  # Large house
            room_configs = [
                {"type": RoomType.LIVING_ROOM, "area_ratio": 0.18, "direction": Direction.SOUTH},
                {"type": RoomType.BEDROOM, "area_ratio": 0.15, "direction": Direction.SOUTH_WEST},
                {"type": RoomType.BEDROOM, "area_ratio": 0.12, "direction": Direction.WEST},
                {"type": RoomType.BEDROOM, "area_ratio": 0.1, "direction": Direction.NORTH_WEST},
                {"type": RoomType.KITCHEN, "area_ratio": 0.1, "direction": Direction.SOUTH_EAST},
                {"type": RoomType.DINING_ROOM, "area_ratio": 0.08, "direction": Direction.NORTH},
                {"type": RoomType.STUDY, "area_ratio": 0.08, "direction": Direction.NORTH_EAST},
                {"type": RoomType.BATHROOM, "area_ratio": 0.06, "direction": Direction.NORTH_WEST},
                {"type": RoomType.BATHROOM, "area_ratio": 0.04, "direction": Direction.WEST},
                {"type": RoomType.STORAGE, "area_ratio": 0.03, "direction": Direction.SOUTH_WEST},
                {"type": RoomType.CORRIDOR, "area_ratio": 0.06, "direction": Direction.NORTH}
            ]
    else:  # Commercial
        room_configs = [
            {"type": RoomType.LIVING_ROOM, "area_ratio": 0.4, "direction": Direction.SOUTH},  # Main area
            {"type": RoomType.BATHROOM, "area_ratio": 0.1, "direction": Direction.NORTH},
            {"type": RoomType.STORAGE, "area_ratio": 0.2, "direction": Direction.WEST},
            {"type": RoomType.CORRIDOR, "area_ratio": 0.3, "direction": Direction.EAST}
        ]
    
    # Generate room objects
    current_y = 0
    room_id = 1
    
    for config in room_configs:
        room_area = total_area * config["area_ratio"]
        
        # Calculate room dimensions (mock layout)
        room_width = min(image_width * 0.8, max(100, room_area ** 0.5 * 10))
        room_height = room_area / (room_width / 10)  # Adjust for scaling
        
        # Mock window count based on room type and area
        windows = _calculate_mock_windows(config["type"], room_area)
        
        room = Room(
            id=f"room_{room_id}",
            type=config["type"],
            name=None,
            area=room_area,
            direction=config["direction"],
            windows=windows,
            doors=1,  # Mock: assume all rooms have at least 1 door
            coordinates=Coordinates(
                x=50,  # Mock x position
                y=current_y,
                width=room_width,
                height=room_height
            ),
            has_natural_ventilation=windows > 0
        )
        
        rooms.append(room)
        current_y += room_height + 10  # Mock spacing
        room_id += 1
    
    return rooms

def _calculate_mock_windows(room_type: RoomType, area: float) -> int:
    """Calculate mock window count based on room type and area"""
    
    base_windows = {
        RoomType.LIVING_ROOM: 2,
        RoomType.BEDROOM: 1,
        RoomType.KITCHEN: 1,
        RoomType.DINING_ROOM: 1,
        RoomType.STUDY: 1,
        RoomType.BATHROOM: 0,
        RoomType.CORRIDOR: 0,
        RoomType.STORAGE: 0,
        RoomType.POOJA_ROOM: 1
    }
    
    base_count = base_windows.get(room_type, 0)
    
    # Add extra windows for larger rooms
    if area > 150:
        base_count += 1
    if area > 300:
        base_count += 1
    
    return base_count

def _generate_sample_floor_plan(building_type: str, complexity: str) -> FloorPlan:
    """Generate sample floor plan for testing purposes"""
    
    # Define area based on complexity
    area_map = {
        "simple": 800,
        "medium": 1200,
        "complex": 2000
    }
    
    total_area = area_map.get(complexity, 1200)
    
    # Generate mock room data
    rooms = _generate_rooms_from_image_analysis(800, 600, building_type, total_area)
    
    building_info = BuildingInfo(
        total_area=total_area,
        floors=1,
        building_type=building_type,
        construction_year=2023,
        location_coordinates={"lat": 28.6139, "lng": 77.2090}  # Mock: Delhi coordinates
    )
    
    floor_plan = FloorPlan(
        rooms=rooms,
        building_info=building_info,
        image_metadata={
            "generated": True,
            "complexity": complexity,
            "sample_type": building_type
        }
    )
    
    return floor_plan
