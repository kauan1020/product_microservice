# tests/unit/infra/repositories/test_mongodb_product_repository.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from tech.domain.entities.products import Products
from tech.infra.repositories.mongodb_product_repository import MongoDBProductRepository


class TestMongoDBProductRepository:
    """Unit tests for the MongoDBProductRepository."""

    def setup_method(self):
        """Set up test dependencies."""
        # Mock the MongoDB collection
        self.mock_collection = Mock()

        # Patch the get_collection function to return our mock
        self.get_collection_patch = patch('tech.infra.repositories.mongodb_product_repository.get_collection')
        self.mock_get_collection = self.get_collection_patch.start()
        self.mock_get_collection.return_value = self.mock_collection

        # Create the repository instance
        self.repository = MongoDBProductRepository()

        # Verify get_collection was called with correct collection name
        self.mock_get_collection.assert_called_once_with('products')

        # Create a test product
        self.test_product = Products(
            id=None,
            name="Test Product",
            price=10.99,
            category="test_category"
        )

        # Test product with ID
        self.existing_product = Products(
            id=1,
            name="Existing Product",
            price=15.99,
            category="existing_category",
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 1)
        )

    def teardown_method(self):
        """Clean up after tests."""
        self.get_collection_patch.stop()

    def test_generate_id_no_products(self):
        """Test ID generation when no products exist."""
        # Arrange
        self.mock_collection.find_one.return_value = None

        # Act
        result = self.repository._generate_id()

        # Assert
        assert result == 1
        self.mock_collection.find_one.assert_called_once()

    def test_generate_id_with_existing_products(self):
        """Test ID generation when products exist."""
        # Arrange
        highest_id_product = {"product_id": 5}
        self.mock_collection.find_one.return_value = highest_id_product

        # Act
        result = self.repository._generate_id()

        # Assert
        assert result == 6
        self.mock_collection.find_one.assert_called_once()

    def test_add_new_product(self):
        """Test adding a new product."""
        # Arrange
        self.mock_collection.find_one.return_value = None  # No existing product with same ID
        self.mock_collection.insert_one.return_value = Mock()

        # Act
        result = self.repository.add(self.test_product)

        # Assert
        self.mock_collection.insert_one.assert_called_once()

        # Verify the product dict passed to insert_one
        product_dict = self.mock_collection.insert_one.call_args[0][0]
        assert product_dict["product_id"] == 1  # Generated ID
        assert product_dict["name"] == "Test Product"
        assert product_dict["price"] == 10.99
        assert product_dict["category"] == "test_category"
        assert "created_at" in product_dict
        assert "updated_at" in product_dict

        # Verify the returned product
        assert isinstance(result, Products)
        assert result.id == 1
        assert result.name == "Test Product"
        assert result.price == 10.99
        assert result.category == "test_category"

    def test_get_by_id_found(self):
        """Test retrieving a product by ID when found."""
        # Arrange
        product_id = 1
        mock_doc = {
            "product_id": product_id,
            "name": "Test Product",
            "price": 10.99,
            "category": "test_category",
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime(2023, 1, 1)
        }
        self.mock_collection.find_one.return_value = mock_doc

        # Act
        result = self.repository.get_by_id(product_id)

        # Assert
        self.mock_collection.find_one.assert_called_once_with({"product_id": product_id})
        assert isinstance(result, Products)
        assert result.id == product_id
        assert result.name == "Test Product"
        assert result.price == 10.99
        assert result.category == "test_category"
        assert result.created_at == datetime(2023, 1, 1)
        assert result.updated_at == datetime(2023, 1, 1)

    def test_get_by_id_not_found(self):
        """Test retrieving a product by ID when not found."""
        # Arrange
        product_id = 999
        self.mock_collection.find_one.return_value = None

        # Act
        result = self.repository.get_by_id(product_id)

        # Assert
        self.mock_collection.find_one.assert_called_once_with({"product_id": product_id})
        assert result is None

    def test_get_by_id_with_string_id(self):
        """Test retrieving a product by ID when ID is a string."""
        # Arrange
        product_id = "1"  # String ID
        expected_int_id = 1
        mock_doc = {
            "product_id": expected_int_id,
            "name": "Test Product",
            "price": 10.99,
            "category": "test_category"
        }
        self.mock_collection.find_one.return_value = mock_doc

        # Act
        result = self.repository.get_by_id(product_id)

        # Assert
        self.mock_collection.find_one.assert_called_once_with({"product_id": expected_int_id})
        assert result.id == expected_int_id

    def test_get_by_id_exception_handling(self):
        """Test exception handling in get_by_id."""
        # Arrange
        product_id = 1
        self.mock_collection.find_one.side_effect = Exception("Database error")

        # Act
        result = self.repository.get_by_id(product_id)

        # Assert
        assert result is None

    def test_get_by_name_found(self):
        """Test retrieving a product by name when found."""
        # Arrange
        product_name = "Test Product"
        mock_doc = {
            "product_id": 1,
            "name": product_name,
            "price": 10.99,
            "category": "test_category"
        }
        self.mock_collection.find_one.return_value = mock_doc

        # Act
        result = self.repository.get_by_name(product_name)

        # Assert
        self.mock_collection.find_one.assert_called_once_with({"name": product_name})
        assert isinstance(result, Products)
        assert result.id == 1
        assert result.name == product_name

    def test_get_by_name_not_found(self):
        """Test retrieving a product by name when not found."""
        # Arrange
        product_name = "Nonexistent Product"
        self.mock_collection.find_one.return_value = None

        # Act
        result = self.repository.get_by_name(product_name)

        # Assert
        self.mock_collection.find_one.assert_called_once_with({"name": product_name})
        assert result is None

    def test_list_all_products(self):
        """Test listing all products."""
        # Arrange
        mock_docs = [
            {
                "product_id": 1,
                "name": "Product 1",
                "price": 10.99,
                "category": "category1"
            },
            {
                "product_id": 2,
                "name": "Product 2",
                "price": 20.99,
                "category": "category2"
            }
        ]

        # Create a mock cursor that can be iterated
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_docs)
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.list_all_products()

        # Assert
        self.mock_collection.find.assert_called_once_with({})
        assert len(result) == 2
        assert all(isinstance(p, Products) for p in result)
        assert result[0].id == 1
        assert result[0].name == "Product 1"
        assert result[1].id == 2
        assert result[1].name == "Product 2"

    def test_list_all_products_empty(self):
        """Test listing all products when no products exist."""
        # Arrange
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([])
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.list_all_products()

        # Assert
        self.mock_collection.find.assert_called_once_with({})
        assert len(result) == 0
        assert isinstance(result, list)

    def test_list_all_products_skips_invalid(self):
        """Test that list_all_products skips documents without valid product_id."""
        # Arrange
        mock_docs = [
            {
                "product_id": 1,
                "name": "Valid Product",
                "price": 10.99,
                "category": "category1"
            },
            {
                # Missing product_id
                "name": "Invalid Product",
                "price": 20.99,
                "category": "category2"
            },
            {
                "product_id": None,  # None product_id
                "name": "Another Invalid",
                "price": 30.99,
                "category": "category3"
            }
        ]

        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_docs)
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.list_all_products()

        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Valid Product"

    def test_list_all_alias(self):
        """Test that list_all is an alias for list_all_products."""
        # Arrange
        with patch.object(self.repository, 'list_all_products') as mock_list:
            mock_list.return_value = []

            # Act
            result = self.repository.list_all()

            # Assert
            mock_list.assert_called_once()
            assert result == []

    def test_list_by_category(self):
        """Test listing products by category."""
        # Arrange
        category = "test_category"
        mock_docs = [
            {
                "product_id": 1,
                "name": "Product 1",
                "price": 10.99,
                "category": category
            },
            {
                "product_id": 2,
                "name": "Product 2",
                "price": 20.99,
                "category": category
            }
        ]

        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_docs)
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.list_by_category(category)

        # Assert
        self.mock_collection.find.assert_called_once_with({"category": category})
        assert len(result) == 2
        assert all(p.category == category for p in result)

    def test_list_by_category_empty(self):
        """Test listing products by category when none exist in that category."""
        # Arrange
        category = "empty_category"
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([])
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.list_by_category(category)

        # Assert
        self.mock_collection.find.assert_called_once_with({"category": category})
        assert len(result) == 0

    def test_update_product(self):
        """Test updating a product successfully."""
        # Arrange
        product_id = 1
        updated_product = Products(
            id=product_id,
            name="Updated Name",
            price=15.99,
            category="updated_category"
        )

        # Mock the update operation
        self.mock_collection.update_one.return_value = Mock()

        # Mock the find_one after update to return the updated document
        updated_doc = {
            "product_id": product_id,
            "name": "Updated Name",
            "price": 15.99,
            "category": "updated_category",
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime(2023, 1, 2)
        }
        self.mock_collection.find_one.return_value = updated_doc

        # Act
        result = self.repository.update(updated_product)

        # Assert
        # Check that update_one was called with correct parameters
        self.mock_collection.update_one.assert_called_once()
        call_args = self.mock_collection.update_one.call_args
        assert call_args[0][0] == {"product_id": product_id}
        assert "name" in call_args[0][1]["$set"]
        assert "price" in call_args[0][1]["$set"]
        assert "category" in call_args[0][1]["$set"]
        assert "updated_at" in call_args[0][1]["$set"]

        # Check the returned product
        assert isinstance(result, Products)
        assert result.id == product_id
        assert result.name == "Updated Name"
        assert result.price == 15.99
        assert result.category == "updated_category"
        assert result.created_at == datetime(2023, 1, 1)
        assert result.updated_at == datetime(2023, 1, 2)

    def test_update_product_with_string_id(self):
        """Test updating a product when ID is a string."""
        # Arrange
        product_id = "1"  # String ID
        expected_int_id = 1
        updated_product = Products(
            id=product_id,
            name="Updated Product",
            price=15.99,
            category="updated_category"
        )

        self.mock_collection.update_one.return_value = Mock()

        updated_doc = {
            "product_id": expected_int_id,
            "name": "Updated Product",
            "price": 15.99,
            "category": "updated_category"
        }
        self.mock_collection.find_one.return_value = updated_doc

        # Act
        result = self.repository.update(updated_product)

        # Assert
        self.mock_collection.update_one.assert_called_once()
        call_args = self.mock_collection.update_one.call_args
        assert call_args[0][0] == {"product_id": expected_int_id}

    def test_update_product_exception_handling(self):
        """Test exception handling in update."""
        # Arrange
        product_id = 1
        updated_product = Products(
            id=product_id,
            name="Updated Product",
            price=15.99,
            category="updated_category"
        )

        # Mock an exception during update
        self.mock_collection.update_one.side_effect = Exception("Database error")

        # Act
        result = self.repository.update(updated_product)

        # Assert
        assert result == updated_product  # Returns original product on error

    def test_delete_product(self):
        """Test deleting a product successfully."""
        # Arrange
        product_id = 1
        self.mock_collection.delete_one.return_value = Mock(deleted_count=1)

        # Act
        result = self.repository.delete(product_id)

        # Assert
        self.mock_collection.delete_one.assert_called_once_with({"product_id": product_id})
        assert result is True

    def test_delete_product_with_string_id(self):
        """Test deleting a product when ID is a string."""
        # Arrange
        product_id = "1"  # String ID
        expected_int_id = 1
        self.mock_collection.delete_one.return_value = Mock(deleted_count=1)

        # Act
        result = self.repository.delete(product_id)

        # Assert
        self.mock_collection.delete_one.assert_called_once_with({"product_id": expected_int_id})
        assert result is True

    def test_delete_product_not_found(self):
        """Test deleting a product that doesn't exist."""
        # Arrange
        product_id = 999
        self.mock_collection.delete_one.return_value = Mock(deleted_count=0)

        # Act
        result = self.repository.delete(product_id)

        # Assert
        self.mock_collection.delete_one.assert_called_once_with({"product_id": product_id})
        assert result is False

    def test_delete_product_exception_handling(self):
        """Test exception handling in delete."""
        # Arrange
        product_id = 1
        self.mock_collection.delete_one.side_effect = Exception("Database error")

        # Act
        result = self.repository.delete(product_id)

        # Assert
        assert result is False

    def test_get_by_ids(self):
        """Test retrieving multiple products by their IDs."""
        # Arrange
        product_ids = [1, 2, "3"]  # Mix of int and string IDs
        mock_docs = [
            {"product_id": 1, "name": "Product 1", "price": 10.99, "category": "category1"},
            {"product_id": 2, "name": "Product 2", "price": 20.99, "category": "category2"},
            {"product_id": 3, "name": "Product 3", "price": 30.99, "category": "category3"}
        ]

        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_docs)
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.get_by_ids(product_ids)

        # Assert
        self.mock_collection.find.assert_called_once()
        call_args = self.mock_collection.find.call_args
        assert call_args[0][0] == {"product_id": {"$in": [1, 2, 3]}}

        assert len(result) == 3
        assert all(isinstance(p, Products) for p in result)
        assert [p.id for p in result] == [1, 2, 3]

    def test_get_by_ids_with_invalid_ids(self):
        """Test retrieving products with invalid IDs in the list."""
        # Arrange
        product_ids = ["invalid", "not_a_number", "abc"]

        # Act
        result = self.repository.get_by_ids(product_ids)

        # Assert
        assert result == []
        self.mock_collection.find.assert_not_called()

    def test_get_by_ids_with_mixed_ids(self):
        """Test retrieving products with a mix of valid and invalid IDs."""
        # Arrange
        product_ids = [1, "invalid", 3]

        mock_docs = [
            {"product_id": 1, "name": "Product 1", "price": 10.99, "category": "category1"},
            {"product_id": 3, "name": "Product 3", "price": 30.99, "category": "category3"}
        ]

        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(mock_docs)
        self.mock_collection.find.return_value = mock_cursor

        # Act
        result = self.repository.get_by_ids(product_ids)

        # Assert
        self.mock_collection.find.assert_called_once()
        call_args = self.mock_collection.find.call_args
        assert call_args[0][0] == {"product_id": {"$in": [1, 3]}}

        assert len(result) == 2
        assert [p.id for p in result] == [1, 3]