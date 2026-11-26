@visual
Feature: Visual appearance of the Contact Us page

  As a customer
  I want the Contact Us page to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Contact Us form looks as expected
    Given the customer is logged in and opens the Contact Us page
    Then the Contact Us form matches the visual snapshot

  Scenario: The validation errors look as expected
    Given the customer is logged in and opens the Contact Us page
    When the customer submits the enquiry
    Then the Contact Us form with the validation errors matches the visual snapshot

  Scenario: The enquiry success page looks as expected
    Given the customer is logged in and opens the Contact Us page
    When the customer fills in the Contact Us form with fixed data
    And the customer submits the enquiry
    Then the enquiry success page matches the visual snapshot