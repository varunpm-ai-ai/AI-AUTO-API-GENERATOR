/**
 * Request Validation Middleware using Zod for Auth Service
 */
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiError = require('../utils/apiError');

const validateRequest = (schema) => (req, res, next) => {
  try {
    const result = schema.safeParse({
      body: req.body,
      query: req.query,
      params: req.params
    });

    if (!result.success) {
      const formattedErrors = result.error.errors.map((err) => ({
        field: err.path.join('.').replace(/^body\./, ''),
        message: err.message
      }));

      throw new ApiError(
        HTTP_STATUS.BAD_REQUEST,
        'Request input validation failed',
        'VALIDATION_ERROR',
        formattedErrors
      );
    }

    if (result.data.body) req.body = result.data.body;
    if (result.data.query) req.query = result.data.query;
    if (result.data.params) req.params = result.data.params;

    next();
  } catch (error) {
    next(error);
  }
};

module.exports = validateRequest;
