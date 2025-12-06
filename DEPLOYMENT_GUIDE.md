# Agentic HR Assistant - Setup Guide

## Prerequisites

1. **Python 3.11+**
2. **Docker & Docker Compose**
3. **Anthropic API Key** (sign up at https://anthropic.com)

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd "c:\Users\LENOVO\OneDrive\Documents\Python\Agentic HR Assistant"

# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings:
# - Set ANTHROPIC_API_KEY
# - Set secure SECRET_KEY and ENCRYPTION_KEY (32+ characters each)
# - Configure database passwords
```

### 2. Start Services with Docker

```bash
# Start all services (PostgreSQL, MinIO, Redis, API, Workers)
docker-compose up -d

# Check service health
docker-compose ps
```

### 3. Run Database Migrations

```bash
# Install Python dependencies locally (for migration tools)
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin interface)
- **API Health Check**: http://localhost:8000/health

## Development Setup (Without Docker)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Start External Services

```bash
# Start only external services
docker-compose up -d postgres minio redis
```

### 3. Run the Application

```bash
# Set environment variables (use .env file)
# Run migrations
alembic upgrade head

# Start the API server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Start background worker (in another terminal)
celery -A src.workers.celery_app worker --loglevel=info
```

## Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL=postgresql://hr_admin:your_secure_password@localhost:5432/hr_assistant_db

# MinIO Object Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=your_minio_password

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security (Generate secure 32+ character keys)
SECRET_KEY=your_very_secure_secret_key_here_32_chars_min
ENCRYPTION_KEY=your_encryption_key_here_32_chars_minimum

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Security Notes

1. **Never commit `.env` files** - use `.env.example` as template
2. **Use strong passwords** for database and MinIO
3. **Generate unique keys** for SECRET_KEY and ENCRYPTION_KEY
4. **Enable HTTPS** in production environments

## API Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Create Candidate with Resume

```bash
curl -X POST "http://localhost:8000/api/v1/candidates/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "full_name=John Doe" \
  -F "email=john.doe@example.com" \
  -F "phone=+1234567890" \
  -F "experience_years=5" \
  -F "current_position=Software Engineer" \
  -F "resume_file=@/path/to/resume.pdf"
```

### 3. List Candidates

```bash
curl -X GET "http://localhost:8000/api/v1/candidates/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Data Protection & GDPR Compliance

### Built-in Features

1. **PII Encryption**: All personally identifiable information encrypted at rest
2. **Consent Management**: Granular consent tracking for different data processing types
3. **Data Retention**: Automatic data retention policy enforcement
4. **Right to Erasure**: Complete data deletion capabilities
5. **Data Portability**: Export candidate data in structured format
6. **Audit Logging**: Complete audit trail for compliance

### GDPR Operations

```bash
# Export candidate data (GDPR Article 20)
curl -X GET "http://localhost:8000/api/v1/candidates/{candidate_id}/export" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Delete candidate data (GDPR Article 17)
curl -X DELETE "http://localhost:8000/api/v1/candidates/{candidate_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Monitoring & Logs

### Application Logs

```bash
# View API logs
docker-compose logs -f hr_api

# View worker logs
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db

# View candidate data (encrypted)
SELECT id, experience_years, current_position FROM hr_core.candidates;
```

### MinIO Access

- Console: http://localhost:9001
- Username: minioadmin (or your MINIO_ACCESS_KEY)
- Password: your_minio_password (or your MINIO_SECRET_KEY)

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check if PostgreSQL is running: `docker-compose ps`
   - Verify DATABASE_URL in `.env`

2. **MinIO Connection Error**
   - Check MinIO service: `docker-compose logs minio`
   - Verify MinIO credentials in `.env`

3. **Anthropic API Errors**
   - Verify ANTHROPIC_API_KEY is valid
   - Check API quotas and rate limits

4. **Permission Denied Errors**
   - Ensure user has proper role assignments
   - Check JWT token validity

### Performance Tuning

1. **Database Performance**
   - Increase `DATABASE_POOL_SIZE` for high load
   - Add database indexes for frequently queried fields

2. **Claude API Optimization**
   - Adjust `CLAUDE_RATE_LIMIT_RPM` based on your plan
   - Use batch processing for multiple resumes

3. **File Storage**
   - Configure MinIO with proper storage backend
   - Set up CDN for file delivery in production

## Production Deployment

### Security Checklist

- [ ] Use HTTPS/TLS certificates
- [ ] Set secure passwords for all services
- [ ] Enable database SSL connections
- [ ] Configure firewall rules
- [ ] Set up proper backup procedures
- [ ] Enable audit logging
- [ ] Configure monitoring and alerting

### Infrastructure Requirements

- **Minimum**: 4 CPU cores, 8GB RAM, 100GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 500GB SSD storage
- **Database**: PostgreSQL 15+ with SSL
- **Object Storage**: MinIO or AWS S3
- **Cache**: Redis 7+

### Scaling Considerations

1. **Horizontal Scaling**: Add multiple API and worker containers
2. **Database Scaling**: Use read replicas for heavy read workloads
3. **File Storage**: Use distributed MinIO cluster or cloud storage
4. **Load Balancing**: Add nginx or cloud load balancer

## Support

For issues and questions:
1. Check the logs for error details
2. Review the API documentation at `/docs`
3. Verify environment configuration
4. Check service health endpoints

## License

MIT License - see LICENSE file for details.