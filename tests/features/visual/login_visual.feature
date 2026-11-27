@visual
Feature: Visual appearance of the Login page

  As a customer
  I want the Login page to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Login page looks as expected
    Given the user opens the login page
    Then the returning customer section matches the visual snapshot
    And the new customer section matches the visual snapshot

  Scenario: The login error looks as expected
    Given the user opens the login page
    When the user submits the fixed wrong credentials
    Then the login error alert matches the visual snapshot
    And the returning customer section with the login error matches the visual snapshot
