@account_password
Feature: Change account password

  As a registered customer
  I want to change my account password
  So that I can keep my account secure

  # [CLEANUP] The positive scenario restores the original password from .env in its last steps.
  # Additionally a fixture (steps file) restores it even when the scenario fails halfway.

  @positive @security
  Scenario: Change password and restore the original password
    Given the customer is logged in and opens Change password from the account dashboard
    When the customer changes the password to a generated new password
    Then the account dashboard confirms the password was successfully updated
    And the customer can log in with the new password
    # [CLEANUP]
    When the customer opens Change password again
    And the customer restores the original password from the environment
    Then the account dashboard confirms the password was successfully updated
    And the customer can log in with the original password

  @negative @validation
  Scenario Outline: Reject a password change with invalid input: <case>
    Given the customer is logged in and opens Change password
    When the customer submits the password change with current password "<current>", new password "<new>" and confirmation "<confirm>"
    Then the password change form stays open with an error alert
    And the password change form displays the error "<message>" for "<field>"
    And the customer can log in with the original password

    Examples:
      | case                        | current     | new          | confirm          | field            | message                                               |
      | incorrect current password  | __WRONG__   | ValidPass123 | ValidPass123     | current_password | Your current password is incorrect! Please try again. |
      | empty current password      | __EMPTY__   | ValidPass123 | ValidPass123     | current_password | Your current password is incorrect! Please try again. |
      | new password too short      | __CURRENT__ | abc          | abc              | password         | Password must be between 4 and 20 characters!         |
      | new password too long       | __CURRENT__ | __LONG_21__  | __LONG_21__      | password         | Password must be between 4 and 20 characters!         |
      | empty new password          | __CURRENT__ | __EMPTY__    | __EMPTY__        | password         | Password must be between 4 and 20 characters!         |
      | confirmation does not match | __CURRENT__ | ValidPass123 | DifferentPass123 | confirm          | Password confirmation does not match password!        |
