/**
 * Performance and Load Tests using k6
 * Tests system behavior under various load conditions
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
const tradeCounter = new Counter('trades_submitted');
const tradeErrors = new Rate('trade_errors');
const tradeDuration = new Trend('trade_duration');
const validationErrors = new Rate('validation_errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 50 },  // Ramp up to 50 users
    { duration: '2m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 100 }, // Ramp up to 100 users
    { duration: '2m', target: 100 },  // Stay at 100 users
    { duration: '1m', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% of requests under 500ms
    'trade_errors': ['rate<0.05'],                     // Error rate under 5%
    'validation_errors': ['rate<0.1'],                 // Validation error rate under 10%
    'http_req_failed': ['rate<0.1'],                  // HTTP failure rate under 10%
  },
};

// Test data generator
function generateTradeData() {
  const types = ['BUY', 'SELL'];
  const instruments = ['EQUITY', 'BOND', 'FX', 'COMMODITY'];
  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'US10Y', 'EURUSD', 'GOLD'];
  const counterparties = ['Goldman Sachs', 'JP Morgan', 'Morgan Stanley', 'Barclays', 'HSBC'];
  
  const quantity = Math.floor(Math.random() * 1000) + 1;
  const price = (Math.random() * 500 + 1).toFixed(2);
  const total = quantity * parseFloat(price);
  
  // Ensure under $1M
  if (total >= 1000000) {
    return generateTradeData();
  }
  
  return {
    type: types[Math.floor(Math.random() * types.length)],
    instrument: instruments[Math.floor(Math.random() * instruments.length)],
    symbol: symbols[Math.floor(Math.random() * symbols.length)],
    quantity: quantity,
    price: parseFloat(price),
    counterparty: counterparties[Math.floor(Math.random() * counterparties.length)],
    trader: `Trader_${__VU}`, // Use virtual user ID
    notes: `Load test trade from VU ${__VU}`,
  };
}

// Main test scenario
export default function () {
  const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
  
  // Scenario 1: Submit valid trade
  const tradeData = generateTradeData();
  const submitStart = Date.now();
  
  const submitResponse = http.post(
    `${BASE_URL}/api/trades`,
    JSON.stringify(tradeData),
    {
      headers: { 
        'Content-Type': 'application/json',
        'X-Voice-Trade': 'true'
      },
    }
  );
  
  const submitDuration = Date.now() - submitStart;
  tradeDuration.add(submitDuration);
  
  const submitSuccess = check(submitResponse, {
    'trade submitted successfully': (r) => r.status === 200 || r.status === 201,
    'response has trade ID': (r) => {
      const body = JSON.parse(r.body);
      return body && body.id && body.id.startsWith('VT');
    },
    'response time under 500ms': (r) => submitDuration < 500,
  });
  
  if (submitSuccess) {
    tradeCounter.add(1);
  } else {
    tradeErrors.add(1);
  }
  
  sleep(1); // Wait 1 second between requests
  
  // Scenario 2: Query trades
  const queryResponse = http.get(`${BASE_URL}/api/trades`, {
    headers: { 'Accept': 'application/json' },
  });
  
  check(queryResponse, {
    'trades retrieved successfully': (r) => r.status === 200,
    'response is array': (r) => {
      const body = JSON.parse(r.body);
      return Array.isArray(body);
    },
  });
  
  sleep(0.5);
  
  // Scenario 3: Submit invalid trade (over $1M)
  if (Math.random() < 0.1) { // 10% chance to test validation
    const invalidTrade = {
      ...tradeData,
      quantity: 10000,
      price: 100,
    };
    
    const invalidResponse = http.post(
      `${BASE_URL}/api/trades`,
      JSON.stringify(invalidTrade),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
    
    const validationCheck = check(invalidResponse, {
      'validation error returned': (r) => r.status === 400,
      'error message correct': (r) => {
        const body = JSON.parse(r.body);
        return body && body.error && body.error.includes('$1M limit');
      },
    });
    
    if (!validationCheck) {
      validationErrors.add(1);
    }
  }
  
  sleep(0.5);
  
  // Scenario 4: Get trade statistics
  const statsResponse = http.get(`${BASE_URL}/api/trades/stats`, {
    headers: { 'Accept': 'application/json' },
  });
  
  check(statsResponse, {
    'stats retrieved successfully': (r) => r.status === 200,
    'stats contain required fields': (r) => {
      const body = JSON.parse(r.body);
      return body && 
             body.hasOwnProperty('totalTrades') &&
             body.hasOwnProperty('totalVolume') &&
             body.hasOwnProperty('avgSize');
    },
  });
  
  sleep(1);
}

// Setup function - run once before test
export function setup() {
  const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
  
  // Check if API is available
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error('API is not available');
  }
  
  return { startTime: Date.now() };
}

// Teardown function - run once after test
export function teardown(data) {
  const duration = Date.now() - data.startTime;
  console.log(`Test completed in ${duration}ms`);
}