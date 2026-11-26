@visual
Feature: Visual appearance of the Edit account details page

  As a registered customer
  I want the Edit account details page to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Edit account details form looks as expected
    Given the customer is logged in and opens Edit account details
    When the customer fills the account details form with fixed values
    Then the Edit account details form matches the visual snapshot

  Scenario: The validation errors look as expected
    Given the customer is logged in and opens Edit account details
    When the customer fills the account details form with fixed values
    And the customer breaks the first name, last name and e-mail
    And the customer submits the account details form
    Then the account details error alert matches the visual snapshot
    And the Edit account details form with the validation errors matches the visual snapshot
