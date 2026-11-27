@visual
Feature: Visual appearance of the logout

  As a logged-in customer
  I want the pages shown after logging out to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Account Logout page looks as expected
    Given the customer is logged in and is on the Account Dashboard
    When the customer logs out using the Account Dashboard side menu
    Then the Account Logout heading matches the visual snapshot
    And the Account Logout messages with the Continue button match the visual snapshot

  Scenario: The ACCOUNT menu of a logged-out customer looks as expected
    Given the customer is logged in and is on the Account Dashboard
    When the customer logs out using the Account Dashboard side menu
    And the customer clicks Continue on the Account Logout page
    And the customer hovers over the ACCOUNT menu
    Then the ACCOUNT menu matches the visual snapshot
