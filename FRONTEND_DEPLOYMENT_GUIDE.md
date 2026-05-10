# Frontend Deployment Guide - Vercel

## Overview
Your AI Policy Assistant frontend is now ready for deployment on Vercel. The frontend consists of a modern web application that communicates with your Render-deployed backend.

## Files Created
- `index.html` - Main HTML structure with chat interface
- `styles.css` - Mahindra-branded styling with responsive design
- `script.js` - JavaScript for API calls and chat functionality
- `vercel.json` - Vercel deployment configuration
- `README.md` - Documentation for the frontend

## Deployment Steps

### Step 1: Prepare Your Repository
1. Create a new GitHub repository for the frontend
2. Copy the `frontend-vercel` folder contents to the repository
3. Commit and push the files

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration
5. Click "Deploy"

### Step 3: Configure Environment (Optional)
If you need environment variables, add them in Vercel dashboard:
- No environment variables needed for basic functionality
- API URL is hardcoded in `script.js`

## Testing the Deployment

### Local Testing
The frontend is currently running locally at: http://localhost:8000

### API Connection
- Backend URL: `https://company-project-f3ae.onrender.com/api/v1`
- Endpoint: `POST /api/v1/policy/query`
- The frontend will call this endpoint for policy queries

## Features Included

### UI Components
- ✅ Mahindra-branded header with logo
- ✅ Chat interface with message bubbles
- ✅ Loading indicators
- ✅ Responsive design for mobile/desktop
- ✅ Policy categories sidebar
- ✅ Quick question tags

### Functionality
- ✅ Real-time chat with backend API
- ✅ Error handling for API failures
- ✅ Auto-scrolling chat messages
- ✅ Keyboard shortcuts (Enter to send)

## Customization Options

### Change Backend URL
Edit `script.js` line 2:
```javascript
const API_BASE_URL = 'YOUR_NEW_BACKEND_URL/api/v1';
```

### Modify Branding
Edit CSS custom properties in `styles.css`:
```css
:root {
  --mahindra-red: #YOUR_COLOR;
  --mahindra-gray: #YOUR_COLOR;
  /* ... */
}
```

### Add New Features
- Extend the sidebar with more policy categories
- Add file upload functionality
- Implement user authentication
- Add chat history persistence

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if backend is running on Render
   - Verify the API_BASE_URL in script.js
   - Check browser console for CORS errors

2. **Styling Issues**
   - Clear browser cache
   - Check CSS file is loading correctly
   - Verify Font Awesome CDN is accessible

3. **Deployment Issues**
   - Ensure all files are committed to GitHub
   - Check Vercel build logs for errors
   - Verify vercel.json configuration

### Browser Compatibility
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## Next Steps

1. **Deploy the frontend** using the steps above
2. **Test the full application** by asking policy questions
3. **Customize the UI** to match your exact requirements
4. **Add analytics** if needed for usage tracking

## Support

If you encounter issues:
1. Check the browser developer console for errors
2. Verify backend API is responding correctly
3. Review Vercel deployment logs
4. Check network tab for failed API calls

Your AI Policy Assistant is now ready for production use! 🚀