@account_edit
Feature: Edit account details

  As a registered customer
  I want to edit my personal details
  So that my account information stays up to date

  # [CLEANUP] After each positive scenario the original data from .env is restored (fixture in the steps file).

  @positive
  Scenario: Update all editable account details and restore the original data
    Given the customer is logged in and opens Edit account details from the account dashboard
    When the customer changes all editable account details to new values
    And the customer submits the account details form
    Then the account dashboard confirms the account was successfully updated
    When the customer opens Edit account details again
    Then the updated account details are displayed
    And the login name remains unchanged

  @positive
  Scenario: Clear the optional telephone and fax and restore the original data
    Given the customer is logged in and opens Edit account details from the account dashboard
    When the customer clears the optional telephone and fax
    And the customer submits the account details form
    Then the account dashboard confirms the account was successfully updated
    When the customer opens Edit account details again
    Then the telephone and fax fields are empty
    And the first name, last name and e-mail are unchanged

  @negative @validation
  Scenario Outline: Reject invalid first name: <case>
    Given the customer is logged in and opens Edit account details
    When the customer sets the first name to "<value>"
    And the customer submits the account details form
    Then the account details form displays a validation error for "firstname"
    And the account details form stays open with an error alert
    And the account details were not saved

    Examples:
      | case                 | value       |
      | empty                | __EMPTY__   |
      | longer than 32 chars | __LONG_33__ |

  @negative @validation
  Scenario Outline: Reject invalid last name: <case>
    Given the customer is logged in and opens Edit account details
    When the customer sets the last name to "<value>"
    And the customer submits the account details form
    Then the account details form displays a validation error for "lastname"
    And the account details form stays open with an error alert
    And the account details were not saved

    Examples:
      | case                 | value       |
      | empty                | __EMPTY__   |
      | longer than 32 chars | __LONG_33__ |

  @negative @validation
  Scenario Outline: Reject invalid e-mail address: <case>
    Given the customer is logged in and opens Edit account details
    When the customer sets the e-mail to "<value>"
    And the customer submits the account details form
    Then the account details form displays a validation error for "email"
    And the account details form stays open with an error alert
    And the account details were not saved

    Examples:
      | case             | value               |
      | empty            | __EMPTY__           |
      | missing at sign  | invalid.example.com |
      | missing domain   | invalid@            |
      | missing username | @example.com        |
