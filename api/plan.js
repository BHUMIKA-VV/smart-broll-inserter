// Vercel serverless function to proxy /api/plan requests with file uploads
// This shows logs in Vercel

export const config = {
  api: {
    bodyParser: false, // Disable body parsing, we'll handle raw body for file uploads
  },
};

export default async function handler(req, res) {
  const backendUrl = process.env.REACT_APP_API_URL || 'https://smart-broll-inserter-backend.onrender.com';
  const targetUrl = `${backendUrl}/api/plan`;
  
  console.log(`[API Proxy] ${req.method} ${targetUrl}`);
  console.log(`[API Proxy] Headers:`, JSON.stringify(req.headers, null, 2));
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    // For file uploads, we need to stream the request body
    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        // Forward Content-Type with boundary for multipart/form-data
        'Content-Type': req.headers['content-type'] || 'multipart/form-data',
      },
      body: req, // Stream the request body directly
    });
    
    const data = await response.json();
    
    console.log(`[API Proxy] Response status: ${response.status}`);
    console.log(`[API Proxy] Response data keys:`, Object.keys(data));
    
    // Forward the response
    res.status(response.status).json(data);
  } catch (error) {
    console.error('[API Proxy] Error:', error);
    res.status(500).json({ 
      error: 'Proxy error', 
      message: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}
