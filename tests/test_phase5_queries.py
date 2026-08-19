"""
Phase 5 Analytical SQL Queries Center Test (Task-2 Queries a-j)
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from store.views import QUERY_CATALOG

def test_phase5_queries():
    print("==================================================")
    print("  PHASE 5 ANALYTICAL SQL QUERIES CENTER TEST (a-j)")
    print("==================================================")

    client = Client()

    # 1. Test Queries Index View GET
    response_index = client.get('/queries/')
    print(f"✔ Queries Portal Main GET Status: {response_index.status_code}")
    assert response_index.status_code == 200, "Queries GET failed"
    content = response_index.content.decode('utf-8')
    assert "Analytical SQL Queries Center" in content

    # 2. Iterate through all 10 mandatory queries (a to j) and verify response & data execution
    for q_key, q_info in QUERY_CATALOG.items():
        url = f"/queries/?query={q_key}"
        response = client.get(url)
        assert response.status_code == 200, f"Query '{q_key}' failed with status {response.status_code}"
        res_content = response.content.decode('utf-8')
        
        # Verify query title and SQL string presence
        assert q_info['title'] in res_content, f"Title missing for query {q_key}"
        assert "Query Output Data Table" in res_content, f"Data table missing for query {q_key}"
        assert "Execution Error" not in res_content, f"Query '{q_key}' raised SQL execution error"
        
        print(f"✔ Query ({q_key.upper()}): '{q_info['title']}' executed successfully against Neon PostgreSQL!")

    # 3. Test Custom SQL Runner POST
    custom_sql_payload = {
        'query': 'custom',
        'custom_sql': 'SELECT product_id, name, price FROM store_product WHERE price > 500 ORDER BY price DESC;'
    }
    response_custom = client.post('/queries/', custom_sql_payload)
    print(f"✔ Custom SQL Runner POST Status: {response_custom.status_code}")
    assert response_custom.status_code == 200
    custom_content = response_custom.content.decode('utf-8')
    assert "Custom Ad-Hoc SQL Runner" in custom_content
    assert "Execution Error" not in custom_content

    print("==================================================")
    print("RESULT: Phase 5 Analytical SQL Queries Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_phase5_queries()
