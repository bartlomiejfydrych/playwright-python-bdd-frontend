@contact_us
Feature: Contact the store owner
  As a customer
  I want to send an enquiry to the store owner
  So that I can ask questions about the store

  Background:
    Given the customer is logged in and opens the Contact Us page

  # ==========================================================================================
  # POSITIVE
  # ==========================================================================================

  @positive @smoke
  Scenario: Send an enquiry with all fields filled in correctly
    Then the store address and telephone number are correct
    When the customer fills in the Contact Us form with valid data
    And the customer submits the enquiry
    Then the enquiry success page is displayed

  @positive
  Scenario: Reset a filled-in Contact Us form
    Then the store address and telephone number are correct
    When the customer fills in the Contact Us form with valid data
    Then the Contact Us form contains the entered data
    When the customer resets the form
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
    And only the "<field>" field shows the required field error

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
    And only the "Email" field shows the invalid value error

    Examples:
      | email             |
      | plainaddress      |
      | user@             |
      | @example.com      |
      | user@@example.com |

  @negative @validation
  Scenario Outline: Submit the Contact Us form with a first name outside the allowed length
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "First name" field to a value of <length> characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And only the "First name" field shows the invalid value error

    Examples:
      | length |
      | 2      |

  @negative @validation
  Scenario Outline: Submit the Contact Us form with an enquiry outside the allowed length
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "Enquiry" field to a value of <length> characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And only the "Enquiry" field shows the invalid value error

    Examples:
      | length |
      | 3001   |

  # ==========================================================================================
  # KNOWN BUGS: the store accepts these values and sends the enquiry (success page)
  # ==========================================================================================

  @negative @validation @known_bug
  Scenario: Reject an email address with a comma instead of a dot
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "Email" field to "user@example,com"
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And only the "Email" field shows the invalid value error

  @negative @validation @known_bug
  Scenario: Reject a first name longer than 32 characters
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "First name" field to a value of 33 characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And only the "First name" field shows the invalid value error

  @negative @validation @known_bug
  Scenario: Reject an enquiry shorter than 10 characters
    When the customer fills in the Contact Us form with valid data
    And the customer sets the "Enquiry" field to a value of 9 characters
    And the customer submits the enquiry
    Then the Contact Us form remains open
    And only the "Enquiry" field shows the invalid value error