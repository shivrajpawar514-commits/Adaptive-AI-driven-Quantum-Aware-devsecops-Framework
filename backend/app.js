const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const logger = require('./src/config/logger');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./src/config/swagger');
const routes = require('./src/routes');
const errorMiddleware = require('./src/middlewares/error.middleware');
const rateLimiter = require('./src/middlewares/rateLimiter.middleware');
const pipelineRoutes = require('./src/routes/pipeline.routes');

const app = express();

// Security Middlewares
app.use(helmet());
app.use(cors({ origin: '*' }));
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Response Standardization Middleware
app.use((req, res, next) => {
  const startTime = Date.now();
  const requestId = req.headers['x-request-id'] || req.headers['x-correlation-id'] || `REQ-GATE-${Date.now()}`;
  
  const originalJson = res.json;
  
  res.json = function(data) {
    const executionTime = `${Date.now() - startTime}ms`;
    
    if (data && data.service && data.status) {
      return originalJson.call(this, data);
    }
    
    const isError = res.statusCode >= 400;
    const standardized = {
      status: isError ? 'error' : 'success',
      timestamp: new Date().toISOString(),
      request_id: requestId,
      service: 'Backend Gateway API',
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

// Rate Limiter
app.use(rateLimiter);

// Morgan Winston Logging Integration
const morganFormat = process.env.NODE_ENV === 'production' ? 'combined' : 'dev';
app.use(morgan(morganFormat, {
  stream: {
    write: (message) => logger.info(message.trim())
  }
}));

// Serve public directory
app.use(express.static('public'));

// Serve pipeline routes at both root and /api prefixes
app.use('/', pipelineRoutes);
app.use('/api', pipelineRoutes);

// Root health route
app.use('/health', require('./src/routes/health.routes'));

// Swagger UI Endpoint
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Base Routes
app.use('/api', routes);

// Centralized Error Handler Middleware
app.use(errorMiddleware);

module.exports = app;
