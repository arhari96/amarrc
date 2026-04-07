# Amarrc Project - Comprehensive Documentation

## Project Overview
Amarrc is a Django-based web application for managing Registration Certificate (RC) data for vehicles, featuring image generation capabilities for both new and old RC formats. The system integrates with balance management for transaction processing and provides API endpoints for frontend consumption.

## Project Structure
```
amarrc/
├── amarrc/                 # Main Django project settings
├── balance/                # Balance management app
├── smartrc/                # Smart RC (registration certificate) app
├── flutter_web_app/        # Flutter frontend
├── webfrontend/            # React frontend
├── media/                  # Uploaded media files
├── static/                 # Static assets
├── templates/              # HTML templates
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
└── CLAUDE.md               # This file
```

## Core Components

### 1. Balance App (`balance/`)
- **Models**: Tracks financial transactions with recharge/debit amounts
- **Views**: Provides balance listing and calculation APIs
- **Functionality**: Manages financial operations for RC creation

### 2. SmartRC App (`smartrc/`)
- **Models**: 
  - `NewRc`: For new registration certificates
  - `OldRc`: For old registration certificates  
  - `Rc`: JSON-based storage for external API data
- **Views**: 
  - API endpoints for RC creation, search, deletion
  - Image generation for RC certificates
  - External API integration for vehicle details
- **Serializers**: DRF serializers for model data

### 3. Main Project (`amarrc/`)
- **Settings**: Django configuration including database, CORS, static files
- **URLs**: API endpoint routing
- **WSGI/ASGI**: Application entry points

## Key Features

### RC Image Generation
- Automatically generates front/back images for NewRc and OldRc models
- Uses PIL/Pillow for text drawing and image manipulation
- Integrates QR code generation for verification
- Saves generated images to media directories

### Balance Management
- Tracks financial transactions with automatic date ordering
- Provides debit functionality for RC creation fees
- Calculates total balances for API responses

### API Endpoints
- `/api/test/` - Test endpoint
- `/api/new_create_rc/` - Create new RC
- `/api/old_create_rc/` - Create old RC  
- `/api/search_rc/` - Search RCs by registration number
- `/api/delete_rc/` - Delete RC by registration number
- `/api/balance_list/` - Get balance list with totals
- `/api/reg_detail/` - Get vehicle registration details
- `/api/save_rc_details/` - Save/update external RC data

## Setup Instructions

### Prerequisites
- Python 3.13+
- MySQL database
- Pip package manager
- Node.js (for frontend)
- Flutter SDK (for mobile app)

### Backend Setup
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure database in `amarrc/settings.py`:
   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.mysql",
           "NAME": "your_database_name",
           "HOST": "your_host",
           "USER": "your_username", 
           "PASSWORD": "your_password",
           "PORT": 3306,
       }
   }
   ```
6. Run migrations: `python manage.py makemigrations` then `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Collect static files: `python manage.py collectstatic`
9. Start development server: `python manage.py runserver`

### Environment Variables
For production, consider moving sensitive data to environment variables:
- `SECRET_KEY`
- Database credentials
- API keys for external services

## Development Guidelines

### Coding Standards
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Keep functions focused on single responsibilities
- Add docstrings for complex functions
- Use type hints where beneficial

### Django Best Practices
- Keep business logic in models, not views
- Use Django's ORM efficiently (avoid N+1 queries)
- Leverage Django signals for decoupled operations
- Use class-based views for reusable logic
- Implement proper error handling and validation

### Image Generation
- The image generation logic is embedded in model `save()` methods
- Consider extracting to service layer for better testability
- Ensure required font files exist in `fonts/` directory
- Base templates (`front.png`, `back.png`) must exist in media root

### Security Considerations
- Never commit sensitive credentials to version control
- Use environment variables for production secrets
- Keep `DEBUG=False` in production
- Restrict `ALLOWED_HOSTS` to specific domains
- Implement proper CSRF protection
- Validate and sanitize all user inputs
- Use Django's built-in authentication and permissions

### Database Optimization
- Add indexes on frequently queried fields
- Use `select_related()` and `prefetch_related()` for related objects
- Consider database connection pooling for high traffic
- Regularly analyze slow queries
- Implement proper backup strategies

## API Design Principles

### Response Formats
- Success responses should follow consistent structure
- Error responses should include appropriate HTTP status codes
- Use DRF's standard error formatting where possible
- Include meaningful error messages for debugging

### Endpoint Organization
- Group related endpoints under common prefixes
- Use HTTP methods appropriately (GET for retrieval, POST for creation, etc.)
- Implement proper authentication for sensitive endpoints
- Consider API versioning for future changes

### Performance
- Implement pagination for list endpoints
- Use caching for frequently accessed data
- Consider asynchronous processing for heavy operations
- Optimize database queries with proper indexing

## Deployment Considerations

### Production Settings
- Set `DEBUG = False`
- Configure proper `ALLOWED_HOSTS`
- Use secure database connection settings
- Configure static/media file serving via CDN or web server
- Set up proper logging
- Enable HTTPS

### Scaling
- Consider using gunicorn/uWSGI with multiple workers
- Implement database read replicas if needed
- Use caching layers (Redis/Memcached)
- Consider horizontal scaling with load balancers
- Monitor application performance and database metrics

## Testing Strategy

### Unit Tests
- Test model methods and properties
- Test view logic and API responses
- Test form validation and cleaning
- Test utility functions and helpers

### Integration Tests
- Test API endpoint workflows
- Test database transactions
- Test image generation processes
- Test external API integrations

### Test Coverage
- Aim for high coverage on critical paths
- Test edge cases and error conditions
- Use Django's test framework or pytest
- Implement continuous integration for test runs

## Common Issues and Troubleshooting

### Image Generation Failures
- Missing font files in `fonts/` directory
- Missing base template images (`front.png`, `back.png`)
- Insufficient permissions for media directory writes
- Corrupted image files

### Database Connection Issues
- Incorrect database credentials in settings
- MySQL server not running or inaccessible
- Network connectivity problems
- Insufficient user permissions

### API Errors
- Missing required fields in request data
- Invalid data types or formats
- Authentication/authorization failures
- Rate limiting or throttling

### Performance Problems
- Unoptimized database queries
- Large media files causing slow uploads/downloads
- Insufficient server resources
- Lack of caching for expensive operations

## Future Enhancements

### Technical Improvements
- Extract image generation to service layer
- Implement proper background task processing (Celery)
- Add comprehensive test suite
- Implement API documentation (Swagger/OpenAPI)
- Add rate limiting and throttling
- Implement proper logging and monitoring
- Add caching layer for performance improvement
- Containerize application with Docker
- Implement CI/CD pipeline

### Feature Enhancements
- Add user authentication and authorization
- Implement role-based access control
- Add audit trail for RC modifications
- Implement file validation for uploads
- Add bulk import/export capabilities
- Implement search/filter enhancements
- Add reporting and analytics features
- Improve mobile responsiveness
- Add multi-language support

## Maintenance Tasks

### Regular Maintenance
- Backup database regularly
- Monitor disk usage for media files
- Clean up temporary files
- Update dependencies periodically
- Review and optimize slow queries
- Check for security updates
- Monitor application logs

### Periodic Reviews
- Review code for technical debt
- Update documentation as features change
- Refactor duplicated code
- Review and update dependencies
- Assess performance and scalability needs
- Plan for future feature development

## Contact Information
For questions or issues regarding this project, please refer to the project repository or contact the development team.

---
*Documentation generated: 2026-04-01*