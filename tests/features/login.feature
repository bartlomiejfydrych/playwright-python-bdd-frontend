Feature: Login page

  As a returning customer
  I want to log in to Automation Test Store
  So that I can access my customer account

  # Tokens used in Examples tables (resolved in steps/test_login.py):
  #   __VALID_LOGIN_NAME__      - login name from .env
  #   __VALID_PASSWORD__        - password from .env
  #   __VALID_PASSWORD_UPPER__  - valid password with changed case (password is case-sensitive)
  #   __EMPTY__                 - empty string (pytest-bdd cannot match "" in a quoted parameter)
  #   __SPACES__                - three spaces
  #   __LONG_1000__             - 1000 characters
  #
  # NOTE: lines with __VALID_LOGIN_NAME__ + bad password may count towards the login attempt limit
  # on a real test account. If the store enforces it, use a separate account.

  Background:
    Given the user opens the login page

  # ==========================================================================================================
  # POSITIVE
  # ==========================================================================================================

  @positive @smoke
  Scenario: Log in with valid credentials
    When the user logs in with the configured credentials
    Then the customer account page is displayed
    And the logoff link is available

  # ==========================================================================================================
  # NEGATIVE: wrong credentials
  # ==========================================================================================================

  @negative
  Scenario Outline: Login is rejected for wrong credentials
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login error informs about incorrect login or password
    And the login page remains displayed

    Examples:
      | login_name           | password                 |
      | wrong_login_name     | __VALID_PASSWORD__       |
      | __VALID_LOGIN_NAME__ | wrong_password           |
      | wrong_login_name     | wrong_password           |
      | user@invalid.example | wrong_password           |
      | __VALID_LOGIN_NAME__ | __VALID_PASSWORD_UPPER__ |

  # ==========================================================================================================
  # NEGATIVE: missing / blank input
  # ==========================================================================================================

  @negative @validation
  Scenario Outline: Login is rejected when a required field is empty
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login page remains displayed

    Examples:
      | login_name           | password           |
      | __EMPTY__            | __VALID_PASSWORD__ |
      | __VALID_LOGIN_NAME__ | __EMPTY__          |
      | __EMPTY__            | __EMPTY__          |

  @negative @validation
  Scenario Outline: Login is rejected when a field contains only spaces
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login page remains displayed

    Examples:
      | login_name           | password           |
      | __SPACES__           | __VALID_PASSWORD__ |
      | __VALID_LOGIN_NAME__ | __SPACES__         |
      | __SPACES__           | __SPACES__         |

  # ==========================================================================================================
  # NEGATIVE: special characters, unicode, very long values
  # ==========================================================================================================

  @negative @validation
  Scenario Outline: Login is rejected for special characters, unicode and very long values
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login page remains displayed

    Examples:
      | login_name       | password       |
      | !@#$%^&*()       | wrong_password |
      | wrong_login_name | !@#$%^&*()     |
      | zażółć_gęślą     | jaźń_123       |
      | __LONG_1000__    | wrong_password |
      | wrong_login_name | __LONG_1000__  |
      | __LONG_1000__    | __LONG_1000__  |

  # ==========================================================================================================
  # NEGATIVE: security
  # ==========================================================================================================

  @negative @security
  Scenario Outline: Login is not vulnerable to injection payloads
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login page remains displayed
    And no JavaScript dialog was triggered

    Examples:
      | login_name                   | password                  |
      | ' OR '1'='1                  | ' OR '1'='1               |
      | admin'--                     | wrong_password            |
      | <script>alert(1)</script>    | wrong_password            |
      | wrong_login_name             | <script>alert(1)</script> |
      | <img src=x onerror=alert(1)> | wrong_password            |

  @negative @security
  Scenario: Credentials are not exposed in the URL after a failed login
    When the user submits login name "secret_login" and password "secret_password_123"
    Then a login error is displayed
    And the URL does not contain "secret_login"
    And the URL does not contain "secret_password_123"

  @negative @security
  Scenario: Failed login does not grant access to My Account
    When the user submits login name "wrong_login_name" and password "wrong_password"
    And the user opens the My Account page directly
    Then the login page is displayed

  @negative @security
  Scenario: Guest is redirected to the login page when opening My Account
    When the user opens the My Account page directly
    Then the login page is displayed

  @negative @usability
  Scenario: Pressing Enter in the password field submits the login form
    When the user types login name "wrong_login_name" and password "wrong_password" and presses Enter
    Then a login error is displayed
    And the login page remains displayed

  # ==========================================================================================================
  # UI
  # ==========================================================================================================

  @ui
  Scenario: Login page displays the expected form elements
    Then the login page is displayed
    And the returning customer form is visible
    And the login name and password fields are visible
    And the login fields are empty
    And the login button is visible
    And the login form uses POST and contains a CSRF token
    And the password recovery links are visible
    And the new customer registration form is visible
    And the register account option is selected by default

  @ui
  Scenario: Breadcrumb shows the path to the login page
    Then the breadcrumb trail is "Home > Register Account > Login"

  # ==========================================================================================================
  # NAVIGATION
  # ==========================================================================================================

  @navigation
  Scenario: User can open password recovery
    When the user opens password recovery
    Then the password recovery page is displayed

  @navigation
  Scenario: User can open login name recovery
    When the user opens login name recovery
    Then the login name recovery page is displayed

  @navigation
  Scenario: User can start account registration
    When the user starts account registration
    Then the account registration page is displayed

  @navigation
  Scenario: Home breadcrumb leads to the home page
    When the user clicks the Home breadcrumb
    Then the home page is displayed
