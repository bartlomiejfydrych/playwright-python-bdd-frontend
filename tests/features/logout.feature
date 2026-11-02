@logout
Feature: Logout

  As a logged-in customer
  I want to log out of Automation Test Store
  So that my account is no longer accessible from the current session

  # ==========================================================================================
  # POSITIVE
  # ==========================================================================================

  @positive @smoke
  Scenario Outline: Log out using <method>
    Given the customer is logged in and is on the Account Dashboard
    When the customer logs out using "<method>"
    Then the Account Logout page is displayed with the confirmation messages
    When the customer clicks Continue on the Account Logout page
    Then the home page is displayed in the logged-out state
    When the customer hovers over the ACCOUNT menu
    Then the LOGIN option is displayed in the ACCOUNT menu
    And the LOGOUT option is not displayed in the ACCOUNT menu

    Examples:
      | method                               |
      | Account Dashboard side menu: Logoff  |
      | ACCOUNT menu: LOGOUT                 |
      | welcome message menu: Logoff         |
      | footer: Logoff                       |

  # ==========================================================================================
  # SECURITY
  # ==========================================================================================

  @security
  Scenario: Account pages are not accessible after logging out
    Given the customer is logged in and is on the Account Dashboard
    When the customer logs out using "Account Dashboard side menu: Logoff"
    Then the Account Logout page is displayed with the confirmation messages
    When the customer opens the Account Dashboard directly
    Then the Login page is displayed

  @security
  Scenario: The browser Back button does not bring back the account after logging out
    Given the customer is logged in and is on the Account Dashboard
    When the customer logs out using "Account Dashboard side menu: Logoff"
    Then the Account Logout page is displayed with the confirmation messages
    When the customer goes back in the browser
    Then the Login page is displayed
    And the customer is not logged in
