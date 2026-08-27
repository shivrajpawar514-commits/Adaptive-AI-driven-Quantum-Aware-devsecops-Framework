const swaggerJSDoc = require('swagger-jsdoc');
const dotenv = require('dotenv');

dotenv.config();

const PORT = process.env.PORT || 5000;

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Adaptive DevSecOps Framework API Documentation',
      version: '1.0.0',
      description: 'API documentation for the backend foundation of Sprint-05.'
    },
    servers: [
      {
        url: `http://localhost:${PORT}/api`,
        description: 'Development Server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      }
    }
  },
  apis: ['./src/routes/*.js', './src/routes/index.js']
};

const swaggerSpec = swaggerJSDoc(options);

module.exports = swaggerSpec;
