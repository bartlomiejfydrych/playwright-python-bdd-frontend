@address_book
Feature: Manage address book

  As a registered customer
  I want to manage saved addresses
  So that my delivery and billing details remain correct

  @positive
  Scenario: Add, edit and delete a non-default address
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    And the original address book entries are remembered
    When the customer adds a valid non-default address
    Then the address book confirms the address was successfully inserted
    And the original addresses are unchanged
    And the address book has one more address than before
    And the new address is listed with the entered details
    When the customer edits the new address with different valid details
    Then the address book confirms the address was successfully updated
    And the original addresses are unchanged
    And the address book has one more address than before
    And the updated address is listed with the entered details
    # The store makes an edited address the default one (see the @known_bug scenario), so the original
    # default address has to be restored before the temporary address can be deleted
    When the customer restores the original address as default
    # [CLEANUP] Remove the temporary address
    And the customer deletes the new address
    Then the address book confirms the address was successfully deleted
    And the original addresses are unchanged
    And the address book has the same number of addresses as before
    And the new address is not listed

  @positive
  Scenario: The only saved address remains default when edited to No
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    And the original address book entries are remembered
    And the account has exactly one address
    When the customer edits the only address and sets Default Address to "No"
    And the customer opens the only address for editing again
    Then Default Address is still set to "Yes"

  @positive
  Scenario: A default address cannot be deleted
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    And the original address book entries are remembered
    When the customer adds a valid default address
    Then the address book confirms the address was successfully inserted
    And the new address has no Delete button
    And the original default address has a Delete button
    # [CLEANUP] Restore the original address as default and remove the temporary address
    When the customer restores the original address as default
    And the customer deletes the new address
    Then the address book confirms the address was successfully deleted
    And the new address is not listed
    And the original addresses are unchanged
    And the address book has the same number of addresses as before

  @negative @known_bug
  Scenario: Editing a non-default address keeps it non-default
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    And the original address book entries are remembered
    And the customer has a temporary non-default address
    When the customer edits only the first name of the temporary address
    Then the address book confirms the address was successfully updated
    And the new address has a Delete button
    And the original default address has no Delete button

  @negative @validation
  Scenario Outline: Reject invalid values when adding an address: <case>
    Given the customer is logged in and opens a new address form
    When the customer fills all required address fields with valid values except "<field>" set to "<value>"
    And the customer submits the address form
    Then the address form stays open with an error alert
    And the address form displays the validation error for "<field>"
    And the address was not saved

    Examples:
      | case                   | field     | value        |
      | empty first name       | firstname | __EMPTY__    |
      | first name too long    | firstname | __LONG_33__  |
      | empty last name        | lastname  | __EMPTY__    |
      | last name too long     | lastname  | __LONG_33__  |
      | empty address line     | address_1 | __EMPTY__    |
      | address line too short | address_1 | __SHORT_2__  |
      | address line too long  | address_1 | __LONG_129__ |
      | empty city             | city      | __EMPTY__    |
      | city too short         | city      | __SHORT_2__  |
      | city too long          | city      | __LONG_129__ |
      | empty postcode         | postcode  | __EMPTY__    |
      | postcode too short     | postcode  | __SHORT_1__  |
      | postcode too long      | postcode  | __LONG_11__  |
      | region not selected    | zone_id   | __EMPTY__    |

  @negative @validation
  Scenario Outline: Reject invalid values when editing an address: <case>
    Given the customer is logged in and opens Manage Address Book from the account dashboard
    And the original address book entries are remembered
    And the customer has a temporary non-default address
    When the customer opens the temporary address for editing
    And the customer changes only "<field>" to "<value>"
    And the customer submits the address form
    Then the address form stays open with an error alert
    And the address form displays the validation error for "<field>"
    And the temporary address keeps its original details
    And the original addresses are unchanged

    Examples:
      | case                   | field     | value        |
      | empty first name       | firstname | __EMPTY__    |
      | last name too long     | lastname  | __LONG_33__  |
      | address line too short | address_1 | __SHORT_2__  |
      | city too long          | city      | __LONG_129__ |
      | postcode too short     | postcode  | __SHORT_1__  |
      | region not selected    | zone_id   | __EMPTY__    |
