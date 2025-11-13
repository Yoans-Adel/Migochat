"""
Comprehensive Tests for BWW Store Package
Tests for bww_store package including models, client, search, and integration
"""

import pytest
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

if TYPE_CHECKING:
    from typing import Any, Dict, List


# ============================================================================
# MODELS TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.unit
class TestBWWStoreModels:
    """Test bww_store data models"""

    def test_cache_strategy_enum(self):
        """Test CacheStrategy enum values"""
        from bww_store.models import CacheStrategy
        
        assert CacheStrategy.NO_CACHE.value == "no_cache"
        assert CacheStrategy.SHORT_TERM.value == "short_term"
        assert CacheStrategy.MEDIUM_TERM.value == "medium_term"
        assert CacheStrategy.LONG_TERM.value == "long_term"
        assert len(list(CacheStrategy)) == 4

    def test_api_response_success(self):
        """Test APIResponse for successful operation"""
        from bww_store.models import APIResponse
        
        response = APIResponse(
            data={"products": []},
            success=True,
            status_code=200
        )
        
        assert response.success is True
        assert response.status_code == 200
        assert response.error is None
        assert response.data == {"products": []}
        assert response.cached is False
        assert isinstance(response.timestamp, datetime)

    def test_api_response_error(self):
        """Test APIResponse for error condition"""
        from bww_store.models import APIResponse
        
        response = APIResponse(
            success=False,
            error="Network timeout",
            status_code=504
        )
        
        assert response.success is False
        assert response.status_code == 504
        assert response.error == "Network timeout"
        assert response.data is None

    def test_api_response_cached(self):
        """Test APIResponse with cached flag"""
        from bww_store.models import APIResponse
        
        response = APIResponse(
            data={"test": "data"},
            success=True,
            cached=True,
            response_time_ms=5.0
        )
        
        assert response.cached is True
        assert response.response_time_ms == 5.0

    def test_product_info_basic(self):
        """Test ProductInfo with basic data"""
        from bww_store.models import ProductInfo
        
        product = ProductInfo(
            id=12345,
            name="Test Product",
            final_price=299.99,
            original_price=399.99,
            discount=25.0,
            store_name="BWW Store",
            rating=4.5,
            count_rating=100,
            stock_quantity=50,
            main_image="https://example.com/image.jpg",
            category={"id": 1, "name": "Electronics"}
        )
        
        assert product.id == 12345
        assert product.name == "Test Product"
        assert product.final_price == 299.99
        assert product.discount == 25.0
        assert product.rating == 4.5
        assert product.stock_quantity == 50

    def test_product_info_optional_fields(self):
        """Test ProductInfo with optional fields"""
        from bww_store.models import ProductInfo
        
        product = ProductInfo(
            id=123,
            name="Premium Product",
            final_price=999.99,
            original_price=999.99,
            discount=0.0,
            store_name="BWW",
            rating=5.0,
            count_rating=200,
            stock_quantity=10,
            main_image="image.jpg",
            category={},
            is_best_seller=True,
            is_new_arrival=True,
            is_free_delivery=True,
            is_refundable=True,
            colors=["Black", "White", "Blue"],
            sizes=["S", "M", "L", "XL"],
            material="Cotton",
            description="Premium quality product"
        )
        
        assert product.is_best_seller is True
        assert product.is_new_arrival is True
        assert product.is_free_delivery is True
        assert product.is_refundable is True
        assert len(product.colors) == 3
        assert len(product.sizes) == 4
        assert product.material == "Cotton"
        assert "Premium" in product.description

    def test_product_info_immutable(self):
        """Test that ProductInfo is immutable (frozen dataclass)"""
        from bww_store.models import ProductInfo
        
        product = ProductInfo(
            id=1, name="Test", final_price=100, original_price=100,
            discount=0, store_name="BWW", rating=0, count_rating=0,
            stock_quantity=0, main_image="", category={}
        )
        
        with pytest.raises(AttributeError):
            product.name = "Modified"  # Should raise error


# ============================================================================
# PACKAGE IMPORTS TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.unit
class TestBWWStorePackage:
    """Test bww_store package initialization and exports"""

    def test_package_imports(self):
        """Test that package can be imported"""
        import bww_store
        assert bww_store is not None

    def test_package_version(self):
        """Test package version is defined"""
        from bww_store import __version__
        assert __version__ == "2.0.0"  # Updated to match current version

    def test_package_exports_api_service(self):
        """Test BWWStoreAPIService is exported"""
        from bww_store import BWWStoreAPIService
        assert BWWStoreAPIService is not None

    def test_package_exports_models(self):
        """Test models are exported"""
        from bww_store import APIResponse, CacheStrategy, ProductInfo
        assert all([APIResponse, CacheStrategy, ProductInfo])

    def test_package_exports_constants(self):
        """Test constants are exported"""
        from bww_store import (
            EGYPTIAN_CORRECTIONS,
            CLOTHING_KEYWORDS_AR,
            CLOTHING_KEYWORDS_EN
        )
        assert all([EGYPTIAN_CORRECTIONS, CLOTHING_KEYWORDS_AR, CLOTHING_KEYWORDS_EN])


# ============================================================================
# CONSTANTS TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.unit
class TestBWWStoreConstants:
    """Test bww_store constants and static data"""

    def test_egyptian_corrections_exist(self):
        """Test EGYPTIAN_CORRECTIONS dictionary exists"""
        from bww_store.constants import EGYPTIAN_CORRECTIONS
        assert isinstance(EGYPTIAN_CORRECTIONS, dict)
        assert len(EGYPTIAN_CORRECTIONS) > 0

    def test_egyptian_corrections_samples(self):
        """Test some Egyptian dialect corrections"""
        from bww_store.constants import EGYPTIAN_CORRECTIONS
        
        # Common corrections
        assert "عايز" in EGYPTIAN_CORRECTIONS
        assert "محتاج" in EGYPTIAN_CORRECTIONS
        assert "كتير" in EGYPTIAN_CORRECTIONS
        assert "جميل" in EGYPTIAN_CORRECTIONS

    def test_clothing_keywords_ar(self):
        """Test Arabic clothing keywords"""
        from bww_store.constants import CLOTHING_KEYWORDS_AR
        
        assert isinstance(CLOTHING_KEYWORDS_AR, dict)
        assert "قميص" in CLOTHING_KEYWORDS_AR  # Shirt
        assert "بنطال" in CLOTHING_KEYWORDS_AR  # Pants
        assert "جاكيت" in CLOTHING_KEYWORDS_AR  # Jacket

    def test_clothing_keywords_en(self):
        """Test English clothing keywords"""
        from bww_store.constants import CLOTHING_KEYWORDS_EN
        
        assert isinstance(CLOTHING_KEYWORDS_EN, dict)
        assert "suit" in CLOTHING_KEYWORDS_EN
        assert "pants" in CLOTHING_KEYWORDS_EN
        assert "shirt" in CLOTHING_KEYWORDS_EN

    def test_search_suggestions_ar(self):
        """Test Arabic search suggestions"""
        from bww_store.constants import BWW_SEARCH_SUGGESTIONS_AR
        
        assert isinstance(BWW_SEARCH_SUGGESTIONS_AR, dict)
        assert len(BWW_SEARCH_SUGGESTIONS_AR) > 0
        # Check some keys exist
        assert "قميص" in BWW_SEARCH_SUGGESTIONS_AR or "رجالي" in BWW_SEARCH_SUGGESTIONS_AR

    def test_priority_items_ar(self):
        """Test Arabic priority items"""
        from bww_store.constants import BWW_PRIORITY_ITEMS_AR
        
        assert isinstance(BWW_PRIORITY_ITEMS_AR, list)
        assert len(BWW_PRIORITY_ITEMS_AR) > 0


# ============================================================================
# API CLIENT TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.unit
class TestBWWStoreAPIService:
    """Test BWWStoreAPIService main class"""

    def test_api_service_initialization(self):
        """Test API service can be initialized"""
        from bww_store import BWWStoreAPIService
        
        client = BWWStoreAPIService(language="ar")
        assert client is not None
        assert client.language == "ar"

    def test_api_service_components(self):
        """Test API service has all components"""
        from bww_store import BWWStoreAPIService
        
        client = BWWStoreAPIService(language="ar")
        
        assert hasattr(client, 'client')
        assert hasattr(client, 'search')
        assert hasattr(client, 'products')
        assert hasattr(client, 'compatibility')

    def test_api_service_methods_exist(self):
        """Test API service has expected methods"""
        from bww_store import BWWStoreAPIService
        
        client = BWWStoreAPIService(language="ar")
        
        # Search methods
        assert hasattr(client, 'search_and_format_products')
        
        # Product methods
        assert hasattr(client, 'get_product_details')
        assert hasattr(client, 'search_products_by_text')
        assert hasattr(client, 'get_products_by_category')
        assert hasattr(client, 'get_products_by_color')
        assert hasattr(client, 'get_products_by_price_range')
        assert hasattr(client, 'filter_products')

    def test_api_service_english_language(self):
        """Test API service with English language"""
        from bww_store import BWWStoreAPIService
        
        client = BWWStoreAPIService(language="en")
        assert client.language == "en"


# ============================================================================
# INTEGRATION WITH PROJECT TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.integration
class TestBWWStoreProjectIntegration:
    """Test bww_store integration with Migochat project"""

    def test_imported_in_routes_api(self):
        """Test bww_store is imported in Server/routes/api.py"""
        try:
            from Server.routes.api import BWWStoreAPIService
            assert BWWStoreAPIService is not None
        except ImportError:
            pytest.skip("Server.routes.api not available")

    def test_bww_store_in_project_root(self):
        """Test bww_store folder exists in project root"""
        bww_store_path = Path("bww_store")
        assert bww_store_path.exists()
        assert bww_store_path.is_dir()

    def test_bww_store_has_init(self):
        """Test bww_store has __init__.py"""
        init_file = Path("bww_store/__init__.py")
        assert init_file.exists()

    def test_bww_store_modules_exist(self):
        """Test all bww_store modules exist"""
        bww_store_path = Path("bww_store")
        
        required_modules = [
            "api_client.py",
            "client.py",
            "search.py",
            "product_ops.py",
            "product_formatter.py",
            "card_generator.py",
            "comparison_tool.py",
            "models.py",
            "constants.py",
            "base.py",
            "utils.py"
        ]
        
        for module in required_modules:
            module_path = bww_store_path / module
            assert module_path.exists(), f"Missing module: {module}"


# ============================================================================
# CRITICAL FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.critical
class TestBWWStoreCritical:
    """Critical tests that must pass for bww_store to work"""

    def test_can_import_main_service(self):
        """CRITICAL: Main service must be importable"""
        try:
            from bww_store import BWWStoreAPIService
            assert BWWStoreAPIService is not None
        except Exception as e:
            pytest.fail(f"Cannot import BWWStoreAPIService: {e}")

    def test_can_create_client_instance(self):
        """CRITICAL: Client instance must be creatable"""
        try:
            from bww_store import BWWStoreAPIService
            client = BWWStoreAPIService(language="ar")
            assert client is not None
        except Exception as e:
            pytest.fail(f"Cannot create client instance: {e}")

    def test_models_are_importable(self):
        """CRITICAL: Models must be importable"""
        try:
            from bww_store.models import APIResponse, CacheStrategy, ProductInfo
            assert all([APIResponse, CacheStrategy, ProductInfo])
        except Exception as e:
            pytest.fail(f"Cannot import models: {e}")

    def test_constants_are_importable(self):
        """CRITICAL: Constants must be importable"""
        try:
            from bww_store.constants import EGYPTIAN_CORRECTIONS
            assert EGYPTIAN_CORRECTIONS is not None
        except Exception as e:
            pytest.fail(f"Cannot import constants: {e}")

    def test_package_structure_valid(self):
        """CRITICAL: Package structure must be valid"""
        bww_store_path = Path("bww_store")
        
        # Must have __init__.py
        assert (bww_store_path / "__init__.py").exists()
        
        # Must have main modules
        assert (bww_store_path / "api_client.py").exists()
        assert (bww_store_path / "models.py").exists()
        assert (bww_store_path / "constants.py").exists()


# ============================================================================
# SMOKE TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.smoke
class TestBWWStoreSmoke:
    """Quick smoke tests for bww_store package"""

    def test_import_package(self):
        """Smoke: Import package"""
        import bww_store
        assert bww_store is not None

    def test_import_main_class(self):
        """Smoke: Import main class"""
        from bww_store import BWWStoreAPIService
        assert BWWStoreAPIService is not None

    def test_create_client(self):
        """Smoke: Create client instance"""
        from bww_store import BWWStoreAPIService
        client = BWWStoreAPIService()
        assert client is not None

    def test_models_dataclasses(self):
        """Smoke: Models are valid dataclasses"""
        from bww_store.models import APIResponse, ProductInfo
        from dataclasses import is_dataclass
        
        assert is_dataclass(APIResponse)
        assert is_dataclass(ProductInfo)


# ============================================================================
# DOCUMENTATION TESTS
# ============================================================================

@pytest.mark.bww_store
@pytest.mark.documentation
class TestBWWStoreDocumentation:
    """Test bww_store documentation files"""

    def test_readme_exists(self):
        """Test README.md exists"""
        readme_path = Path("bww_store/README.md")
        assert readme_path.exists()

    def test_changelog_exists(self):
        """Test CHANGELOG.md exists"""
        changelog_path = Path("bww_store/CHANGELOG.md")
        assert changelog_path.exists()

    def test_license_exists(self):
        """Test LICENSE file exists"""
        license_path = Path("bww_store/LICENSE")
        assert license_path.exists()

    def test_docs_folder_exists(self):
        """Test docs folder exists"""
        docs_path = Path("bww_store/docs")
        assert docs_path.exists()
        assert docs_path.is_dir()

    def test_pyproject_toml_exists(self):
        """Test pyproject.toml exists"""
        pyproject_path = Path("bww_store/pyproject.toml")
        assert pyproject_path.exists()
