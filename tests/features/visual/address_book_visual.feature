@visual
Feature: Visual appearance of the address book

  As a registered customer
  I want the address book pages to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The new address form looks as expected
    Given the customer is logged in and opens a new address form
    Then the new address form matches the visual snapshot

  Scenario: The validation error looks as expected
    Given the customer is logged in and opens a new address form
    When the customer submits the address form with an empty first name
    Then the validation error alert matches the visual snapshot
    And the address form with the validation error matches the visual snapshot

  Scenario: A new address entry looks as expected
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    When the customer adds a valid non-default address
    Then the address book confirms the address was successfully inserted
    And the new address entry matches the visual snapshot
    # [CLEANUP] Remove the temporary address
    When the customer deletes the new address
    Then the address book confirms the address was successfully deleted
