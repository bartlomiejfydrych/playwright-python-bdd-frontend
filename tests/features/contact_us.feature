@contact_us
Feature: Contact the store owner
  As a customer
  I want to send an enquiry to the store owner
  So that I can ask questions about the store

  Background:
    Given the customer is logged in and opens the Contact Us page
    Then the store address and telephone number are correct

  # ==========================================================================================
  # POSITIVE
  # ==========================================================================================

  @positive @smoke
  Scenario: Send an enquiry with all fields filled in correctly
    When the customer fills in the Contact Us form with valid data
    And the customer submits the enquiry
    Then the enquiry success page is displayed

  @positive
  Scenario: Reset a filled-in Contact Us form
    When the customer fills in the Contact Us form with valid data
    And the customer resets the form
    Then all Contact Us form fields are empty

  # ==========================================================================================
  # NEGATIVE: required fields
  # ==========================================================================================

  @negative @validation
  Scenario: Submit the Contact Us form with all fields empty
    When the customer submits the enquiry
    Then the Contact Us form remains open
    And validation errors are displayed for all fields

  @negative @validation
  Scenario Outline: Submit the Contact Us form with one required field empty
    When the customer fills in the Contact Us form with valid data
    And the customer clears the "<field>" field
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And a validation error is displayed for the "<field>" field

    Examples:
      | field      |
      | First name |
      | Email      |
      | Enquiry    |

  # ==========================================================================================
  # NEGATIVE: invalid formats and length limits
  # ==========================================================================================

  @negative @validation
  Scenario Outline: Submit the Contact Us form with an invalid email address
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "Email" field to "<email>"
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And a validation error is displayed for the "Email" field

    Examples:
      | email             |
      | plainaddress      |
      | user@             |
      | @example.com      |
      | user@@example.com |
      | user@example,com  |

  @negative @validation
  Scenario Outline: Submit the Contact Us form with a first name outside the allowed length
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "First name" field to a value of <length> characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And a validation error is displayed for the "First name" field

    Examples:
      | length |
      | 2      |
      | 33     |

  @negative @validation
  Scenario Outline: Submit the Contact Us form with an enquiry outside the allowed length
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "Enquiry" field to a value of <length> characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And a validation error is displayed for the "Enquiry" field

    Examples:
      | length |
      | 9      |
      | 3001   |
