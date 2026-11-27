@visual
Feature: Visual appearance of the product tags

  As a customer
  I want the product tags and the search results for a tag to look correct
  So that I can see and understand what I am doing in the browser

  Scenario: The Tags tab looks as expected
    Given the user is on the page of the product "Skinsheen Bronzer Stick"
    When the user opens the tags tab
    Then the tags tab matches the visual snapshot

  Scenario: The search results for a tag look as expected
    Given the user is on the page of the product "Skinsheen Bronzer Stick"
    When the user opens the tags tab
    And the user clicks the tag "cheeks"
    Then the search criteria match the visual snapshot
    And the search results grid matches the visual snapshot
