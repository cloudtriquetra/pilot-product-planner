/**
 * Mock Data Generator for Testing
 */

export const MockTradeData = {
  // Valid trade templates
  validTrades: {
    equity: {
      type: 'BUY',
      instrument: 'EQUITY',
      symbol: 'AAPL',
      quantity: 100,
      price: 150.50,
      counterparty: 'Goldman Sachs',
      trader: 'John Smith',
      notes: 'Voice trade from morning call',
      status: 'pending',
      voiceTrade: true
    },
    bond: {
      type: 'SELL',
      instrument: 'BOND',
      symbol: 'US10Y',
      quantity: 1000,
      price: 98.75,
      counterparty: 'JP Morgan',
      trader: 'Jane Doe',
      notes: 'Treasury bond sale',
      status: 'pending',
      voiceTrade: true
    },
    fx: {
      type: 'BUY',
      instrument: 'FX',
      symbol: 'EURUSD',
      quantity: 50000,
      price: 1.0850,
      counterparty: 'Barclays',
      trader: 'Mike Johnson',
      notes: 'EUR/USD spot trade',
      status: 'pending',
      voiceTrade: true
    },
    commodity: {
      type: 'SELL',
      instrument: 'COMMODITY',
      symbol: 'GOLD',
      quantity: 10,
      price: 1950.00,
      counterparty: 'HSBC',
      trader: 'Sarah Wilson',
      notes: 'Gold futures',
      status: 'pending',
      voiceTrade: true
    }
  },

  // Invalid trade templates
  invalidTrades: {
    overLimit: {
      type: 'BUY',
      instrument: 'EQUITY',
      symbol: 'EXPENSIVE',
      quantity: 10000,
      price: 100,
      counterparty: 'Test Corp',
      trader: 'Rich Trader',
      notes: 'Trade over $1M limit'
    },
    missingFields: {
      type: '',
      instrument: 'EQUITY',
      symbol: '',
      quantity: null,
      price: 150
    },
    invalidTypes: {
      type: 'HOLD',
      instrument: 'CRYPTO',
      symbol: 'BTC',
      quantity: -10,
      price: -100,
      counterparty: '',
      trader: ''
    },
    invalidNumbers: {
      type: 'BUY',
      instrument: 'EQUITY',
      symbol: 'TEST',
      quantity: 100.5,
      price: 0,
      counterparty: 'Test',
      trader: 'Test'
    }
  },

  // Generate random valid trade
  generateRandomTrade: () => {
    const types = ['BUY', 'SELL'];
    const instruments = ['EQUITY', 'BOND', 'FX', 'COMMODITY'];
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'US10Y', 'EURUSD', 'GOLD'];
    const counterparties = ['Goldman Sachs', 'JP Morgan', 'Morgan Stanley', 'Barclays', 'HSBC'];
    const traders = ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson', 'Tom Brown'];
    
    const quantity = Math.floor(Math.random() * 1000) + 1;
    const price = (Math.random() * 500 + 1).toFixed(2);
    const total = quantity * parseFloat(price);
    
    // Ensure under $1M
    if (total >= 1000000) {
      return MockTradeData.generateRandomTrade();
    }
    
    return {
      id: `VT${Math.floor(Math.random() * 9000) + 1000}`,
      timestamp: new Date().toISOString(),
      type: types[Math.floor(Math.random() * types.length)],
      instrument: instruments[Math.floor(Math.random() * instruments.length)],
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      quantity: quantity,
      price: parseFloat(price),
      total: total,
      counterparty: counterparties[Math.floor(Math.random() * counterparties.length)],
      trader: traders[Math.floor(Math.random() * traders.length)],
      notes: 'Automated test trade',
      status: 'pending',
      voiceTrade: true
    };
  },

  // Generate batch of trades
  generateBatch: (count) => {
    const trades = [];
    for (let i = 0; i < count; i++) {
      trades.push(MockTradeData.generateRandomTrade());
    }
    return trades;
  },

  // Edge case trades
  edgeCases: {
    justUnderLimit: {
      type: 'BUY',
      instrument: 'EQUITY',
      symbol: 'LIMIT',
      quantity: 9999,
      price: 99.99,
      counterparty: 'Edge Corp',
      trader: 'Edge Trader',
      total: 999900.01
    },
    minimalValues: {
      type: 'BUY',
      instrument: 'EQUITY',
      symbol: 'MIN',
      quantity: 1,
      price: 0.01,
      counterparty: 'Min Corp',
      trader: 'Min Trader',
      total: 0.01
    },
    maxSymbolLength: {
      type: 'SELL',
      instrument: 'BOND',
      symbol: 'VERYLONGSY',
      quantity: 100,
      price: 100,
      counterparty: 'Test',
      trader: 'Test',
      total: 10000
    }
  }
};

export const MockFormData = {
  // Form input scenarios
  fillValidForm: (document) => {
    document.getElementById('tradeType').value = 'BUY';
    document.getElementById('instrument').value = 'EQUITY';
    document.getElementById('symbol').value = 'AAPL';
    document.getElementById('quantity').value = '100';
    document.getElementById('price').value = '150.50';
    document.getElementById('counterparty').value = 'Test Corp';
    document.getElementById('trader').value = 'Test Trader';
    document.getElementById('notes').value = 'Test notes';
  },

  fillInvalidForm: (document) => {
    document.getElementById('tradeType').value = '';
    document.getElementById('instrument').value = '';
    document.getElementById('symbol').value = '';
    document.getElementById('quantity').value = '-10';
    document.getElementById('price').value = '0';
    document.getElementById('counterparty').value = '';
    document.getElementById('trader').value = '';
  },

  clearForm: (document) => {
    document.getElementById('tradeForm').reset();
  }
};

export const MockLocalStorage = {
  // Mock localStorage implementation
  createMock: () => {
    const storage = {};
    return {
      getItem: (key) => storage[key] || null,
      setItem: (key, value) => { storage[key] = value; },
      removeItem: (key) => { delete storage[key]; },
      clear: () => { 
        for (const key in storage) {
          delete storage[key];
        }
      },
      get data() { return { ...storage }; }
    };
  },

  // Pre-populate with test data
  populateWithTrades: (localStorage, trades) => {
    localStorage.setItem('voiceTrades', JSON.stringify(trades));
  }
};

export const MockDOMEvents = {
  // Create submit event
  createSubmitEvent: (window) => {
    return new window.Event('submit', { 
      cancelable: true,
      bubbles: true 
    });
  },

  // Create click event
  createClickEvent: (window) => {
    return new window.MouseEvent('click', {
      view: window,
      bubbles: true,
      cancelable: true
    });
  },

  // Create keyboard event
  createKeyboardEvent: (window, key, ctrlKey = false, metaKey = false) => {
    return new window.KeyboardEvent('keydown', {
      key: key,
      ctrlKey: ctrlKey,
      metaKey: metaKey,
      bubbles: true
    });
  }
};

export const TestHelpers = {
  // Wait for condition
  waitFor: (condition, timeout = 3000) => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const interval = setInterval(() => {
        if (condition()) {
          clearInterval(interval);
          resolve();
        } else if (Date.now() - startTime > timeout) {
          clearInterval(interval);
          reject(new Error('Timeout waiting for condition'));
        }
      }, 50);
    });
  },

  // Wait for element
  waitForElement: (selector, document, timeout = 3000) => {
    return TestHelpers.waitFor(
      () => document.querySelector(selector),
      timeout
    );
  },

  // Format number like the app does
  formatNumber: (num) => {
    return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
  },

  // Format time like the app does
  formatTime: (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  },

  // Verify trade in list
  verifyTradeInList: (document, trade) => {
    const tradeList = document.getElementById('tradeList');
    const content = tradeList.innerHTML;
    return content.includes(trade.symbol) && 
           content.includes(trade.type) &&
           content.includes(TestHelpers.formatNumber(trade.total));
  },

  // Get summary values
  getSummaryValues: (document) => {
    return {
      totalTrades: document.getElementById('totalTrades').textContent,
      totalVolume: document.getElementById('totalVolume').textContent,
      avgSize: document.getElementById('avgSize').textContent
    };
  }
};

export default {
  MockTradeData,
  MockFormData,
  MockLocalStorage,
  MockDOMEvents,
  TestHelpers
};