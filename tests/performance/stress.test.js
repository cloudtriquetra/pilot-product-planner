/**
 * Stress Testing for Voice Trade System
 * Tests system limits and breaking points
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Metrics
const successfulTrades = new Counter('successful_trades');
const failedTrades = new Counter('failed_trades');
const systemErrors = new Rate('system_errors');
const responseTime = new Trend('response_time');

// Stress test configuration - push system to limits
export const options = {
  stages: [
    { duration: '30s', target: 100 },  // Ramp to 100 users quickly
    { duration: '1m', target: 200 },   // Push to 200 users
    { duration: '2m', target: 500 },   // Stress with 500 users
    { duration: '1m', target: 1000 },  // Maximum stress
    { duration: '2m', target: 1000 },  // Sustain maximum load
    { duration: '1m', target: 0 },     // Recovery phase
  ],
  thresholds: {
    'system_errors': ['rate<0.5'],     // System should handle 50% error rate max
    'response_time': ['p(50)<2000'],   // Median response under 2s even under stress
  },
};

// Aggressive trade submission
function aggressiveTradeSubmission() {
  const trades = [];
  for (let i = 0; i < 10; i++) {
    trades.push({
      type: Math.random() > 0.5 ? 'BUY' : 'SELL',
      instrument: 'EQUITY',
      symbol: `STRESS${i}`,
      quantity: Math.floor(Math.random() * 1000) + 1,
      price: (Math.random() * 100 + 1).toFixed(2),
      counterparty: 'Stress Test Corp',
      trader: `StressUser_${__VU}_${i}`,
      notes: 'Stress test trade',
    });
  }
  return trades;
}

export default function () {
  const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
  
  // Burst submission - send multiple trades rapidly
  const trades = aggressiveTradeSubmission();
  const batch = {
    'trades': trades.map(trade => ({
      method: 'POST',
      url: `${BASE_URL}/api/trades`,
      body: JSON.stringify(trade),
      params: {
        headers: { 'Content-Type': 'application/json' },
      },
    })),
  };
  
  const startTime = Date.now();
  const responses = http.batch(batch.trades);
  const duration = Date.now() - startTime;
  
  responseTime.add(duration);
  
  // Check responses
  let successes = 0;
  let failures = 0;
  
  responses.forEach(response => {
    if (response.status === 200 || response.status === 201) {
      successes++;
      successfulTrades.add(1);
    } else if (response.status >= 500) {
      systemErrors.add(1);
      failedTrades.add(1);
      failures++;
    } else {
      failedTrades.add(1);
      failures++;
    }
  });
  
  // Concurrent read operations
  const readOperations = [];
  for (let i = 0; i < 5; i++) {
    readOperations.push({
      method: 'GET',
      url: `${BASE_URL}/api/trades`,
      params: {
        headers: { 'Accept': 'application/json' },
      },
    });
  }
  
  const readResponses = http.batch(readOperations);
  readResponses.forEach(response => {
    check(response, {
      'read operation successful': (r) => r.status === 200,
    });
  });
  
  // Memory stress - request large datasets
  const largeDataRequest = http.get(`${BASE_URL}/api/trades?limit=1000`, {
    headers: { 'Accept': 'application/json' },
  });
  
  check(largeDataRequest, {
    'large dataset handled': (r) => r.status === 200 || r.status === 206,
  });
  
  // No sleep - maximum pressure
  if (__VU % 10 === 0) {
    sleep(0.1); // Only every 10th user gets a small break
  }
}

// Spike test scenario
export function spikeTest() {
  const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
  
  // Sudden burst of 1000 simultaneous requests
  const spikeRequests = [];
  for (let i = 0; i < 1000; i++) {
    spikeRequests.push({
      method: 'POST',
      url: `${BASE_URL}/api/trades`,
      body: JSON.stringify({
        type: 'BUY',
        instrument: 'EQUITY',
        symbol: 'SPIKE',
        quantity: 100,
        price: 50,
        counterparty: 'Spike Test',
        trader: `SpikeUser_${i}`,
        notes: 'Spike test',
      }),
      params: {
        headers: { 'Content-Type': 'application/json' },
      },
    });
  }
  
  const startTime = Date.now();
  const responses = http.batch(spikeRequests);
  const totalTime = Date.now() - startTime;
  
  let successCount = 0;
  responses.forEach(response => {
    if (response.status === 200 || response.status === 201) {
      successCount++;
    }
  });
  
  console.log(`Spike test: ${successCount}/1000 successful in ${totalTime}ms`);
  
  return {
    successRate: successCount / 1000,
    totalTime: totalTime,
  };
}

// Recovery test - check system recovery after stress
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    './stress-test-report.json': JSON.stringify(data, null, 2),
    './stress-test-report.html': htmlReport(data, { title: 'Voice Trade Stress Test' }),
  };
}