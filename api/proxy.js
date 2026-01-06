// Vercel serverless function to proxy API requests to Render backend
// This allows us to see logs in Vercel

export default async function handler(req, res) {
  // Get the API path from query parameter
  const path = req.query.path || '';
  const backendUrl = process.env.REACT_APP_API_URL || 'https://smart-broll-inserter-backend.onrender.com';
  
  // Construct the full backend URL
  const targetUrl = `${backendUrl}/api/${path}`;
  
  // Log the request (this will show in Vercel logs)
  console.log(`[API Proxy] ${req.method} ${targetUrl}`);
  console.log(`[API Proxy] Headers:`, req.headers);
  
  try {
    // Forward the request to the backend
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': req.headers['content-type'] || 'application/json',
        // Forward other headers if needed
        ...(req.headers.authorization && { Authorization: req.headers.authorization }),
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined,
    });
    
    const data = await response.text();
    
    // Log the response
    console.log(`[API Proxy] Response status: ${response.status}`);
    
    // Forward the response
    res.status(response.status).json(JSON.parse(data));
  } catch (error) {
    console.error('[API Proxy] Error:', error);
    res.status(500).json({ error: 'Proxy error', message: error.message });
  }
}
