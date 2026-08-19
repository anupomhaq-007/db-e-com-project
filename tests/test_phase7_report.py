"""
Phase 7 Advanced DBMS Capabilities, Reporting & Visualizers Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client

def test_phase7_report():
    print("==================================================")
    print("  PHASE 7 ADVANCED DBMS REPORT & VISUALIZERS TEST")
    print("==================================================")

    client = Client()

    # 1. Test Report Portal GET
    response = client.get('/report/')
    print(f"✔ Report Portal GET HTTP Status: {response.status_code}")
    assert response.status_code == 200, "Report portal GET failed"

    content = response.content.decode('utf-8')

    # 2. Verify RAID-4 Visualizer Engine presence
    assert "RAID-4 Block-Level Striping" in content or "RAID-4 Storage Engine" in content
    assert "Dedicated Parity" in content or "Parity Disk" in content
    print("✔ RAID-4 Storage Engine & XOR Parity Simulator verified!")

    # 3. Verify B+ Tree Indexing Engine presence
    assert "B+ Tree" in content
    assert "ROOT NODE" in content
    print("✔ B+ Tree Indexing Architecture Engine verified!")

    # 4. Verify Final Report & Academic Metadata
    assert "Database System Live Record Metrics" in content
    assert "22025214" in content
    assert "Independent University Bangladesh" in content
    print("✔ Final Lab System Report & Academic Metadata verified!")

    print("==================================================")
    print("RESULT: Phase 7 Advanced DBMS Report Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_phase7_report()
