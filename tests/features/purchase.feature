@purchase @e2e
Feature: Complete purchase

  As a logged-in customer
  I want to add products to my basket and complete an order
  So that I can verify the complete purchase process

  @positive @smoke
  Scenario: Purchase multiple products, remove one, confirm the order and verify the empty basket
    Given the customer is logged in and has an empty basket

    When the customer adds 3 units of "Skinsheen Bronzer Stick" to the basket
    Then the basket contains 1 product row with:
      | product                 | quantity | line total |
      | Skinsheen Bronzer Stick | 3        | 83.07€     |
    And the basket totals are Sub-Total "83.07€", Shipping "1.88€" and Total "84.95€"

    When the customer adds 1 unit of "BeneFit Girl Meets Pearl" to the basket
    Then the basket contains 2 product rows with:
      | product                 | quantity | line total |
      | Skinsheen Bronzer Stick | 3        | 83.07€     |
      | BeneFit Girl Meets Pearl | 1        | 17.83€     |
    And the basket totals are Sub-Total "100.90€", Shipping "1.88€" and Total "102.78€"

    When the customer adds 2 units of "Benefit Bella Bamba" to the basket
    Then the basket contains 3 product rows with:
      | product                 | quantity | line total |
      | Skinsheen Bronzer Stick | 3        | 83.07€     |
      | BeneFit Girl Meets Pearl | 1        | 17.83€     |
      | Benefit Bella Bamba      | 2        | 52.56€     |
    And the basket totals are Sub-Total "153.46€", Shipping "1.88€" and Total "155.34€"

    When the customer removes "BeneFit Girl Meets Pearl" from the basket
    Then the basket contains 2 product rows with:
      | product                 | quantity | line total |
      | Skinsheen Bronzer Stick | 3        | 83.07€     |
      | Benefit Bella Bamba      | 2        | 52.56€     |
    And the basket totals are Sub-Total "135.63€", Shipping "1.88€" and Total "137.51€"

    When the customer proceeds to checkout
    Then the checkout confirmation contains the expected shipping and payment details
    And the checkout confirmation contains these products:
      | product                 | unit price | quantity | line total |
      | Skinsheen Bronzer Stick | 27.69€     | 3        | 83.07€     |
      | Benefit Bella Bamba      | 26.28€     | 2        | 52.56€     |
    And the checkout confirmation totals are Sub-Total "135.63€", Shipping "1.88€" and Total "137.51€"
    And the order summary contains these products:
      | product                 | unit price | quantity |
      | Skinsheen Bronzer Stick | 27.69€     | 3        |
      | Benefit Bella Bamba      | 26.28€     | 2        |

    When the customer confirms the order
    Then the order success page confirms that the order has been processed

    When the customer continues shopping
    Then the home page is displayed
    When the customer opens the basket
    Then the basket is empty
