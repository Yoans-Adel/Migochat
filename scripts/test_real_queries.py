"""
Real-World Customer Query Testing Script
========================================

This script tests BWW Store with real customer queries in Egyptian Arabic
to validate language understanding and search accuracy.

Usage:
    python scripts/test_real_queries.py

Author: BWW Store Team
Date: 2025
"""

import sys
import time
from pathlib import Path
from colorama import init, Fore, Style

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bww_store import BWWClient
from bww_store.constants import EGYPTIAN_CORRECTIONS


# Initialize colorama for colored output
init(autoreset=True)


# ============================================================================
# Real Customer Queries Database
# ============================================================================

REAL_CUSTOMER_QUERIES = {
    "Casual Wear": [
        "عايز طقم كاجوال حلو",
        "محتاج لبس عملي للجامعة",
        "بدور على قميص وبنطال جينز",
        "نفسي في هودي مريح للبيت",
        "ياريت شورت وتيشرت للصيف",
    ],
    
    "Formal Wear": [
        "عايز بدلة رسمية سودا",
        "محتاج طقم فورمال للشغل",
        "بدور على قميص أبيض وبنطال",
        "نفسي في جاكيت بليزر أنيق",
        "ياريت كرافتة وحزام",
    ],
    
    "Women's Wear": [
        "عايزة فستان سهرة حلو",
        "محتاجة بلوزة وجونلة",
        "بدور على طقم محجبات",
        "نفسي في فستان ماكسي صيفي",
        "ياريت شنطة حلوة",
    ],
    
    "Sports Wear": [
        "عايز طقم رياضي للجيم",
        "محتاج لبس سبورت للران",
        "بدور على كوتشي رياضي",
        "نفسي في شورت وتانك توب",
        "ياريت ليجنج للتمرين",
    ],
    
    "Kids Wear": [
        "عايز طقم للولاد",
        "محتاج فستان للبنات",
        "بدور على ملابس أطفال",
        "نفسي في طقم مدرسة",
        "ياريت بيجاما للعيال",
    ],
    
    "Seasonal": [
        "عايز طقم صيفي خفيف",
        "محتاج جاكيت شتوي دافي",
        "بدور على قميص قطن",
        "نفسي في معطف صوف",
        "ياريت سويتر ثقيل",
    ],
    
    "Colors & Styles": [
        "عايز قميص أبيض سادة",
        "محتاج بنطال جينز أسود",
        "بدور على فستان أحمر",
        "نفسي في جاكيت أزرق",
        "ياريت شنطة بنية",
    ],
    
    "Mixed Attributes": [
        "عايز قميص أبيض قطن رجالي",
        "محتاج بنطال جينز أسود واسع",
        "بدور على فستان وردي طويل",
        "نفسي في جاكيت جلد أسود",
        "ياريت طقم رياضي أزرق للأطفال",
    ],
    
    "Conversational": [
        "عايز حاجة حلوة للفرح",
        "محتاج لبس شيك للمناسبة",
        "بدور على حاجة مريحة",
        "نفسي في طقم جامد",
        "ياريت حاجة مش غالية",
    ],
    
    "Typos & Variations": [
        "عاوز قمسي ابيض",  # عاوز، قمسي
        "محتاج بنطلون اسود",  # بنطلون
        "بدور على جاكت جلد",  # جاكت
        "نفسي في تيشرت احمر",  # تيشرت
        "ياريت كوتشي ازرق",  # كوتشي، ازرق
    ],
}


# ============================================================================
# Test Functions
# ============================================================================

def print_header(text: str):
    """Print colored header"""
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")


def print_category(category: str):
    """Print category header"""
    print(f"\n{Fore.YELLOW}>>> {category} <<<{Style.RESET_ALL}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def test_query(client: BWWClient, query: str, verbose: bool = False) -> dict:
    """
    Test a single query
    
    Args:
        client: BWW Store client
        query: Search query
        verbose: Print detailed results
        
    Returns:
        Test result dictionary
    """
    start_time = time.time()
    
    try:
        results = client.search(query)
        duration = time.time() - start_time
        
        if results is None:
            return {
                'query': query,
                'success': False,
                'error': 'No results returned',
                'duration': duration
            }
        
        result_count = len(results)
        
        if verbose:
            print(f"  Query: '{query}'")
            print(f"  Results: {result_count}")
            print(f"  Duration: {duration:.3f}s")
            if result_count > 0:
                print(f"  First result: {results[0].get('name', 'N/A')}")
            print()
        
        return {
            'query': query,
            'success': True,
            'result_count': result_count,
            'duration': duration,
            'has_results': result_count > 0
        }
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            'query': query,
            'success': False,
            'error': str(e),
            'duration': duration
        }


def test_category(client: BWWClient, category: str, queries: list, verbose: bool = False):
    """Test all queries in a category"""
    print_category(category)
    
    results = []
    for query in queries:
        result = test_query(client, query, verbose)
        results.append(result)
        
        if result['success']:
            if result['has_results']:
                print_success(f"{query} → {result['result_count']} results ({result['duration']:.2f}s)")
            else:
                print_warning(f"{query} → 0 results ({result['duration']:.2f}s)")
        else:
            print_error(f"{query} → Error: {result.get('error', 'Unknown')}")
    
    return results


def print_summary(all_results: dict):
    """Print summary statistics"""
    print_header("Test Summary")
    
    total_queries = 0
    successful = 0
    with_results = 0
    total_duration = 0.0
    
    for category, results in all_results.items():
        for result in results:
            total_queries += 1
            if result['success']:
                successful += 1
                if result.get('has_results', False):
                    with_results += 1
                total_duration += result['duration']
    
    success_rate = (successful / total_queries * 100) if total_queries > 0 else 0
    results_rate = (with_results / total_queries * 100) if total_queries > 0 else 0
    avg_duration = total_duration / total_queries if total_queries > 0 else 0
    
    print(f"Total Queries:    {total_queries}")
    print(f"Successful:       {successful} ({success_rate:.1f}%)")
    print(f"With Results:     {with_results} ({results_rate:.1f}%)")
    print(f"Failed:           {total_queries - successful}")
    print(f"Avg Duration:     {avg_duration:.3f}s")
    print(f"Total Duration:   {total_duration:.3f}s")
    
    # Category breakdown
    print(f"\n{Fore.CYAN}Category Breakdown:{Style.RESET_ALL}\n")
    for category, results in all_results.items():
        cat_total = len(results)
        cat_success = sum(1 for r in results if r['success'] and r.get('has_results', False))
        cat_rate = (cat_success / cat_total * 100) if cat_total > 0 else 0
        print(f"  {category:20} {cat_success}/{cat_total} ({cat_rate:.0f}%)")


def test_egyptian_corrections():
    """Test Egyptian corrections dictionary"""
    print_header("Egyptian Corrections Dictionary")
    
    print(f"Total corrections: {len(EGYPTIAN_CORRECTIONS)}")
    print("\nSample corrections:")
    for i, (egyptian, standard) in enumerate(list(EGYPTIAN_CORRECTIONS.items())[:10]):
        print(f"  '{egyptian}' → '{standard}'")
    
    print("\nCategories covered:")
    categories = {
        'want_expressions': ['عايز', 'عاوز', 'محتاج', 'نفسي'],
        'quality_adjectives': ['حلو', 'جميل', 'جامد', 'شيك'],
        'demonstratives': ['ده', 'دي', 'كده', 'كدا'],
        'colors': ['أحمر', 'أسود', 'أبيض', 'أزرق'],
        'clothing': ['قميص', 'بنطال', 'جاكيت', 'فستان'],
    }
    
    for cat_name, words in categories.items():
        found = sum(1 for w in words if w in EGYPTIAN_CORRECTIONS)
        print(f"  {cat_name:20} {found}/{len(words)} words")


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main test function"""
    print_header("BWW Store - Real Customer Query Testing")
    
    # Test Egyptian corrections dictionary
    test_egyptian_corrections()
    
    # Initialize BWW client
    print_header("Initializing BWW Store Client")
    try:
        client = BWWClient(
            use_cache=True,
            cache_ttl=3600,
            enable_smart_search=True,
            language='ar'
        )
        print_success("BWW Store client initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize client: {e}")
        return
    
    # Test all categories
    print_header("Testing Real Customer Queries")
    
    all_results = {}
    for category, queries in REAL_CUSTOMER_QUERIES.items():
        results = test_category(client, category, queries, verbose=False)
        all_results[category] = results
    
    # Print summary
    print_summary(all_results)
    
    # Test performance
    print_header("Performance Test")
    print("Testing repeated queries for cache effectiveness...")
    
    test_query_perf = "عايز قميص أبيض"
    
    # First call (no cache)
    result1 = test_query(client, test_query_perf)
    print(f"First call:  {result1['duration']:.3f}s")
    
    # Second call (cached)
    result2 = test_query(client, test_query_perf)
    print(f"Second call: {result2['duration']:.3f}s (cached)")
    
    if result1['success'] and result2['success']:
        speedup = result1['duration'] / result2['duration'] if result2['duration'] > 0 else 0
        print(f"Speedup:     {speedup:.1f}x faster")
    
    print(f"\n{Fore.GREEN}✓ Testing completed!{Style.RESET_ALL}\n")


if __name__ == '__main__':
    main()
