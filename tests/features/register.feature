Feature: Registration of a new customer
  As a new customer
  I want to create an account in the shop
  So that I can log in and place orders

  Background:
    Given the registration page is open

  # ==========================================================================================
  # POSITIVE (only one - the whole form filled in)
  # ==========================================================================================

  Scenario: Register a new account with the whole form filled in
    When I fill in the required fields with valid data
    And I fill in the optional fields with valid data
    And I subscribe to the newsletter
    And I accept the privacy policy
    And I click Continue
    Then the account created page is displayed

  # ==========================================================================================
  # NEGATIVE: empty form / privacy policy
  # ==========================================================================================

  Scenario: Submit an empty form with the privacy policy accepted
    When I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And errors are shown under all required fields
    And all required field errors are also listed in the alert

  Scenario: Submit an empty form without accepting the privacy policy
    When I click Continue
    Then I stay on the registration page
    And the privacy policy error is shown
    And errors are shown under all required fields

  Scenario: Submit a valid form without accepting the privacy policy
    When I fill in the required fields with valid data
    And I click Continue
    Then I stay on the registration page
    And the privacy policy error is shown
    And no field errors are shown

  # ==========================================================================================
  # NEGATIVE: required fields
  # ==========================================================================================

  Scenario Outline: Submit the form with one required field left empty
    When I fill in the required fields with valid data
    And I leave the "<field>" field empty
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the "<field>" field shows its validation error
    And only the "<field>" field has an error

    Examples:
      | field         |
      | First Name    |
      | Last Name     |
      | E-Mail        |
      | Address 1     |
      | City          |
      | Region / State|
      | ZIP Code      |
      | Login name    |
      | Password      |

  # ==========================================================================================
  # NEGATIVE: field formats and length limits
  # ==========================================================================================

  Scenario Outline: Submit the form with an invalid e-mail address
    When I fill in the required fields with valid data
    And I set the "E-Mail" field to "<email>"
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the "E-Mail" field shows its validation error
    And only the "E-Mail" field has an error

    Examples:
      | email            |
      | plainaddress     |
      | user@            |
      | @example.com     |
      | user@@example.com|
      | user@example,com |

  Scenario Outline: Submit the form with a value outside the allowed length
    When I fill in the required fields with valid data
    And I set the "<field>" field to a value of <length> characters
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the "<field>" field shows its validation error
    And only the "<field>" field has an error

    Examples:
      | field      | length |
      | First Name | 33     |
      | Last Name  | 33     |
      | Address 1  | 2      |
      | Address 1  | 129    |
      | City       | 2      |
      | City       | 129    |
      | ZIP Code   | 2      |
      | Login name | 4      |
      | Login name | 65     |
      | Password   | 3      |
      | Password   | 21     |

  Scenario Outline: Submit the form with forbidden characters in the login name
    When I fill in the required fields with valid data
    And I set the "Login name" field to "<login_name>"
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the "Login name" field shows its validation error
    And only the "Login name" field has an error

    Examples:
      | login_name   |
      | user name    |
      | user@name    |
      | user!name    |
      | użytkownik   |

  Scenario: Submit the form with a password confirmation that does not match
    When I fill in the required fields with valid data
    And I set the "Password Confirm" field to "DifferentPass1"
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the error alert contains "Password confirmation does not match password!"
    And only the "Password Confirm" field has an error

  # ==========================================================================================
  # NEGATIVE: data already used by another account
  # (the existing account is the one from .env - ACCOUNT_E_MAIL / ACCOUNT_LOGIN_NAME)
  # (messages below are my best guess of AbanteCart texts - verify on the first run)
  # ==========================================================================================

  Scenario: Register with an e-mail address that is already registered
    When I fill in the required fields with valid data
    And I use the e-mail address of the existing account
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the error alert contains "already registered"

  Scenario: Register with a login name that is already taken
    When I fill in the required fields with valid data
    And I use the login name of the existing account
    And I accept the privacy policy
    And I click Continue
    Then I stay on the registration page
    And the error alert contains "not available"

  # ==========================================================================================
  # FORM BEHAVIOUR (no submit)
  # ==========================================================================================

  Scenario: Open and close the privacy policy window
    When I open the privacy policy
    Then the privacy policy window is displayed
    When I close the privacy policy
    Then the privacy policy window is not displayed

  Scenario: Go to the login page from the registration page
    When I click the login page link
    Then the login page is displayed

  Scenario: Regions are reloaded after changing the country
    When I select the country "United Kingdom"
    Then the region list contains "Greater London"
    When I select the country "Poland"
    Then the region list does not contain "Greater London"
