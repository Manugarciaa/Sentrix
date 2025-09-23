#!/usr/bin/env python3
"""
Simple test runner for basic functionality
"""

import os
import sys
import pytest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test if basic modules can be imported"""
    try:
        # Test basic Python functionality
        import json
        import datetime
        assert True
        print("OK Basic Python imports work")
    except Exception as e:
        print(f"FAIL Basic imports failed: {e}")
        assert False

def test_pydantic_models():
    """Test basic Pydantic model functionality"""
    try:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42
        print("OK Pydantic models work")
    except Exception as e:
        print(f"FAIL Pydantic test failed: {e}")
        assert False

def test_sqlalchemy_basic():
    """Test basic SQLAlchemy functionality"""
    try:
        from sqlalchemy import Column, Integer, String, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        Base = declarative_base()

        class TestTable(Base):
            __tablename__ = 'test_table'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        # Use SQLite in-memory database for testing
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Test basic operations
        test_item = TestTable(name="test")
        session.add(test_item)
        session.commit()

        result = session.query(TestTable).first()
        assert result.name == "test"

        session.close()
        print("OK SQLAlchemy basic functionality works")
    except Exception as e:
        print(f"FAIL SQLAlchemy test failed: {e}")
        assert False

def test_fastapi_basic():
    """Test basic FastAPI functionality"""
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "test"}
        print("OK FastAPI basic functionality works")
    except Exception as e:
        print(f"FAIL FastAPI test failed: {e}")
        assert False

if __name__ == "__main__":
    print("Running basic functionality tests...")

    test_basic_imports()
    test_pydantic_models()
    test_sqlalchemy_basic()
    test_fastapi_basic()

    print("\nOK All basic tests passed!")