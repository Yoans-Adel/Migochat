"""
Product Comparison and Side-by-Side Analysis Tools

This module provides functionality for comparing multiple products side-by-side,
generating formatted comparison tables in both Arabic and English. Useful for
helping customers make informed purchasing decisions by highlighting differences
in pricing, features, ratings, and availability.

The comparison tool automatically identifies the best deal based on final price
and presents information in a structured, easy-to-read format suitable for
Messenger conversations.

Functions:
    format_comparison_ar: Generate Arabic comparison table
    format_comparison_en: Generate English comparison table

Features:
    - Side-by-side product comparison
    - Automatic best deal identification
    - Multi-language support (Arabic/English)
    - Structured pricing and rating display
    - Availability and shipping information

Example:
    >>> products = [{"id": 1, "name": "Product A", "final_price": 100}, ...]
    >>> comparison = format_comparison_ar(products)
"""

from typing import Any, Dict, List

from .product_formatter import parse_product_data


def format_comparison_ar(products: List[Dict[str, Any]]) -> str:
    header = "📊 **مقارنة المنتجات**\n" + "=" * 50 + "\n\n"
    comparison: List[str] = []
    for i, product in enumerate(products, 1):
        parsed = parse_product_data(product)
        item = f"**منتج {i}: {parsed.name}**\n"
        item += f"💰 السعر: {parsed.final_price} جنيه"
        item += f" (خصم {parsed.discount}%)\n" if parsed.discount > 0 else "\n"
        item += f"⭐ التقييم: {parsed.rating}/5 ({parsed.count_rating} تقييم)\n"
        item += f"📦 متوفر: {parsed.stock_quantity} قطعة\n" if parsed.stock_quantity > 0 else "❌ غير متوفر\n"
        if parsed.is_best_seller:
            item += "🏆 الأكثر مبيعاً\n"
        if parsed.is_new_arrival:
            item += "🆕 وصل حديثاً\n"
        if parsed.is_free_delivery:
            item += "🚚 شحن مجاني\n"
        if parsed.colors:
            item += f"🎨 الألوان: {', '.join(parsed.colors[:3])}\n"
        if parsed.sizes:
            item += f"📏 الأحجام: {', '.join(parsed.sizes[:3])}\n"
        if parsed.main_image:
            item += f"🖼️ [عرض الصورة]({parsed.main_image})\n"
        comparison.append(item)

    best_deal = min(products, key=lambda p: p.get("final_price", float("inf")))
    best_deal_name = parse_product_data(best_deal).name
    footer = f"\n{'=' * 50}\n"
    footer += f"🏆 **أفضل صفقة**: {best_deal_name} - {best_deal.get('final_price', 0)} جنيه"
    return header + "\n\n".join(comparison) + footer


def format_comparison_en(products: List[Dict[str, Any]]) -> str:
    header = "📊 **Product Comparison**\n" + "=" * 50 + "\n\n"
    comparison: List[str] = []
    for i, product in enumerate(products, 1):
        parsed = parse_product_data(product)
        item = f"**Product {i}: {parsed.name}**\n"
        item += f"💰 Price: {parsed.final_price} EGP"
        item += f" (Save {parsed.discount}%)\n" if parsed.discount > 0 else "\n"
        item += f"⭐ Rating: {parsed.rating}/5 ({parsed.count_rating} reviews)\n"
        item += f"📦 Available: {parsed.stock_quantity} pieces\n" if parsed.stock_quantity > 0 else "❌ Out of Stock\n"
        if parsed.is_best_seller:
            item += "🏆 Best Seller\n"
        if parsed.is_new_arrival:
            item += "🆕 New Arrival\n"
        if parsed.is_free_delivery:
            item += "🚚 Free Delivery\n"
        if parsed.colors:
            item += f"🎨 Colors: {', '.join(parsed.colors[:3])}\n"
        if parsed.sizes:
            item += f"📏 Sizes: {', '.join(parsed.sizes[:3])}\n"
        if parsed.main_image:
            item += f"🖼️ [View Image]({parsed.main_image})\n"
        comparison.append(item)

    best_deal = min(products, key=lambda p: p.get("final_price", float("inf")))
    best_deal_name = parse_product_data(best_deal).name
    footer = f"\n{'=' * 50}\n"
    footer += f"🏆 **Best Deal**: {best_deal_name} - {best_deal.get('final_price', 0)} EGP"
    return header + "\n\n".join(comparison) + footer


