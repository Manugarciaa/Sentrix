#!/usr/bin/env python3
"""
Debug the analysis service directly
"""

import sys
import os
import asyncio

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def debug_service():
    """Debug the analysis service directly"""

    try:
        from backend.app.services.analysis_service import analysis_service

        print("=== TESTING SERVICE DIRECTLY ===")

        analysis_id = "1f3b29f0-12ed-4ef5-8f19-c3183cac7886"

        result = await analysis_service.get_analysis_by_id(analysis_id)

        if result:
            print("Service returned:")
            print(f"  has_gps_data: {result.get('has_gps_data')}")
            print(f"  google_maps_url: {result.get('google_maps_url')}")
            print(f"  All keys: {list(result.keys())}")
        else:
            print("Service returned None")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_service())