"""Search strategies and result processing for BWW Store."""

from typing import Any, Dict, List


def extract_products_from_results(products_data: List[Any]) -> List[Dict[str, Any]]:
    """Extract product dictionaries from search results.

    Handles both tuple format (product, score) and direct dict format.

    Args:
        products_data: List of products in various formats

    Returns:
        List of product dictionaries (deduplicated)
    """
    products: List[Dict[str, Any]] = []

    for item in products_data:
        product: Dict[str, Any]

        if isinstance(item, tuple) and len(item) > 0:
            product = item[0]
        elif isinstance(item, dict):
            product = item
        else:
            continue

        if product not in products:
            products.append(product)

    return products


def format_no_results_message(
    intent: Any,
    suggestions: List[str],
    language: str,
    smart_response_generator: Any
) -> str:
    """Generate smart no-results message with suggestions.

    Args:
        intent: Search intent
        suggestions: Search suggestions
        language: Language code
        smart_response_generator: Engine to generate response

    Returns:
        Formatted no-results message
    """
    no_results_response = smart_response_generator.generate_smart_response(intent, results_count=0)

    if not suggestions:
        return no_results_response

    if language == "ar":
        suggestion_text = "\n\n💡 جرب تدور عن:\n" + "\n".join(f"• {s}" for s in suggestions)
    else:
        suggestion_text = "\n\n💡 Try searching for:\n" + "\n".join(f"• {s}" for s in suggestions)

    return no_results_response + suggestion_text
