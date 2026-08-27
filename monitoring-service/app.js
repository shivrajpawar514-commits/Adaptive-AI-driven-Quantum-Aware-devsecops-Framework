const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const logger = require('./src/config/logger');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./src/config/swagger');
const metricsRoutes = require('./src/routes/metrics.routes');

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

// Response Standardization Middleware
app.use((req, res, next) => {
  const startTime = Date.now();
  const requestId = req.headers['x-request-id'] || req.headers['x-correlation-id'] || `REQ-MON-${Date.now()}`;
  
  const originalJson = res.json;
  
  res.json = function(data) {
    const executionTime = `${Date.now() - startTime}ms`;
    
    // Skip formatting for prometheus metrics text endpoint
    if (req.url === '/metrics' && typeof data === 'string') {
      return originalJson.call(this, data);
    }
    
    if (data && data.service && data.status) {
      return originalJson.call(this, data);
    }
    
    const isError = res.statusCode >= 400;
    const standardized = {
      status: isError ? 'error' : 'success',
      timestamp: new Date().toISOString(),
      request_id: requestId,
      service: 'Monitoring Service API',
      version: '1.0.0',
      execution_time: executionTime,
      data: isError ? null : data,
      errors: isError ? (data.message || data.error || data) : null
    };
    
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      for (const [key, value] of Object.entries(data)) {
        if (!(key in standardized) || key === 'data') {
          standardized[key] = value;
        }
      }
    }
    
    return originalJson.call(this, standardized);
  };
  
  next();
});

app.use(morgan('dev', {
  stream: {
    write: (message) => logger.info(message.trim())
  }
}));

// Swagger documentation
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Health Check route
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', version: '1.0.0' });
});

// Mount Metrics endpoints
app.use('/', metricsRoutes);

// Error middleware
app.use((err, req, res, next) => {
  logger.error(`Error: ${err.message}`, { stack: err.stack });
  res.status(err.statusCode || 500).json({
    status: 'error',
    message: err.message || 'Internal Server Error'
  });
});

module.exports = app;
