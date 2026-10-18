@wishlist
Feature: Product wish list

  As a logged-in customer
  I want to manage my wish list
  So that I can save products and move them to the shopping cart

  @positive
  Scenario: Manage the wish list and move a product to the cart
    Given the customer is logged in and opens the home page
    And the wish list and shopping cart are empty
    When the customer adds the first 3 featured products to the wish list
    And the customer goes to My Account
    Then the wish list counter should be 3
    When the customer opens the wish list
    Then the wish list should contain all 3 selected products
    When the customer removes the first selected product from the wish list
    Then the first selected product should not be in the wish list
    And the wish list should contain the 2 remaining selected products
    When the customer adds the second selected product to the shopping cart from the wish list
    Then the shopping cart page should be displayed
    And the shopping cart should contain the second selected product
    When the customer removes the second selected product from the shopping cart
    And the customer goes to My Account
    Then the wish list counter should be 2
    When the customer opens the wish list
    Then the wish list should contain the 2 remaining selected products
    When the customer removes the 2 remaining selected products from the wish list
    Then the wish list should be empty