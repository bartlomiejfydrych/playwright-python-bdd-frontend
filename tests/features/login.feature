Feature: Login page
  As a returning customer
  I want to log in to Automation Test Store
  So that I can access my customer account

  Background:
    Given the user opens the login page

  @positive
  Scenario: Log in with valid credentials
    When the user logs in with the configured credentials
    Then the customer account page is displayed

  @negative
  Scenario Outline: Login is rejected when credentials are invalid or incomplete
    When the user submits login name "<login_name>" and password "<password>"
    Then a login error is displayed
    And the login page remains displayed

    Examples:
      | login_name           | password         |
      | invalid_login_name   | <VALID_PASSWORD> |
      | <VALID_LOGIN_NAME>   | invalid_password |
      | invalid_login_name   | invalid_password |
      | __EMPTY__            | <VALID_PASSWORD> |
      | <VALID_LOGIN_NAME>   | __EMPTY__        |
      | __EMPTY__            | __EMPTY__        |
      | invalid_login_name   | __EMPTY__        |
      | __EMPTY__            | invalid_password |
      | user@invalid.example | invalid_password |
      | !@#$%^&*()           | invalid_password |
      | whitespace_login     | __EMPTY__        |

  @ui
  Scenario: Login page displays the expected form elements
    Then the login page is displayed
    And the returning customer form is visible
    And the login name and password fields are visible
    And the login button is visible
    And the password recovery links are visible
    And the new customer registration form is visible

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
