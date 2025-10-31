"""
Product Card Generator for Messenger

This module generates detailed product cards with proper BWW Store links.
"""

import re
from datetime import datetime
from typing import Any, Dict

from .product_formatter import parse_product_data


def _create_product_link(product: Dict[str, Any], language: str = "ar") -> str:
    """Create BWW Store product link matching their actual format.
    
    Format: https://bww-store.com/{lang}/product-details/{slug}/{product_id}
    Example: https://bww-store.com/ar/product-details/raia-mens-summer-set-2/2464
    
    Args:
        product: Product data dictionary
        language: Language code ("ar" or "en")
    
    Returns:
        Full product URL
    """
    product_id = product.get("id", "")
    if not product_id:
        return "https://bww-store.com"
    
    # Create slug from product name
    product_name = str(product.get("name", "")).strip()
    if product_name:
        # Remove Arabic/English special characters, keep alphanumeric and spaces
        slug = re.sub(r'[^\w\s-]', '', product_name, flags=re.UNICODE)
        # Replace spaces and multiple dashes with single dash
        slug = re.sub(r'[-\s]+', '-', slug).strip('-').lower()
        # Limit slug length
        slug = slug[:50] if len(slug) > 50 else slug
        if not slug:
            slug = f"product-{product_id}"
    else:
        slug = f"product-{product_id}"
    
    # Match BWW Store format: /ar/product-details/slug/id
    lang_prefix = "ar" if language == "ar" else "en"
    return f"https://bww-store.com/{lang_prefix}/product-details/{slug}/{product_id}"


def _create_size_guide(product: Dict[str, Any], language: str) -> str:
    """Create size guide if sizes are available."""
    sizes = product.get("sizes", [])
    if not sizes:
        return ""
    
    if language == "ar":
        title = "📏 **المقاسات المتوفرة:**"
        size_list = [f"• {s}" for s in sizes[:5]]  # Show max 5 sizes
    else:
        title = "📏 **Available Sizes:**"
        size_list = [f"• {s}" for s in sizes[:5]]
    
    return "\n".join([title] + size_list)


def _create_features(product: Dict[str, Any], language: str) -> str:
    """Create features list from product data."""
    features = []
    material = product.get("material", "")
    
    if material:
        features.append(("• خامة: {m}" if language == "ar" else "• Material: {m}").format(m=material))
    
    if product.get("is_best_seller"):
        features.append("• الأكثر مبيعاً ⭐" if language == "ar" else "• Best Seller ⭐")
    
    if product.get("is_new_arrival"):
        features.append("• وصل حديثاً 🆕" if language == "ar" else "• New Arrival 🆕")
    
    if product.get("is_free_delivery"):
        features.append("• شحن مجاني 🚚" if language == "ar" else "• Free Delivery 🚚")
    
    return "\n".join(features) if features else ""


def generate_product_card(product: Dict[str, Any], language: str = "ar") -> Dict[str, Any]:
    """Generate a complete product card for Messenger with BWW Store link.
    
    Creates a formatted card with all product details and a working link to BWW Store.
    
    Args:
        product: Product data dictionary from API
        language: Language code ("ar" for Arabic, "en" for English)
    
    Returns:
        Dictionary with:
        - success: bool
        - card_content: str (formatted card)
        - metadata: dict (generation info)
        - error: str (if failed)
    """
    try:
        parsed = parse_product_data(product)
        
        # Create components
        product_link = _create_product_link(product, language)
        size_guide = _create_size_guide(product, language)
        features = _create_features(product, language)
        
        # Build card based on language
        if language == "ar":
            card = f"🛍️ **{parsed.name}**\n\n"
            
            # Price with discount
            card += f"💰 **السعر**: {parsed.final_price} جنيه"
            if parsed.discount > 0:
                card += f" (خصم {parsed.discount}%)\n"
                card += f"📊 **السعر الأصلي**: {parsed.original_price} جنيه\n"
            else:
                card += "\n"
            
            # Store and rating
            card += f"🏪 **المتجر**: {parsed.store_name}\n"
            if parsed.rating > 0:
                card += f"⭐ **التقييم**: {parsed.rating}/5 ({parsed.count_rating} تقييم)\n"
            
            # Stock availability
            if parsed.stock_quantity > 0:
                card += f"📦 **متوفر**: {parsed.stock_quantity} قطعة\n"
            else:
                card += "❌ **غير متوفر حالياً**\n"
            
            # Special badges
            if parsed.is_best_seller:
                card += "🏆 **الأكثر مبيعاً**\n"
            if parsed.is_new_arrival:
                card += "🆕 **وصل حديثاً**\n"
            if parsed.is_free_delivery:
                card += "🚚 **شحن مجاني**\n"
            
            # Colors
            if parsed.colors:
                card += f"🎨 **الألوان**: {', '.join(parsed.colors[:3])}\n"
            
            # Features
            if features:
                card += f"\n{features}\n"
            
            # Sizes
            if size_guide:
                card += f"\n{size_guide}\n"
            
            # Product link (BWW Store format)
            card += f"\n🔗 **رابط المنتج**: {product_link}"
            card += "\n\n💬 للطلب أو الاستفسار: تواصل معنا"
            
        else:  # English
            card = f"🛍️ **{parsed.name}**\n\n"
            
            # Price with discount
            card += f"💰 **Price**: {parsed.final_price} EGP"
            if parsed.discount > 0:
                card += f" (Save {parsed.discount}%)\n"
                card += f"📊 **Original Price**: {parsed.original_price} EGP\n"
            else:
                card += "\n"
            
            # Store and rating
            card += f"🏪 **Store**: {parsed.store_name}\n"
            if parsed.rating > 0:
                card += f"⭐ **Rating**: {parsed.rating}/5 ({parsed.count_rating} reviews)\n"
            
            # Stock availability
            if parsed.stock_quantity > 0:
                card += f"📦 **Available**: {parsed.stock_quantity} pieces\n"
            else:
                card += "❌ **Out of Stock**\n"
            
            # Special badges
            if parsed.is_best_seller:
                card += "🏆 **Best Seller**\n"
            if parsed.is_new_arrival:
                card += "🆕 **New Arrival**\n"
            if parsed.is_free_delivery:
                card += "🚚 **Free Delivery**\n"
            
            # Colors
            if parsed.colors:
                card += f"🎨 **Colors**: {', '.join(parsed.colors[:3])}\n"
            
            # Features
            if features:
                card += f"\n{features}\n"
            
            # Sizes
            if size_guide:
                card += f"\n{size_guide}\n"
            
            # Product link (BWW Store format)
            card += f"\n🔗 **Product Link**: {product_link}"
            card += "\n\n💬 To order or inquire: Contact us"
        
        return {
            "success": True,
            "card_content": card,
            "product_link": product_link,  # للاختبار
            "metadata": {
                "product_id": parsed.id,
                "language": language,
                "generated_at": datetime.utcnow().isoformat(),
                "card_length": len(card),
            },
        }
    
    except Exception as exc:
        error_msg = "❌ عذراً، حدث خطأ في إنشاء بطاقة المنتج." if language == "ar" else "❌ Sorry, error creating product card."
        return {
            "success": False,
            "error": str(exc),
            "card_content": error_msg,
        }
