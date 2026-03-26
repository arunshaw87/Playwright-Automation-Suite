# Mobile Test Framework

Mobile automation framework using **Python 3.13**, **Appium 2.x**, and **Pytest**.
Implements the Page Object Model (POM) pattern with YAML-based capability management
and automatic skip when an Appium server is not available.

## Structure

```
tests/mobile/
├── caps/
│   ├── android_caps.yaml     # Android desired capabilities (Appium 2.x)
│   └── ios_caps.yaml         # iOS desired capabilities (Appium 2.x)
├── pages/
│   ├── base_page.py          # BasePage: driver, wait helpers, screenshot, swipe
│   ├── login_page.py         # LoginPage: username/password/login button/error
│   ├── home_page.py          # HomePage: products title, menu, cart
│   ├── product_list_page.py  # ProductListPage: item list, sort, scroll
│   └── product_detail_page.py# ProductDetailPage: title, price, add/remove cart
├── tests/
│   ├── test_login.py         # Valid login, invalid credentials, empty fields
│   ├── test_navigation.py    # Home screen, back navigation, scroll
│   └── test_product_browse.py# List items, tap product, detail assertions, cart
├── utils/
│   ├── driver_factory.py     # Loads caps YAML + env overrides → AppiumDriver
│   └── wait_helpers.py       # Explicit waits, swipe gestures
├── conftest.py               # android_driver, ios_driver, driver fixtures + screenshot on fail
├── pytest.ini                # Markers, JUnit XML, pythonpath, logging
├── requirements-mobile.txt   # Pinned dependencies
└── README.md                 # This file
```

## Prerequisites

1. **Python 3.13**
2. **Appium 2.x server** running locally or remotely (`npm install -g appium@next`)
3. **Android**: Android SDK, ADB, an emulator or physical device
4. **iOS**: Xcode, Simulator or physical device (Mac only)
5. **App under test**: Appium demo app or configure your own via env vars

## Setup

```bash
cd tests/mobile

python3.13 -m venv .venv
source .venv/bin/activate

pip install -r requirements-mobile.txt

# Install Appium UiAutomator2 driver (Android)
appium driver install uiautomator2

# Install Appium XCUITest driver (iOS)
appium driver install xcuitest
```

## Configuration

All capabilities can be overridden via environment variables:

| Variable             | Default            | Description                          |
|----------------------|--------------------|--------------------------------------|
| `APPIUM_SERVER_URL`  | `http://localhost:4723` | Appium server URL                |
| `MOBILE_PLATFORM`    | `android`          | `android` or `ios`                   |
| `ANDROID_DEVICE_NAME`| `emulator-5554`    | Android device/emulator name         |
| `ANDROID_APP_PATH`   | —                  | Path to `.apk` file                  |
| `ANDROID_APP_PACKAGE`| —                  | App package name (for installed apps)|
| `ANDROID_APP_ACTIVITY`| —                 | App launch activity                  |
| `IOS_DEVICE_NAME`    | `iPhone 15 Simulator` | iOS device/simulator name         |
| `IOS_PLATFORM_VERSION`| `17.5`            | iOS version                          |
| `IOS_APP_PATH`       | —                  | Path to `.app`/`.ipa`                |
| `IOS_BUNDLE_ID`      | —                  | Bundle ID for installed apps         |
| `MOBILE_ELEMENT_TIMEOUT`| `10`            | Default explicit wait timeout (secs) |

## Running Tests

### Start Appium server first
```bash
appium server --port 4723
```

### Run all mobile tests (Android)
```bash
APPIUM_SERVER_URL=http://localhost:4723 \
ANDROID_APP_PATH=/path/to/app.apk \
pytest tests/ -v
```

### Run only smoke tests
```bash
pytest tests/ -m smoke -v
```

### Run iOS tests
```bash
MOBILE_PLATFORM=ios \
IOS_APP_PATH=/path/to/app.app \
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_login.py -v
```

## Test Marks

| Mark         | Description                            |
|--------------|----------------------------------------|
| `smoke`      | Critical path — login flow             |
| `regression` | Full regression suite                  |
| `mobile`     | All mobile tests                       |
| `android`    | Android-only tests                     |
| `ios`        | iOS-only tests                         |
| `login`      | Login flow tests                       |
| `navigation` | Navigation flow tests                  |
| `product`    | Product browsing tests                 |

## Fixture Design

### `android_driver` (function-scoped)
Creates a fresh Appium WebDriver session for Android before each test and quits
it after. Automatically **skips** if the Appium server is unreachable.

### `ios_driver` (function-scoped)
Same pattern as `android_driver` but for iOS.

### `driver` (function-scoped)
Resolves to `android_driver` or `ios_driver` based on `MOBILE_PLATFORM` env var.

## Screenshots on Failure
Failure screenshots are automatically captured via `pytest_runtest_makereport`
hook and saved to `reports/screenshots/`.

## CI Integration

Mobile tests are typically run manually or in a device cloud (BrowserStack, Sauce Labs).
The CI workflow marks these jobs as `continue-on-error: true` since device availability
is not guaranteed. For local CI with an emulator:

```bash
# Start emulator (Android)
emulator -avd Pixel_5_API_33 -no-window &
adb wait-for-device

# Run tests
pytest tests/mobile/tests/ -c tests/mobile/pytest.ini
```
