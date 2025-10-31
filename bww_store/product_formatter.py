"""
Product Information Formatting and Parsing Utilities

This module provides utilities for parsing raw API product data into structured
ProductInfo objects and formatting them for display in Messenger conversations.
Supports both Arabic and English languages with culturally appropriate formatting.

The formatting functions handle price display, availability status, ratings,
and business attributes like best seller badges and delivery information.

Functions:
    parse_product_data: Convert raw API dict to ProductInfo dataclass
    format_product_for_messenger: Main formatting function with language selection
    _format_product_arabic: Arabic-specific formatting logic
    _format_product_english: English-specific formatting logic

Example:
    >>> raw_product = {"id": 123, "name": "Headphones", "final_price": 199.99}
    >>> product = parse_product_data(raw_product)
    >>> message = format_product_for_messenger(product, language="ar")
"""

from typing import Any, Dict, Union

from .models import ProductInfo


def parse_product_data(product_data: Dict[str, Any]) -> ProductInfo:
    return ProductInfo(
        id=product_data.get("id", 0),
        name=product_data.get("name", "Unknown Product"),
        final_price=float(product_data.get("final_price", 0) or 0),
        original_price=float(product_data.get("original_price", 0) or 0),
        discount=float(product_data.get("discount", 0) or 0),
        store_name=product_data.get("store_name", "BWW Store"),
        rating=float(product_data.get("rating", 0) or 0),
        count_rating=int(product_data.get("count_rating", 0) or 0),
        stock_quantity=int(product_data.get("stock_quantity", 0) or 0),
        main_image=product_data.get("main_image", ""),
        category=product_data.get("category", {}),
        is_best_seller=bool(product_data.get("is_best_seller", False)),
        is_new_arrival=bool(product_data.get("is_new_arrival", False)),
        is_free_delivery=bool(product_data.get("is_free_delivery", False)),
        is_refundable=bool(product_data.get("is_refundable", False)),
        colors=list(product_data.get("colors", []) or []),
        sizes=list(product_data.get("sizes", []) or []),
        material=product_data.get("material", ""),
        description=product_data.get("description", ""),
    )


def format_product_for_messenger(product: Union[Dict[str, Any], ProductInfo], language: str = "ar") -> str:
    info = parse_product_data(product) if isinstance(product, dict) else product
    return _format_product_english(info) if language == "en" else _format_product_arabic(info)


def _format_product_arabic(product: ProductInfo) -> str:
    message = f"🛍️ **{product.name}**\n\n"

    if product.discount > 0:
        message += f"💰 **السعر**: {product.final_price} جنيه (خصم {product.discount}%)\n"
        message += f"📊 **السعر الأصلي**: {product.original_price} جنيه\n"
    else:
        message += f"💰 **السعر**: {product.final_price} جنيه\n"

    message += f"🏪 **المتجر**: {product.store_name}\n"
    if product.rating > 0:
        message += f"⭐ **التقييم**: {product.rating}/5 ({product.count_rating} تقييم)\n"

    if product.stock_quantity > 0:
        message += f"📦 **متوفر**: {product.stock_quantity} قطعة\n"
    else:
        message += "❌ **غير متوفر حالياً**\n"

    if product.is_best_seller:
        message += "🏆 **الأكثر مبيعاً**\n"
    if product.is_new_arrival:
        message += "🆕 **وصل حديثاً**\n"
    if product.is_free_delivery:
        message += "🚚 **شحن مجاني**\n"
    if product.is_refundable:
        message += "↩️ **قابل للإرجاع**\n"

    if product.main_image:
        message += f"\n🖼️ [عرض الصورة]({product.main_image})"

    return message


def _format_product_english(product: ProductInfo) -> str:
    message = f"🛍️ **{product.name}**\n\n"

    if product.discount > 0:
        message += f"💰 **Price**: {product.final_price} EGP (Save {product.discount}%)\n"
        message += f"📊 **Original Price**: {product.original_price} EGP\n"
    else:
        message += f"💰 **Price**: {product.final_price} EGP\n"

    message += f"🏪 **Store**: {product.store_name}\n"
    if product.rating > 0:
        message += f"⭐ **Rating**: {product.rating}/5 ({product.count_rating} reviews)\n"

    if product.stock_quantity > 0:
        message += f"📦 **Available**: {product.stock_quantity} pieces\n"
    else:
        message += "❌ **Out of Stock**\n"

    if product.is_best_seller:
        message += "🏆 **Best Seller**\n"
    if product.is_new_arrival:
        message += "🆕 **New Arrival**\n"
    if product.is_free_delivery:
        message += "🚚 **Free Delivery**\n"
    if product.is_refundable:
        message += "↩️ **Refundable**\n"

    if product.main_image:
        message += f"\n🖼️ [View Image]({product.main_image})"

    return message


