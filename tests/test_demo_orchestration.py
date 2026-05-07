import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from run_discovery_demo import main

@pytest.mark.asyncio
async def test_main_orchestration():
    # Mock all major components
    with patch('run_discovery_demo.Explorer') as MockExplorer, \
         patch('run_discovery_demo.Hardener') as MockHardener, \
         patch('run_discovery_demo.YAMLRunner') as MockRunner, \
         patch('run_discovery_demo.open', create=True) as mock_open, \
         patch('run_discovery_demo.yaml.dump') as mock_yaml_dump, \
         patch('run_discovery_demo.os.getenv', return_value="fake-key"):

        # Setup Explorer mock
        explorer_instance = MockExplorer.return_value
        explorer_instance.run_task = AsyncMock(return_value=[{"action": "goto", "url": "test.com"}])
        
        # Setup Hardener mock
        hardener_instance = MockHardener.return_value
        hardener_instance.harden = AsyncMock(return_value={
            "parameters": [{"name": "employee_id"}],
            "steps": [{"action": "goto", "url": "test.com"}]
        })
        
        # Setup Runner mock
        runner_instance = MockRunner.return_value
        runner_instance.run = AsyncMock(return_value=True)
        
        # Run the demo's main function
        await main()
        
        # Verify orchestration calls
        MockExplorer.assert_called_once()
        explorer_instance.run_task.assert_called_once()
        MockHardener.assert_called_once_with(context=explorer_instance)
        hardener_instance.harden.assert_called_once()
        mock_yaml_dump.assert_called_once()
        MockRunner.assert_called_once_with(headless=True)
        runner_instance.run.assert_called_once()

if __name__ == "__main__":
    asyncio.run(test_main_orchestration())
