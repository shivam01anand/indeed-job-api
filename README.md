# Indeed Job Extractor API

A FastAPI-based service that extracts job descriptions from Indeed using Selenium with stealth mode.

## 🚀 Deployment Options

### Option 1: Vercel (Recommended for your setup)

1. **Setup your domain:**
   ```bash
   # In the api/ directory
   vercel --prod
   ```

2. **Add your custom domain in Vercel dashboard:**
   - Go to your project settings
   - Add your custom domain (e.g., `jobs-api.yourdomain.com`)

### Option 2: Docker Deployment

1. **Build and run locally:**
   ```bash
   cd api/
   docker build -t indeed-api .
   docker run -p 8000:8000 indeed-api
   ```

2. **Deploy to any cloud provider that supports Docker**

### Option 3: Railway/Render/DigitalOcean

Simple deploy with their GitHub integration.

## 📡 API Endpoints

### `POST /extract`
Extract job description from Indeed URL.

**Request:**
```json
{
  "url": "https://www.indeed.com/viewjob?jk=abc123&hl=en",
  "headless": true
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "abc123",
  "description": "Full job description text...",
  "processing_time": 5.2
}
```

### `GET /health`
Health check endpoint.

### `GET /`
API information and available endpoints.

## 🛠️ Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/extract" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.indeed.com/viewjob?jk=c270616d070352c7&hl=en"}'
   ```

## 🔧 Client Usage (TypeScript)

```typescript
import IndeedExtractor from './client_extractor';

const extractor = new IndeedExtractor('https://jobs-api.yourdomain.com');

// Extract from URL
const result = await extractor.extractFromUrl(
  'https://www.indeed.com/viewjob?jk=abc123&hl=en'
);

console.log(result.description);
```

## 🚦 Performance

- **Cold start:** ~10-15 seconds (browser initialization)
- **Warm requests:** ~3-5 seconds per extraction
- **Browser reuse:** Single browser instance for efficiency
- **Concurrent requests:** Supported (queued processing)

## 🔒 Security Considerations

1. **Rate limiting:** Consider adding rate limits in production
2. **Authentication:** Add API keys if needed
3. **CORS:** Configure origins based on your client domains
4. **Resource limits:** Set memory/CPU limits for containerized deployments

## 📊 Monitoring

- Health check endpoint: `GET /health`
- Processing time included in all responses
- Built-in error handling and logging

## 💡 Why This Approach?

✅ **Separation of concerns:** Heavy scraping logic isolated from your main app  
✅ **Language flexibility:** Python for scraping, TypeScript for your app  
✅ **Scalability:** Can handle multiple concurrent requests  
✅ **Reliability:** Selenium with stealth mode bypasses Indeed's blocks  
✅ **Maintainability:** Single API to update when Indeed changes structure  
✅ **Cost-effective:** Use your existing Vercel Pro plan
