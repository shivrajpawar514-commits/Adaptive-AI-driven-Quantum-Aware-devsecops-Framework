const swaggerJSDoc = require('swagger-jsdoc');

const PORT = process.env.PORT || 6001;

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Telemetry Monitoring Service API',
      version: '1.0.0',
      description: 'REST and Prometheus metrics collection endpoints for Sprint-06'
    },
    servers: [
      {
        url: `http://localhost:${PORT}`
      }
    ]
  },
  apis: ['./src/routes/*.js']
};

module.exports = swaggerJSDoc(options);
