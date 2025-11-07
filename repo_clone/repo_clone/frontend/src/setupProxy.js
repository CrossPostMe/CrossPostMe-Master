const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests to backend server
  app.use(
    '/api',
    createProxyMiddleware({
      target: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      onProxyReq: (proxyReq) => {
        // Log proxy requests in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[Proxy] ${proxyReq.method} ${proxyReq.path}`);
        }
      },
      onError: (err, req, res) => {
        console.error('[Proxy Error]', err);
        res.status(500).json({
          error: 'Proxy Error',
          message: 'Failed to connect to backend server. Is it running on ' + 
                   (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000') + '?'
        });
      }
    })
  );
};
