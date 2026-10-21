@account_password
Feature: Change account password

  As a registered customer
  I want to change my account password
  So that I can keep my account secure

  @positive @security
  Scenario: Change password and restore the original password
    Given the customer is logged in and opens Change password from the account dashboard
    When the customer changes the password to a generated new password
    Then the account dashboard confirms the password was successfully updated
    When the customer opens Change password again
    And the customer restores the original password from the environment
    Then the account dashboard confirms the password was successfully updated

  @negative @validation
  Scenario Outline: Reject a password change with invalid input: <case>
    Given the customer is logged in and opens Change password
    When the customer submits the password change with current password "<current>", new password "<new>" and confirmation "<confirm>"
    Then the password change form stays open with an error alert
    And the password change form displays the expected field error for "<error_field>"
    And the password was not changed

    Examples:
      | case                        | current     | new          | confirm          | error_field      |
      | incorrect current password  | __WRONG__   | ValidPass123 | ValidPass123     | current_password |
      | new password too short      | __CURRENT__ | abc          | abc              | password         |
      | new password too long       | __CURRENT__ | __LONG_21__  | __LONG_21__      | password         |
      | confirmation does not match | __CURRENT__ | ValidPass123 | DifferentPass123 | confirm          |
