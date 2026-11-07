@review
Feature: Product reviews

  As a customer
  I want to submit a product review
  So that I can share my opinion about a product

  Background:
    Given the user opens the home page

  # ==========================================================================================================
  # NEGATIVE: CAPTCHA verification
  # ==========================================================================================================

  @negative @captcha
  Scenario: Do not submit an empty review form
    When the user opens the featured product "Skinsheen Bronzer Stick"
    And the user opens the reviews tab
    And the user submits the review form
    Then the review form shows the error message "Human verification has failed! Please try again."
    And the product still has no reviews

  @negative @captcha
  Scenario: Do not submit a review with valid data and a wrong CAPTCHA code
    When the user opens the featured product "Skinsheen Bronzer Stick"
    And the user opens the reviews tab
    And the user fills in the review form with name "Test User", rating 5, text "This is a long enough review text for the validation." and CAPTCHA code "xxxxx"
    And the user submits the review form
    Then the review form shows the error message "Human verification has failed! Please try again."
    And the product still has no reviews