/**
 * Public Request Validation Middleware for API Gateway
 * Implements Section 4.5 of API Gateway Implementation Spec.
 */
const HTTP_STATUS = require('../constants/httpStatusCodes');
const ApiError = require('../utils/apiError');

const validateRequest = (schema) => (req, res, next) => {
  try {
    const dataToValidate = {
      body: req.body,
      query: req.query,
      params: req.params,
      headers: req.headers
    };

    const result = schema.safeParse(dataToValidate);
    if (!result.success) {
      const formattedErrors = result.error.errors.map((err) => ({
        field: err.path.join('.'),
        message: err.message
      }));

      throw new ApiError(
        HTTP_STATUS.BAD_REQUEST,
        'Request validation failed',
        'VALIDATION_ERROR',
        formattedErrors
      );
    }

    // Replace sanitized values
    if (result.data.body) req.body = result.data.body;
    if (result.data.query) req.query = result.data.query;
    if (result.data.params) req.params = result.data.params;

    next();
  } catch (error) {
    next(error);
  }
};

module.exports = validateRequest;
