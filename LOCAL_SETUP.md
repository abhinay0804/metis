# Local Development Setup

This guide will help you run the Optiv Masking application locally.

## Prerequisites

1. Python 3.8+ installed
2. Node.js 16+ installed
3. All dependencies installed (see requirements.txt)

## Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python run_server.py
```

The backend will be available at:
- API: http://localhost:8001
- Documentation: http://localhost:8001/docs

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd optiv-metis-ui/optiv-metis-data-craft-main
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at:
- Application: http://localhost:5173

## Testing the Application

1. Open your browser and go to http://localhost:5173
2. Upload a file using the file upload component
3. Click "Mask Data" or "Reversible Masking" to process the file
4. Check the "Processing History" tab to see the masked data

## Features

### Working Features
- ✅ File upload and processing
- ✅ Sensitive data masking (reversible and irreversible)
- ✅ Processing history with immediate updates
- ✅ Masked data preview and download
- ✅ Local storage for development

### Disabled Features
- ❌ Analysis functionality (coming soon)
- ❌ Authentication (bypassed for local development)

## Troubleshooting

### Backend Issues
- Make sure port 8001 is not in use
- Check that all Python dependencies are installed
- Verify the dev bypass is enabled (ALLOW_DEV_BYPASS=1)

### Frontend Issues
- Make sure port 5173 is not in use
- Check that Node.js dependencies are installed
- Verify the API URL is set to http://localhost:8001

### File Processing Issues
- Ensure the file type is supported (PDF, PPTX, XLSX, images)
- Check that the file is not corrupted
- Verify the backend server is running

## File Types Supported

- PDF files (.pdf)
- PowerPoint presentations (.pptx)
- Excel spreadsheets (.xlsx, .xls)
- Images (.jpg, .png, .gif, etc.)
- Text files (.txt)
- Word documents (.docx)
- CSV files (.csv)

## API Endpoints

- `GET /health` - Health check
- `POST /process` - Process and mask a file
- `GET /maskings` - List all masking operations
- `GET /maskings/{id}` - Get specific masked data
- `GET /maskings/{id}/original` - Get original data (reversible only)

## Development Notes

- The application uses local storage for development
- Authentication is bypassed for local testing
- All masked data is stored in the `data/masked/` directory
- Original data (for reversible masking) is encrypted and stored locally
