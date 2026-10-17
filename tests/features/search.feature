@search
Feature: Product search

  As a customer
  I want to search for products
  So that I can find products matching my search criteria

  Background:
    Given the user opens the home page

  # ==========================================================================================================
  # POSITIVE
  # ==========================================================================================================

  @positive @smoke
  Scenario: Find a product by its full name without selecting a category
    When the user searches for "Curls to straight Shampoo"
    Then the user is taken to the page of the product "Curls to straight Shampoo"

  @positive
  Scenario: Find a product by its full name within its category
    When the user searches for "Curls to straight Shampoo" in category "Hair Care"
    Then the user is taken to the page of the product "Curls to straight Shampoo"

  @positive
  Scenario: Find a product by a partial name
    When the user searches for "Curls to straight"
    Then the user is taken to the page of the product "Curls to straight Shampoo"

  @positive
  Scenario: Find products by a common keyword
    When the user searches for "Shampoo"
    Then at least 2 products are displayed in the search results
    And the product "Curls to straight Shampoo" is displayed in the search results

  @positive
  Scenario: Find a product using the Enter key
    When the user searches for "Curls to straight Shampoo" using Enter
    Then the user is taken to the page of the product "Curls to straight Shampoo"

  # ==========================================================================================================
  # NEGATIVE: category filtering
  # ==========================================================================================================

  @negative
  Scenario Outline: Do not find a product outside the selected category
    When the user searches for "Curls to straight Shampoo" in category "<category>"
    Then the product "Curls to straight Shampoo" is not displayed in the search results

    Examples:
      | category |
      | Makeup   |
      | Skincare |
      | Men      |
      | Books    |

  # ==========================================================================================================
  # NEGATIVE: no matching products
  # ==========================================================================================================

  @negative
  Scenario: No products are found for a nonexistent product name
    When the user searches for "NonexistentProduct123456"
    Then no products are displayed in the search results
    And the search results page shows the message "There is no product that matches the search criteria."
