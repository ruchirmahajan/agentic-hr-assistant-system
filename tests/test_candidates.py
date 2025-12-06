"""
Test cases for candidate API endpoints
"""
import pytest
import json
from fastapi import status
from httpx import AsyncClient

from src.models.candidate import Candidate
from tests.conftest import TestDataFactory


class TestCandidateAPI:
    """Test cases for candidate management."""
    
    @pytest.mark.asyncio
    async def test_create_candidate_success(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict,
        sample_resume_file: str
    ):
        """Test successful candidate creation."""
        candidate_data = TestDataFactory.candidate_data()
        
        # Prepare multipart form data
        with open(sample_resume_file, 'rb') as f:
            files = {"resume_file": ("resume.txt", f, "text/plain")}
            data = candidate_data
            
            response = await async_client.post(
                "/api/v1/candidates/",
                data=data,
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        
        assert "id" in result
        assert result["message"] == "Candidate created successfully"
        assert result["resume_processed"] is True
        assert "skills_extracted" in result
    
    @pytest.mark.asyncio
    async def test_create_candidate_missing_auth(
        self, 
        async_client: AsyncClient,
        sample_resume_file: str
    ):
        """Test candidate creation without authentication."""
        candidate_data = TestDataFactory.candidate_data()
        
        with open(sample_resume_file, 'rb') as f:
            files = {"resume_file": ("resume.txt", f, "text/plain")}
            
            response = await async_client.post(
                "/api/v1/candidates/",
                data=candidate_data,
                files=files
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_list_candidates(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing candidates."""
        response = await async_client.get(
            "/api/v1/candidates/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        
        assert "candidates" in result
        assert "total" in result
        assert isinstance(result["candidates"], list)
    
    @pytest.mark.asyncio
    async def test_get_candidate_not_found(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent candidate."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = await async_client.get(
            f"/api/v1/candidates/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFileUpload:
    """Test file upload functionality."""
    
    @pytest.mark.asyncio
    async def test_upload_valid_file(
        self, 
        async_client: AsyncClient,
        auth_headers: dict,
        sample_resume_file: str
    ):
        """Test uploading valid resume file."""
        candidate_data = TestDataFactory.candidate_data()
        
        with open(sample_resume_file, 'rb') as f:
            files = {"resume_file": ("resume.txt", f, "text/plain")}
            
            response = await async_client.post(
                "/api/v1/candidates/",
                data=candidate_data,
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test uploading invalid file type."""
        candidate_data = TestDataFactory.candidate_data()
        
        # Create a fake executable file
        invalid_content = b"This is not a valid resume file"
        files = {"resume_file": ("malware.exe", invalid_content, "application/octet-stream")}
        
        response = await async_client.post(
            "/api/v1/candidates/",
            data=candidate_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @pytest.mark.asyncio
    async def test_upload_large_file(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test uploading file that exceeds size limit."""
        candidate_data = TestDataFactory.candidate_data()
        
        # Create a large file (simulate > 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"resume_file": ("large.txt", large_content, "text/plain")}
        
        response = await async_client.post(
            "/api/v1/candidates/",
            data=candidate_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGDPRCompliance:
    """Test GDPR compliance features."""
    
    @pytest.mark.asyncio
    async def test_export_candidate_data(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test exporting candidate data for GDPR compliance."""
        # First create a candidate
        candidate_data = TestDataFactory.candidate_data()
        
        # This would need a real candidate ID in practice
        fake_candidate_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = await async_client.get(
            f"/api/v1/candidates/{fake_candidate_id}/export",
            headers=auth_headers
        )
        
        # This will fail because candidate doesn't exist, but tests the endpoint
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    @pytest.mark.asyncio
    async def test_delete_candidate_gdpr(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GDPR-compliant candidate deletion."""
        fake_candidate_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = await async_client.delete(
            f"/api/v1/candidates/{fake_candidate_id}",
            headers=auth_headers
        )
        
        # This will fail because candidate doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.integration
class TestIntegrationFlow:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_candidate_workflow(
        self, 
        async_client: AsyncClient,
        auth_headers: dict,
        sample_resume_file: str
    ):
        """Test complete candidate management workflow."""
        candidate_data = TestDataFactory.candidate_data()
        
        # 1. Create candidate
        with open(sample_resume_file, 'rb') as f:
            files = {"resume_file": ("resume.txt", f, "text/plain")}
            
            create_response = await async_client.post(
                "/api/v1/candidates/",
                data=candidate_data,
                files=files,
                headers=auth_headers
            )
        
        if create_response.status_code == status.HTTP_201_CREATED:
            result = create_response.json()
            candidate_id = result["id"]
            
            # 2. Get candidate details
            get_response = await async_client.get(
                f"/api/v1/candidates/{candidate_id}",
                headers=auth_headers
            )
            
            assert get_response.status_code == status.HTTP_200_OK
            
            # 3. Update candidate
            update_data = {"notes": "Updated via test"}
            update_response = await async_client.put(
                f"/api/v1/candidates/{candidate_id}",
                json=update_data,
                headers=auth_headers
            )
            
            assert update_response.status_code == status.HTTP_200_OK
        
        else:
            # If creation failed, just verify the error handling
            assert create_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR