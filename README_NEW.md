# Mythsnare - AI-Powered Fact-Checking Platform

## Overview

Mythsnare is an intelligent fact-checking web application that leverages advanced machine learning models to verify the authenticity of information. The platform uses BERT for classification, LLaMA for fact verification, and integrates real-time news feeds to provide comprehensive fact-checking capabilities.

## Features

### Core Functionality
- **Intelligent Classification**: Automatically classifies user input as either "Fact" or "News" using a fine-tuned BERT model
- **Fact Verification**: Uses LLaMA 3.1 (via Groq API) to verify factual claims with confidence scores
- **News Analysis**: Fetches and analyzes relevant news articles from Google News RSS feeds
- **Multi-Modal Input**: Supports text, voice recording, and file uploads (audio, video, documents)
- **Real-Time Processing**: Instant fact-checking with loading indicators and progress tracking

### Advanced Features
- **Named Entity Recognition (NER)**: Extracts entities using spaCy for better context understanding
- **Wikipedia Integration**: Fetches relevant Wikipedia summaries to enhance fact-checking accuracy
- **Retry Mechanism**: Automatically retries news fetching with multiple search strategies
- **Confidence Scoring**: Provides percentage-based confidence levels for all verifications
- **Chat Interface**: Modern, ChatGPT-style conversational UI for seamless user experience

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **Machine Learning**: 
  - BERT (transformers library) for text classification
  - LLaMA 3.1-8B (via Groq API) for fact verification
  - Whisper for audio transcription
  - spaCy for Named Entity Recognition
- **APIs**: Groq AI API for LLM access
- **Data Sources**: Google News RSS, Wikipedia API

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS for dynamic interactions
- **Bootstrap 5.3**: UI framework
- **Font Awesome 6.4**: Icon library

### Additional Technologies
- **Audio Processing**: pydub, SpeechRecognition
- **Web Scraping**: feedparser for RSS feeds
- **Real-Time**: Django Channels for WebSocket support
- **Database**: SQLite (development), PostgreSQL (production ready)

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Mythsnare
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Create a .env file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Collect static files:
```bash
python manage.py collectstatic --noinput
```

8. Start the development server:
```bash
python manage.py runserver
```

9. Access the application at: http://localhost:8000

## Docker Deployment

### Building the Docker Image
```bash
docker build -t mythsnare:latest .
```

### Running with Docker
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_api_key \
  -e SECRET_KEY=your_secret_key \
  mythsnare:latest
```

## Deploying to Render

### Step 1: Prepare Your Repository
1. Ensure all files are committed to your Git repository
2. Push to GitHub, GitLab, or Bitbucket

### Step 2: Create render.yaml (already included)
The project includes a `render.yaml` file for automated deployment configuration.

### Step 3: Deploy on Render
1. Log in to your Render account at https://render.com
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Render will automatically detect the Dockerfile
5. Configure environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `SECRET_KEY`: Django secret key
   - `DEBUG`: Set to False for production
   - `ALLOWED_HOSTS`: Your render domain

### Step 4: Deploy
- Click "Create Web Service"
- Render will build and deploy your application automatically
- Access your app at the provided Render URL

## Project Structure

```
Mythsnare/
├── transcribe/              # Main Django app
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template with navigation
│   │   ├── home.html       # Landing page
│   │   ├── transcription.html  # Fact-checking interface
│   │   ├── about.html      # About page
│   │   └── contact.html    # Contact form
│   ├── static/             # Static files (CSS, JS, images)
│   ├── views.py            # View functions and API endpoints
│   ├── models.py           # Database models
│   ├── urls.py             # URL routing
│   └── consumers.py        # WebSocket consumers
├── truthtell/              # Django project configuration
│   ├── settings.py         # Project settings
│   ├── urls.py             # Root URL configuration
│   ├── asgi.py             # ASGI configuration
│   └── wsgi.py             # WSGI configuration
├── trained_model/          # Pre-trained BERT model files
├── media/                  # User uploaded files
├── logs/                   # Application logs
├── db.sqlite3              # SQLite database (development)
├── manage.py               # Django management script
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
└── README.md               # This file
```

## API Endpoints

### POST /classify-text/
Classifies and verifies text input.

**Request Body:**
```json
{
  "message": "Your text to verify"
}
```

**Response:**
```json
{
  "prediction": "Fact" or "News",
  "is_true": true/false/null,
  "confidence": 0-100,
  "explanation": "Detailed explanation",
  "entities": [...]
}
```

### POST /detect/
Processes audio/video files and performs fact-checking.

**Request:** Multipart form data with file upload

**Response:** Same as /classify-text/

## Usage Guide

### Text Verification
1. Navigate to the main page
2. Type your claim or statement in the text area
3. Click "Send" or press Enter
4. Review the verification result with confidence score

### Voice Recording
1. Click the microphone icon
2. Speak your statement
3. Click stop when finished
4. The system will transcribe and verify automatically

### File Upload
1. Click the upload icon
2. Select file type (Audio/Video/Document)
3. Choose your file
4. Wait for processing and verification

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| GROQ_API_KEY | Groq API key for LLaMA access | Yes | None |
| SECRET_KEY | Django secret key | Yes | None |
| DEBUG | Enable debug mode | No | False |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | Yes | localhost |
| DATABASE_URL | PostgreSQL connection string | No | SQLite |

### Settings Customization

Edit `truthtell/settings.py` to customize:
- Database configuration
- Static files location
- Media files storage
- CORS settings
- Allowed hosts
- Security settings

## Model Information

### BERT Classifier
- **Purpose**: Classifies input as Fact or News
- **Location**: `./trained_model/`
- **Type**: Fine-tuned BERT-base-uncased
- **Input**: Text tokens (max 512)
- **Output**: Binary classification (0=Fact, 1=News)

### LLaMA 3.1
- **Provider**: Groq (llama-3.1-8b-instant)
- **Purpose**: Fact verification and explanation generation
- **Features**: High-speed inference, structured JSON output
- **Context**: Uses news articles and Wikipedia data

## Troubleshooting

### Common Issues

**Issue**: "GROQ_API_KEY not found"
- Solution: Add GROQ_API_KEY to your .env file or environment variables

**Issue**: spaCy model not found
- Solution: Run `python -m spacy download en_core_web_sm`

**Issue**: Audio transcription fails
- Solution: Ensure ffmpeg is installed on your system

**Issue**: No news articles found
- Solution: System automatically retries 3 times with different strategies

**Issue**: Static files not loading
- Solution: Run `python manage.py collectstatic --noinput`

### Logging

Application logs are stored in:
- Development: Console output
- Production: `logs/` directory
- Level: INFO (change in settings.py)

## Performance Optimization

### Caching
- Consider implementing Redis for session caching
- Cache Wikipedia summaries to reduce API calls
- Cache RSS feed results with TTL

### Database
- Use PostgreSQL for production
- Enable database connection pooling
- Index frequently queried fields

### Model Loading
- Models are lazy-loaded to reduce startup time
- Whisper model loads only when needed

## Security Considerations

- CSRF protection enabled by default
- CORS headers configured for API access
- User input sanitization implemented
- File upload validation and size limits
- Environment variables for sensitive data
- HTTPS recommended for production

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Test thoroughly
5. Submit a pull request with description

## Known Limitations

- Audio transcription requires stable internet connection
- Large video files may take time to process
- News verification depends on Google News RSS availability
- Groq API rate limits may apply
- spaCy NER may not recognize all entity types

## Future Enhancements

- Multi-language support
- User authentication and history tracking
- Advanced analytics dashboard
- Browser extension for in-context fact-checking
- Mobile application
- API rate limiting and caching
- Blockchain verification for immutable fact records
- Social media integration
- Real-time collaboration features

## License

This project is provided as-is for educational and research purposes.

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact through the application's contact form
- Check documentation and troubleshooting guide

## Acknowledgments

- BERT model from Hugging Face Transformers
- LLaMA 3.1 via Groq API
- spaCy for NER capabilities
- OpenAI Whisper for speech recognition
- Google News RSS for news data
- Wikipedia API for knowledge base
- Django community for excellent framework

## Version History

### Version 1.0.0
- Initial release with core fact-checking features
- BERT classification
- LLaMA verification
- Multi-modal input support
- Chat interface
- News article fetching with retry mechanism

---

Built with Django, BERT, and LLaMA for accurate information verification.
