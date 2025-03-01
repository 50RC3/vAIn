import pytest
from pathlib import Path
import sys
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from api.main import app
from core.self_improvement import SelfImprovementModule 
from modules.analytics.insights import AnalyticsEngine
from services.p2p.network import P2PNetwork

class TestModuleIntegration:
    @pytest.fixture
    async def setup_modules(self):
        """Initialize core modules for testing"""
        self.p2p = P2PNetwork()
        self.analytics = AnalyticsEngine()
        self.agent = SelfImprovementModule(
            meta_learner=None,
            knowledge_graph=None, 
            nas=None
        )
        yield
        # Cleanup
        await self.p2p.shutdown()
        
    @pytest.mark.asyncio
    async def test_core_api_integration(self, setup_modules):
        """Test core API endpoints integration"""
        response = await app.test_client().get("/api/v1/nodes")
        assert response.status_code == 200
        
    @pytest.mark.asyncio
    async def test_p2p_communication(self, setup_modules):
        """Test P2P network communication"""
        connected = await self.p2p.connect()
        assert connected == True
