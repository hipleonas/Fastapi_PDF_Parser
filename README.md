# FastAPI PDF Parser

A modern FastAPI application for parsing PDF documents using Docling. This service converts PDF files to structured markdown format and returns organized JSON data.

## 🚀 Features

- **PDF to Markdown Conversion**: Utilizes Docling for high-quality PDF parsing
- **RESTful API**: Clean FastAPI implementation with automatic documentation
- **Bearer Token Authentication**: Secure API access with configurable tokens
- **File Validation**: Comprehensive file type and size validation
- **Error Handling**: Robust error handling with detailed error responses
- **CORS Support**: Configurable CORS for cross-origin requests
- **Health Checks**: Built-in health monitoring endpoints
- **Docker Support**: Ready for containerized deployment

## 📋 Prerequisites

- Python 3.9+
- Virtual environment (recommended)

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Fastapi_PDF_Parser
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration (Optional)

Create a `.env` file in the project root:

```env
BEARER_TOKEN=your_secure_token_here
```

If no `.env` file is provided, the application defaults to using "test" as the bearer token.

## 🏃‍♂️ Running the Application

### Development Mode (with auto-reload)

```bash
# Method 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Running the main.py file
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📖 API Documentation

Once the application is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

### Health Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### PDF Processing

- `POST /upload-pdf/` - Upload and parse PDF documents

#### Request Example

```bash
curl -X POST "http://localhost:8000/upload-pdf/" \
     -H "Authorization: Bearer test" \
     -F "file=@your_document.pdf"
```

#### Response Example

```json
{
  "title": "document.pdf",
  "paragraphs": [
    {
      "id": 1,
      "text": "This is the first paragraph content."
    },
    {
      "id": 2,
      "text": "This is the second paragraph content."
    }
  ],
  "total_paragraphs": 2,
  "file_size_bytes": 1024000
}
```

## 🧪 Testing

### Using the Test Script

```bash
# Make the test script executable
chmod +x test_curl.sh

# Run the test
./test_curl.sh
```

### Manual Testing

The test script will:

1. Create a sample PDF using ReportLab
2. Send a POST request to the API
3. Display the parsed response
4. Clean up temporary files

## 🐳 Docker Deployment

Build and run using Docker:

```bash
# Build the image
docker build -t fastapi-pdf-parser .

# Run the container
docker run -p 8000:8000 -e BEARER_TOKEN=your_token fastapi-pdf-parser
```

## 📁 Project Structure

```
Fastapi_PDF_Parser/
├── main.py              # Main FastAPI application
├── docling_doc.py       # Docling documentation/examples
├── fastapi_doc.py       # FastAPI learning notes
├── requirements.txt     # Python dependencies
├── test_curl.sh         # Test script
├── Dockerfile           # Docker configuration
├── .env                 # Environment variables (create manually)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔒 Security Features

- **Bearer Token Authentication**: Configurable token-based security
- **File Validation**: Type and size restrictions
- **Temporary File Cleanup**: Automatic cleanup of processed files
- **Error Handling**: Secure error responses without sensitive data exposure

## ⚙️ Configuration

### Environment Variables

| Variable       | Description                         | Default |
| -------------- | ----------------------------------- | ------- |
| `BEARER_TOKEN` | Authentication token for API access | `test`  |

### Application Limits

- **Max File Size**: 50MB
- **Allowed Extensions**: `.pdf`
- **Temporary File Cleanup**: Automatic

## 🚨 Error Handling

The API provides detailed error responses for various scenarios:

- **401 Unauthorized**: Invalid or missing authentication token
- **400 Bad Request**: Invalid file type or format
- **413 Request Entity Too Large**: File size exceeds limit
- **500 Internal Server Error**: Processing errors

## 📚 Example Use Cases

- **Document Processing**: Convert PDF documents to structured data
- **Content Extraction**: Extract text content from PDFs for analysis
- **API Integration**: Integrate PDF parsing into larger applications
- **Batch Processing**: Process multiple PDFs through the API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Useful Links

- **Docling Documentation**: [Docling GitHub](https://github.com/DS4SD/docling)
- **FastAPI Documentation**: [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- **Uvicorn Documentation**: [Uvicorn Official Docs](https://www.uvicorn.org/)

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
2. **Permission Errors**: Check file permissions for uploaded PDFs
3. **Memory Issues**: Large PDFs may require more memory allocation
4. **Port Conflicts**: Change the port if 8000 is already in use

### Debug Mode

Run with debug logging:

```bash
uvicorn main:app --reload --log-level debug
```

---

For questions or support, please open an issue in the repository.
