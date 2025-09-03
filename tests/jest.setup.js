// Jest setup configuration
import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock DOM environment setup
global.showToast = jest.fn();

// Setup test environment
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();
  localStorage.clear();
  
  // Reset DOM
  document.body.innerHTML = '';
});

// Global test utilities
global.waitFor = (fn, timeout = 3000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      try {
        const result = fn();
        if (result) {
          clearInterval(interval);
          resolve(result);
        } else if (Date.now() - startTime > timeout) {
          clearInterval(interval);
          reject(new Error('Timeout waiting for condition'));
        }
      } catch (error) {
        clearInterval(interval);
        reject(error);
      }
    }, 50);
  });
};