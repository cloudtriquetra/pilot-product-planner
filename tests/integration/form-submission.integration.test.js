/**
 * Integration Tests: Form Submission
 * Tests the complete form submission flow including validation, storage, and UI updates
 */

import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('Trade Form Submission Integration', () => {
  let dom;
  let document;
  let window;
  
  beforeEach(() => {
    // Load the HTML file
    const html = fs.readFileSync(
      path.resolve(__dirname, '../../workspace/electronification-of-voice-trades-under-1million/_wip/index.html'),
      'utf-8'
    );
    
    dom = new JSDOM(html, {
      runScripts: 'dangerously',
      resources: 'usable',
      url: 'http://localhost'
    });
    
    document = dom.window.document;
    window = dom.window;
    
    // Mock localStorage
    const localStorageMock = {
      data: {},
      getItem: function(key) {
        return this.data[key] || null;
      },
      setItem: function(key, value) {
        this.data[key] = value;
      },
      removeItem: function(key) {
        delete this.data[key];
      },
      clear: function() {
        this.data = {};
      }
    };
    
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    });
  });

  afterEach(() => {
    dom.window.close();
  });

  describe('Form Field Validation', () => {
    test('should require all mandatory fields', () => {
      const form = document.getElementById('tradeForm');
      const submitBtn = form.querySelector('button[type="submit"]');
      
      // Try to submit empty form
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      // Check that form is invalid
      expect(form.checkValidity()).toBe(false);
    });

    test('should validate trade type selection', () => {
      const tradeTypeSelect = document.getElementById('tradeType');
      
      // Initially empty
      expect(tradeTypeSelect.value).toBe('');
      
      // Select BUY
      tradeTypeSelect.value = 'BUY';
      expect(tradeTypeSelect.value).toBe('BUY');
      
      // Select SELL
      tradeTypeSelect.value = 'SELL';
      expect(tradeTypeSelect.value).toBe('SELL');
    });

    test('should validate instrument selection', () => {
      const instrumentSelect = document.getElementById('instrument');
      
      // Test all valid instruments
      const validInstruments = ['EQUITY', 'BOND', 'FX', 'COMMODITY'];
      validInstruments.forEach(instrument => {
        instrumentSelect.value = instrument;
        expect(instrumentSelect.value).toBe(instrument);
      });
    });

    test('should validate numeric fields', () => {
      const quantityInput = document.getElementById('quantity');
      const priceInput = document.getElementById('price');
      
      // Test quantity constraints
      quantityInput.value = '100';
      expect(quantityInput.validity.valid).toBe(true);
      
      quantityInput.value = '0';
      expect(quantityInput.validity.valid).toBe(false);
      
      quantityInput.value = '-10';
      expect(quantityInput.validity.valid).toBe(false);
      
      // Test price constraints
      priceInput.value = '150.50';
      expect(priceInput.validity.valid).toBe(true);
      
      priceInput.value = '0';
      expect(priceInput.validity.valid).toBe(false);
      
      priceInput.value = '-50';
      expect(priceInput.validity.valid).toBe(false);
    });

    test('should convert symbol to uppercase', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Fill form with valid data
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'aapl';
      document.getElementById('quantity').value = '100';
      document.getElementById('price').value = '150.50';
      document.getElementById('counterparty').value = 'Test Corp';
      document.getElementById('trader').value = 'John Doe';
      
      // Submit form
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      // Check that symbol was converted to uppercase in storage
      setTimeout(() => {
        const stored = window.localStorage.getItem('voiceTrades');
        if (stored) {
          const trades = JSON.parse(stored);
          expect(trades[0].symbol).toBe('AAPL');
        }
        done();
      }, 100);
    });
  });

  describe('Trade Processing', () => {
    test('should calculate total correctly', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Fill form
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'MSFT';
      document.getElementById('quantity').value = '200';
      document.getElementById('price').value = '300.00';
      document.getElementById('counterparty').value = 'Test Corp';
      document.getElementById('trader').value = 'Jane Doe';
      
      // Submit
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      setTimeout(() => {
        const stored = window.localStorage.getItem('voiceTrades');
        const trades = JSON.parse(stored);
        expect(trades[0].total).toBe(60000); // 200 * 300
        done();
      }, 100);
    });

    test('should reject trades over $1M', () => {
      const form = document.getElementById('tradeForm');
      
      // Fill form with trade over $1M
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'EXPENSIVE';
      document.getElementById('quantity').value = '10000';
      document.getElementById('price').value = '100';
      document.getElementById('counterparty').value = 'Test Corp';
      document.getElementById('trader').value = 'Rich Trader';
      
      // Mock showToast to capture error message
      let toastMessage = '';
      window.showToast = (msg, type) => {
        toastMessage = msg;
      };
      
      // Submit
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      // Check that trade was rejected
      expect(toastMessage).toContain('exceeds $1M limit');
    });

    test('should generate unique trade IDs', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Submit multiple trades
      const submitTrade = (symbol) => {
        document.getElementById('tradeType').value = 'BUY';
        document.getElementById('instrument').value = 'EQUITY';
        document.getElementById('symbol').value = symbol;
        document.getElementById('quantity').value = '100';
        document.getElementById('price').value = '100';
        document.getElementById('counterparty').value = 'Test Corp';
        document.getElementById('trader').value = 'Trader';
        
        const submitEvent = new window.Event('submit', { cancelable: true });
        form.dispatchEvent(submitEvent);
      };
      
      submitTrade('AAPL');
      setTimeout(() => submitTrade('MSFT'), 50);
      setTimeout(() => submitTrade('GOOGL'), 100);
      
      setTimeout(() => {
        const stored = window.localStorage.getItem('voiceTrades');
        const trades = JSON.parse(stored);
        
        // Check that all IDs are unique
        const ids = trades.map(t => t.id);
        const uniqueIds = [...new Set(ids)];
        expect(uniqueIds.length).toBe(ids.length);
        
        // Check ID format
        ids.forEach(id => {
          expect(id).toMatch(/^VT\d+$/);
        });
        
        done();
      }, 200);
    });

    test('should set initial status as pending', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Fill and submit form
      document.getElementById('tradeType').value = 'SELL';
      document.getElementById('instrument').value = 'BOND';
      document.getElementById('symbol').value = 'TEST';
      document.getElementById('quantity').value = '500';
      document.getElementById('price').value = '95.50';
      document.getElementById('counterparty').value = 'Test Corp';
      document.getElementById('trader').value = 'Trader';
      
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      setTimeout(() => {
        const stored = window.localStorage.getItem('voiceTrades');
        const trades = JSON.parse(stored);
        expect(trades[0].status).toBe('pending');
        done();
      }, 100);
    });

    test('should auto-confirm trades after delay', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Fill and submit form
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'FX';
      document.getElementById('symbol').value = 'EURUSD';
      document.getElementById('quantity').value = '1000';
      document.getElementById('price').value = '1.10';
      document.getElementById('counterparty').value = 'Test Bank';
      document.getElementById('trader').value = 'FX Trader';
      
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      // Check initial status
      setTimeout(() => {
        const stored1 = window.localStorage.getItem('voiceTrades');
        const trades1 = JSON.parse(stored1);
        expect(trades1[0].status).toBe('pending');
      }, 100);
      
      // Check after auto-confirm delay
      setTimeout(() => {
        const stored2 = window.localStorage.getItem('voiceTrades');
        const trades2 = JSON.parse(stored2);
        expect(trades2[0].status).toBe('confirmed');
        done();
      }, 2500);
    }, 3000);
  });

  describe('UI Updates', () => {
    test('should clear form after successful submission', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Fill form
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'AAPL';
      document.getElementById('quantity').value = '100';
      document.getElementById('price').value = '150';
      document.getElementById('counterparty').value = 'Test';
      document.getElementById('trader').value = 'Trader';
      
      // Submit
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      setTimeout(() => {
        // Check that form was cleared
        expect(document.getElementById('tradeType').value).toBe('');
        expect(document.getElementById('instrument').value).toBe('');
        expect(document.getElementById('symbol').value).toBe('');
        expect(document.getElementById('quantity').value).toBe('');
        expect(document.getElementById('price').value).toBe('');
        done();
      }, 100);
    });

    test('should update trade count badge', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Initial count should be 0
      expect(document.getElementById('tradeCount').textContent).toBe('0 trades');
      
      // Submit a trade
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'TEST';
      document.getElementById('quantity').value = '100';
      document.getElementById('price').value = '50';
      document.getElementById('counterparty').value = 'Test';
      document.getElementById('trader').value = 'Trader';
      
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      setTimeout(() => {
        expect(document.getElementById('tradeCount').textContent).toBe('1 trades');
        done();
      }, 100);
    });

    test('should update summary statistics', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Submit multiple trades
      const submitTrade = (quantity, price) => {
        document.getElementById('tradeType').value = 'BUY';
        document.getElementById('instrument').value = 'EQUITY';
        document.getElementById('symbol').value = 'TEST';
        document.getElementById('quantity').value = String(quantity);
        document.getElementById('price').value = String(price);
        document.getElementById('counterparty').value = 'Test';
        document.getElementById('trader').value = 'Trader';
        
        const submitEvent = new window.Event('submit', { cancelable: true });
        form.dispatchEvent(submitEvent);
      };
      
      submitTrade(100, 50);  // $5,000
      setTimeout(() => submitTrade(200, 100), 100);  // $20,000
      
      setTimeout(() => {
        const totalTrades = document.getElementById('totalTrades').textContent;
        const totalVolume = document.getElementById('totalVolume').textContent;
        const avgSize = document.getElementById('avgSize').textContent;
        
        expect(totalTrades).toBe('2');
        expect(totalVolume).toContain('25,000');  // $25,000 total
        expect(avgSize).toContain('12,500');  // $12,500 average
        done();
      }, 300);
    });
  });

  describe('Quick Actions', () => {
    test('should set trade type via quick buy button', () => {
      const quickBuyBtn = document.querySelector('button[onclick="setTradeType(\'BUY\')"]');
      quickBuyBtn.click();
      expect(document.getElementById('tradeType').value).toBe('BUY');
    });

    test('should set trade type via quick sell button', () => {
      const quickSellBtn = document.querySelector('button[onclick="setTradeType(\'SELL\')"]');
      quickSellBtn.click();
      expect(document.getElementById('tradeType').value).toBe('SELL');
    });

    test('should set instrument via quick equity button', () => {
      const equityBtn = document.querySelector('button[onclick="setInstrument(\'EQUITY\')"]');
      equityBtn.click();
      expect(document.getElementById('instrument').value).toBe('EQUITY');
    });

    test('should set instrument via quick bond button', () => {
      const bondBtn = document.querySelector('button[onclick="setInstrument(\'BOND\')"]');
      bondBtn.click();
      expect(document.getElementById('instrument').value).toBe('BOND');
    });

    test('should clear form via clear button', () => {
      // Fill form
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('symbol').value = 'TEST';
      
      // Click clear
      const clearBtn = document.querySelector('button[onclick="clearForm()"]');
      clearBtn.click();
      
      // Check cleared
      expect(document.getElementById('tradeType').value).toBe('');
      expect(document.getElementById('symbol').value).toBe('');
    });
  });

  describe('Storage Persistence', () => {
    test('should persist trades to localStorage', (done) => {
      const form = document.getElementById('tradeForm');
      
      // Submit trade
      document.getElementById('tradeType').value = 'BUY';
      document.getElementById('instrument').value = 'EQUITY';
      document.getElementById('symbol').value = 'PERSIST';
      document.getElementById('quantity').value = '100';
      document.getElementById('price').value = '50';
      document.getElementById('counterparty').value = 'Test';
      document.getElementById('trader').value = 'Trader';
      
      const submitEvent = new window.Event('submit', { cancelable: true });
      form.dispatchEvent(submitEvent);
      
      setTimeout(() => {
        const stored = window.localStorage.getItem('voiceTrades');
        expect(stored).toBeTruthy();
        
        const trades = JSON.parse(stored);
        expect(trades).toHaveLength(1);
        expect(trades[0].symbol).toBe('PERSIST');
        done();
      }, 100);
    });

    test('should load trades from localStorage on init', () => {
      // Pre-populate localStorage
      const existingTrades = [
        {
          id: 'VT1000',
          type: 'BUY',
          symbol: 'EXISTING',
          quantity: 100,
          price: 50,
          total: 5000,
          status: 'confirmed'
        }
      ];
      window.localStorage.setItem('voiceTrades', JSON.stringify(existingTrades));
      
      // Trigger load
      window.dispatchEvent(new window.Event('DOMContentLoaded'));
      
      // Check that trades were loaded
      setTimeout(() => {
        const tradeList = document.getElementById('tradeList');
        expect(tradeList.innerHTML).toContain('EXISTING');
      }, 100);
    });
  });
});