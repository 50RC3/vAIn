export class NetworkError extends Error {
  constructor(message = 'Network connection failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

export const getErrorMessage = (error) => {
  if (error instanceof NetworkError) {
    return 'Unable to connect to the server. Please check your internet connection.';
  }
  if (error instanceof APIError) {
    return `Server error: ${error.message}`;
  }
  return 'An unexpected error occurred. Please try again.';
};
