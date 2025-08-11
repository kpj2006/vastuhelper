# AI Floor Plan Compliance Checker

A modern full-stack application that analyzes floor plans for building code compliance, Vastu Shastra rules, and sunlight optimization.

## 🚀 Features

- **Upload Floor Plans**: Drag-and-drop or browse to upload floor plan images
- **AI Analysis**: Detects rooms, windows, and walls (currently mocked for demo)
- **Multi-Layer Compliance Check**:
  - Building Code Violations (room sizes, window requirements, exit paths)
  - Vastu Shastra Rules (room directions and placement)
  - Sunlight Analysis (optimal room positioning)
- **Interactive Dashboard**: Beautiful cards showing compliance status and suggestions
- **Dark/Light Theme**: Toggle between themes for better user experience
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

### Frontend
- **React 18** with hooks and modern patterns
- **Tailwind CSS** for styling and responsive design
- **Lucide React** for beautiful icons
- **Axios** for API communication

### Backend
- **FastAPI** (Python) for high-performance REST API
- **Pydantic** for data validation
- **CORS** enabled for cross-origin requests
- **Uvicorn** ASGI server

## 📦 Project Structure

```
ai-floor-plan-checker/
├── frontend/                 # React frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── utils/           # Utility functions
│   │   └── App.js           # Main app component
│   ├── package.json
│   └── tailwind.config.js
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Business logic services
│   │   ├── routers/         # API route handlers
│   │   └── main.py          # FastAPI app entry point
│   ├── requirements.txt
│   └── sample_data/         # Mock data for testing
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.8+
- Git

### 1. Clone and Setup

```bash
cd ai-floor-plan-checker
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔌 API Endpoints

- `POST /api/analyze/building-codes` - Check building code compliance
- `POST /api/analyze/vastu` - Check Vastu Shastra compliance  
- `POST /api/analyze/sunlight` - Analyze sunlight optimization
- `POST /api/analyze/complete` - Run all compliance checks

## 🧠 How It Works

### Current Implementation (Mock/Demo)
1. **Image Upload**: Users upload floor plan images
2. **Mock AI Processing**: Simulates room detection with dummy data
3. **Rule Engine**: Applies building codes, Vastu, and sunlight rules
4. **Results Dashboard**: Shows compliance status with actionable suggestions

### Floor Plan Data Structure
```json
{
  "rooms": [
    {
      "id": "room_1",
      "type": "bedroom",
      "area": 120,
      "direction": "north",
      "windows": 2,
      "doors": 1,
      "coordinates": {"x": 100, "y": 150, "width": 200, "height": 150}
    }
  ],
  "building_info": {
    "total_area": 1200,
    "floors": 1,
    "building_type": "residential"
  }
}
```

## 🚀 Extending with Real AI

To integrate real AI models:

### 1. Replace Mock Detection
```python
# In backend/app/services/ai_service.py
def detect_rooms_and_features(image_path):
    # Replace mock implementation with:
    # - YOLOv8 for object detection
    # - Computer vision for floor plan analysis
    # - OCR for text recognition
    pass
```

### 2. Add Model Dependencies
```bash
pip install torch torchvision ultralytics opencv-python
```

### 3. Frontend Image Processing
```javascript
// Add image preprocessing before upload
// Resize, normalize, format conversion
```

## 🎨 Customization

### Adding New Compliance Rules
1. Create rule in `backend/app/services/compliance_service.py`
2. Add frontend components in `frontend/src/components/`
3. Update dashboard to display new results

### Theme Customization
- Modify `frontend/tailwind.config.js` for colors
- Update theme context in `frontend/src/utils/ThemeContext.js`

## 🐛 Troubleshooting

### Backend Issues
- Ensure Python 3.8+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed

### Frontend Issues  
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall
- Check Node.js version compatibility

### CORS Issues
- Backend CORS is configured for localhost:3000
- Update origins in `backend/app/main.py` if needed

## 📝 License

MIT License - feel free to use this project for learning and development!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using React, FastAPI, and Tailwind CSS**
