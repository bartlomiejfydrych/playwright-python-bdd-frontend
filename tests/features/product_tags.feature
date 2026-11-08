@product_tags
Feature: Product tags

  As a customer
  I want to use the tags assigned to a product
  So that I can find other products related to the same tag

  Background:
    Given the user opens the home page

  @positive @navigation
  Scenario: Clicking a product tag shows the products assigned to that tag
    When the user opens the featured product "Skinsheen Bronzer Stick"
    And the user opens the tags tab
    And the user clicks the tag "cheeks"
    Then the search criteria contain "cheeks"
    And only the following products are displayed in the search results
      | product_name             |
      | Skinsheen Bronzer Stick  |
      | BeneFit Girl Meets Pearl |