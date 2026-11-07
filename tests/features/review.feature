@review
Feature: Product reviews

  As a customer
  I want to submit a product review
  So that I can share my opinion about a product

  Background:
    Given the user opens the store home page for review testing

  # ==========================================================================================================
  # NEGATIVE: CAPTCHA verification
  # ==========================================================================================================

  @negative @captcha
  Scenario: Do not submit a review when CAPTCHA verification fails
    When the user opens the product "Skinsheen Bronzer Stick"
    And the user opens the reviews tab
    And the user submits an empty review
    Then the review form shows the error message "Human verification has failed! Please try again."