@logout
Feature: Logout

  As a logged-in customer
  I want to log out of Automation Test Store
  So that my account is no longer accessible from the current session

  # Authentication is performed through the existing API-backed `logged_in_page` fixture.
  # The scenarios below focus on the logout UI and its navigation.

  @positive @smoke
  Scenario: Log out using Logoff on the Account Dashboard
    Given the customer is logged in and is on the Account Dashboard
    When the customer clicks Logoff in the Account Dashboard side menu
    Then the Account Logout page is displayed with the confirmation messages
    When the customer clicks Continue on the Account Logout page
    Then the home page is displayed in the logged-out state
    When the customer hovers over the ACCOUNT menu
    Then the LOGIN option is displayed in the ACCOUNT menu

  @positive
  Scenario: Log out using LOGOUT in the ACCOUNT menu
    Given the customer is logged in and is on the Account Dashboard
    When the customer clicks LOGOUT in the ACCOUNT menu
    Then the Account Logout page is displayed with the confirmation messages
    When the customer clicks Continue on the Account Logout page
    Then the home page is displayed in the logged-out state
    When the customer hovers over the ACCOUNT menu
    Then the LOGIN option is displayed in the ACCOUNT menu