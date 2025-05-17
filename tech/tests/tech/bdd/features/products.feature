Feature: Product Management
  As an administrator
  I want to manage products
  So that customers can browse and purchase them

  Background:
    Given the system has a registered admin user with login credentials
    And the administrator is authenticated
    And the system has the following categories
      | category        |
      | Lanche          |
      | Acompanhamento  |
      | Bebida          |
      | Sobremesa       |

  Scenario: Admin creates a new product
    When the admin creates a new product with the following details
      | name     | price   | category  |
      | Smart TV | 1299.99 | Lanche    |
    Then the product "Smart TV" should be successfully created
    And the response should include the product ID
    And the product "Smart TV" should be available in the "Lanche" category

  Scenario: Admin updates an existing product
    Given the system has the following products
      | name       | price  | category  |
      | Smartphone | 999.99 | Lanche    |
    When the admin updates the "Smartphone" product with the following details
      | name          | price   | category        |
      | Premium Phone | 1199.99 | Acompanhamento  |
    Then the product should be successfully updated
    And the product's name should be "Premium Phone"
    And the product's price should be 1199.99

  Scenario: Admin deletes a product
    Given the system has the following products
      | name       | price | category |
      | Old Gadget | 49.99 | Bebida   |
    When the admin deletes the product "Old Gadget"
    Then the product should be successfully deleted
    And the product "Old Gadget" should no longer be available

  Scenario: Listing products by category
    Given the system has the following products
      | name    | price  | category       |
      | T-shirt | 19.99  | Sobremesa      |
      | Jeans   | 39.99  | Sobremesa      |
      | Laptop  | 899.99 | Acompanhamento |
    When a user requests products in the "Sobremesa" category
    Then the response should include 2 products
    And the response should include "T-shirt" and "Jeans"
    And the response should not include "Laptop"

  Scenario: Listing all products
    Given the system has the following products
      | name   | price  | category       |
      | Apple  | 0.99   | Lanche         |
      | Bread  | 2.99   | Bebida         |
      | Tablet | 299.99 | Acompanhamento |
    When a user requests all products
    Then the response should include 3 products
    And the response should include "Apple", "Bread", and "Tablet"

  Scenario: Non-admin user cannot create a product
    Given the system has a registered regular user with login credentials
    And the regular user is authenticated
    When the regular user tries to create a new product
    Then the operation should be denied with a 403 error

  Scenario: Attempting to create a product with a duplicate name
    Given the system has the following products
      | name         | price | category  |
      | Coffee Maker | 79.99 | Lanche    |
    When the admin creates a new product with the following details
      | name         | price | category  |
      | Coffee Maker | 89.99 | Lanche    |
    Then the operation should fail with a 400 error
    And the error message should contain "Product already exists"