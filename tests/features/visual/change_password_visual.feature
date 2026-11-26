@visual
Feature: Visual appearance of the Change password page

  As a registered customer
  I want the Change password page to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Change password form looks as expected
    Given the customer is logged in and opens Change password
    Then the Change password form matches the visual snapshot

  Scenario: The validation errors look as expected
    Given the customer is logged in and opens Change password
    When the customer submits the empty Change password form
    Then the password change error alert matches the visual snapshot
    And the Change password form with the validation errors matches the visual snapshot
