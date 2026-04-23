# Lesson Plan Generator

## Overview

The Lesson Plan Generator is an AI-powered web application that creates comprehensive lesson plans for any topic. It uses FastAPI for the backend API and a vanilla HTML/CSS/JavaScript frontend with Tailwind CSS for styling. The application leverages the Hugging Face API (specifically deepseek R1:novita model) to generate educational content including lesson plans and exam questions based on user-provided topics and optional grade levels.

**Features:**
- User-friendly web interface with topic and grade level input
- AI-powered lesson plan generation with automatic exam questions
- RESTful API endpoint for external system integration
- Comprehensive error handling and input validation
- Security measures including XSS prevention and input sanitization
- Interactive API documentation at /docs
- Real-time loading states and user feedback

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: Vanilla JavaScript with Tailwind CSS for styling
- **Design Pattern**: Single-page application (SPA) with form-based interaction
- **Security**: Uses DOMPurify library for sanitizing AI-generated content before rendering to prevent XSS attacks
- **User Experience**: Simple form interface with topic input (required) and grade level input (optional)

### Backend Architecture
- **Framework**: FastAPI (Python web framework)
- **API Design**: RESTful API with JSON request/response format
- **Request Validation**: Uses Pydantic models for input validation with constraints (topic max length: 500 characters)
- **Error Handling**: HTTP exceptions for missing configuration and API errors
- **CORS**: Configured to allow all origins for flexible frontend deployment
- **Static File Serving**: Serves frontend HTML directly from the `/static` directory

### AI Integration
- **LLM Provider**: Hugging Face Router API
- **Model**: Meta Llama 3.1 8B Instruct (via Fireworks AI)
- **API Client**: OpenAI-compatible client library configured for Hugging Face endpoints
- **Prompt Engineering**: Dynamic prompts that incorporate topic and optional grade level, automatically requesting exam questions

### Authentication & Configuration
- **API Security**: Requires HF_TOKEN environment variable for Hugging Face API authentication
- **Configuration Validation**: Server checks for required environment variables at runtime and returns clear error messages if missing

## External Dependencies

### Third-Party APIs
- **Hugging Face Router API**: Primary AI service for generating lesson plans
  - Endpoint: `https://router.huggingface.co/v1`
  - Authentication: Token-based (HF_TOKEN environment variable)
  - Model: `deepseek-ai/DeepSeek-R1:novita`

### Python Libraries
- **FastAPI**: Web framework for building the API
- **OpenAI**: Client library (configured for Hugging Face compatibility)
- **Pydantic**: Data validation and settings management
- **CORS Middleware**: Cross-origin resource sharing support

### Frontend Libraries (CDN)
- **Tailwind CSS**: Utility-first CSS framework for styling
- **DOMPurify**: XSS sanitization library for safe HTML rendering

### Environment Variables
- **HF_TOKEN** (required): Hugging Face API authentication token
