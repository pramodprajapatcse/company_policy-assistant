# Mahindra Rise - AI Policy Assistant Frontend

A modern, responsive web frontend for the AI Policy Assistant, built for Vercel deployment.

## Features

- 🎨 Modern UI with Mahindra brand colors
- 💬 Real-time chat interface
- 📱 Responsive design for all devices
- ⚡ Fast API integration with backend
- 🏢 Policy category sidebar
- 💡 Quick question tags

## Tech Stack

- HTML5
- CSS3 (Custom properties, Flexbox, Grid)
- Vanilla JavaScript (ES6+)
- Font Awesome icons
- Vercel for deployment

## Project Structure

```
frontend-vercel/
├── index.html          # Main HTML file
├── styles.css          # CSS styles with Mahindra branding
├── script.js           # JavaScript for API calls and chat
└── vercel.json         # Vercel deployment configuration
```

## Deployment to Vercel

### Option 1: GitHub Integration (Recommended)

1. Push this code to a GitHub repository
2. Connect your GitHub account to Vercel
3. Import the `frontend-vercel` folder as a new project
4. Vercel will automatically detect the configuration and deploy

### Option 2: Manual Deployment

1. Install Vercel CLI: `npm install -g vercel`
2. Navigate to the frontend-vercel directory
3. Run: `vercel --prod`
4. Follow the prompts to create your project

## Configuration

### Backend API URL

Update the `API_BASE_URL` in `script.js` to point to your deployed backend:

```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com/api/v1';
```

## API Integration

The frontend calls the following backend endpoint:

```
POST /api/v1/policy/query
Content-Type: application/json

{
  "question": "user question",
  "top_k": 5
}
```

## Development

To run locally for development:

1. Open `index.html` in a web browser
2. The app will work with the configured backend API
3. For local backend testing, you may need to handle CORS

## Browser Support

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## Customization

### Colors

The app uses CSS custom properties for easy theming:

```css
:root {
  --mahindra-red: #D71920;
  --mahindra-dark-red: #A5151C;
  --mahindra-gray: #4A4A4A;
  /* ... */
}
```

### API Configuration

Modify the API calls in `script.js` to match your backend endpoints and data format.

## Troubleshooting

### CORS Issues

If you encounter CORS errors during development:

1. Ensure your backend allows requests from your frontend domain
2. For local development, you may need to configure CORS headers
3. Check that the API_BASE_URL is correct

### API Connection

- Verify the backend is running and accessible
- Check network tab in browser dev tools for failed requests
- Ensure the API endpoint paths match your backend implementation

## License

This project is part of the Mahindra Rise AI Policy Assistant system.