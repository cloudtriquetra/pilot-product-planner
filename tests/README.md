# Voice Trade Electronification - Test Suite

Comprehensive test suite for the Voice Trade Electronification MVP, providing unit, integration, E2E, and performance testing with full coverage reporting.

## 📁 Test Structure

```
tests/
├── unit/                     # Unit tests for business logic
│   └── trade-validation.unit.test.js
├── integration/              # Integration tests for form submission
│   └── form-submission.integration.test.js
├── e2e/                     # End-to-end browser tests
│   ├── trade-workflow.e2e.test.js
│   └── playwright.config.js
├── performance/             # Load and stress tests
│   ├── load.test.js
│   └── stress.test.js
├── test-utils/              # Shared test utilities
│   └── mock-data.js
├── coverage/                # Coverage reports (generated)
├── package.json            # Test dependencies and scripts
├── jest.setup.js           # Jest configuration
└── .gitignore             # Ignore generated files
```

## 🚀 Quick Start

### Installation
```bash
cd tests
npm install
```

### Run All Tests
```bash
npm test
```

### Run with Coverage
```bash
npm run test:coverage
```

## 🧪 Test Types

### Unit Tests
Tests core business logic in isolation:
- Trade validation rules
- Amount calculations
- Trade ID generation
- Field validations
- Edge cases and boundaries

```bash
npm run test:unit
```

### Integration Tests
Tests component interactions:
- Form submission flow
- LocalStorage persistence
- DOM updates
- Event handling
- Quick actions
- Keyboard shortcuts

```bash
npm run test:integration
```

### E2E Tests
Full user journey testing with Playwright:
- Complete trade workflows
- Multi-browser testing
- Mobile responsiveness
- Visual validation
- Trade persistence
- Auto-confirmation

```bash
npm run test:e2e
```

### Performance Tests
Load and stress testing with k6:
- Concurrent user simulation
- Response time monitoring
- Error rate tracking
- Spike testing
- Recovery testing

```bash
npm run test:performance
```

## 📊 Coverage Requirements

The test suite enforces the following coverage thresholds:

- **Branches**: 80%
- **Functions**: 80%
- **Lines**: 80%
- **Statements**: 80%

Generate HTML coverage report:
```bash
npm run test:report
```

View coverage report:
```bash
open coverage/index.html
```

## 🎯 Test Scenarios

### Critical User Flows
1. **Voice Trade Entry**: Submit trades under $1M limit
2. **Validation**: Reject trades over limit
3. **Quick Actions**: Use quick buttons for fast entry
4. **Auto-Confirmation**: Trades confirm after 2 seconds
5. **Persistence**: Trades survive page reload
6. **Summary Updates**: Real-time statistics

### Edge Cases Covered
- Boundary values ($999,999.99)
- Minimal values ($0.01)
- Invalid data types
- Missing required fields
- Network failures
- Concurrent submissions
- Browser compatibility

## 🔧 Test Configuration

### Jest Configuration
- Environment: jsdom
- Coverage collection from src/
- HTML and text coverage reporters
- Mock localStorage support

### Playwright Configuration
- Browsers: Chrome, Firefox, Safari
- Mobile: iOS Safari, Android Chrome
- Screenshots on failure
- Video recording on failure
- Trace collection on retry

### k6 Configuration
- Ramp-up stages
- Threshold validation
- Custom metrics
- JSON/HTML reporting

## 📝 Writing Tests

### Unit Test Example
```javascript
test('should reject trades over $1M', () => {
  const result = tradeValidator.validateTradeAmount(1000000);
  expect(result).toBe(false);
});
```

### Integration Test Example
```javascript
test('should submit valid trade', (done) => {
  fillValidForm();
  form.dispatchEvent(new Event('submit'));
  
  setTimeout(() => {
    const trades = JSON.parse(localStorage.getItem('voiceTrades'));
    expect(trades).toHaveLength(1);
    done();
  }, 100);
});
```

### E2E Test Example
```javascript
test('Complete trade workflow', async ({ page }) => {
  await page.fill('#symbol', 'AAPL');
  await page.click('button[type="submit"]');
  await expect(page.locator('#tradeList')).toContainText('AAPL');
});
```

## 🐛 Debugging Tests

### Debug Jest Tests
```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

### Debug Playwright Tests
```bash
npx playwright test --debug
```

### View Playwright Trace
```bash
npx playwright show-trace trace.zip
```

## 📈 Continuous Integration

### GitHub Actions Workflow
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v2
```

## 🚨 Common Issues

### Tests Failing Locally
1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear test cache: `npx jest --clearCache`
3. Check Node version: `node --version` (>= 14.x required)

### E2E Tests Failing
1. Install browsers: `npx playwright install`
2. Check file paths are correct
3. Ensure HTML file exists in workspace/

### Performance Tests Failing
1. Ensure API endpoint is running
2. Set BASE_URL environment variable
3. Check network connectivity

## 📚 Test Utilities

### Mock Data Generator
```javascript
import { MockTradeData } from './test-utils/mock-data';

const trade = MockTradeData.generateRandomTrade();
const batch = MockTradeData.generateBatch(10);
```

### Test Helpers
```javascript
import { TestHelpers } from './test-utils/mock-data';

await TestHelpers.waitFor(() => condition, 3000);
const formatted = TestHelpers.formatNumber(10000);
```

## 🎭 Test Coverage Areas

### Functionality Coverage
- ✅ Trade validation logic
- ✅ Form submission flow
- ✅ LocalStorage persistence
- ✅ UI updates and rendering
- ✅ Quick action buttons
- ✅ Keyboard shortcuts
- ✅ Trade auto-confirmation
- ✅ Summary calculations
- ✅ Error handling
- ✅ Mobile responsiveness

### Browser Coverage
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari/WebKit
- ✅ Mobile Chrome
- ✅ Mobile Safari

### Performance Metrics
- ✅ Response time < 500ms (p95)
- ✅ Error rate < 5%
- ✅ 100 concurrent users
- ✅ 1000 trades/minute throughput

## 🔄 Test Maintenance

### Regular Tasks
- Update test data monthly
- Review coverage reports weekly
- Update browser versions quarterly
- Performance baseline updates

### Before Release
1. Run full test suite
2. Review coverage report
3. Check performance metrics
4. Validate on all browsers
5. Document any known issues

## 📞 Support

For test-related issues:
- Check test output logs
- Review coverage reports
- Consult mock data utilities
- Update test dependencies

## 📄 License

Test suite follows the same license as the main application.