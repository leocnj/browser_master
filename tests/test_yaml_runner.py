import pytest
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
from src.yaml_runner import YAMLRunner

@pytest.fixture
def mock_files():
    # Mocking axe.min.js and a11y_patch.js content
    file_contents = {
        'axe.min.js': 'console.log("axe");',
        'a11y_patch.js': 'console.log("patch");'
    }
    def side_effect(path, *args, **kwargs):
        for name, content in file_contents.items():
            if name in path:
                return mock_open(read_data=content).return_value
        return mock_open().return_value
        
    return side_effect

def test_yaml_runner_initialization(mock_files):
    with patch("builtins.open", side_effect=mock_files):
        runner = YAMLRunner()
        assert runner.axe_script == 'console.log("axe");'
        assert runner.patch_script == 'console.log("patch");'

def test_render_step(mock_files):
    with patch("builtins.open", side_effect=mock_files):
        runner = YAMLRunner()
        step = {"action": "fill", "value": "{{emp_id}}"}
        params = {"emp_id": "123"}
        rendered = runner._render_step(step, params)
        assert rendered["value"] == "123"

@pytest.mark.asyncio
@patch("src.yaml_runner.expect")
@patch("src.yaml_runner.async_playwright")
async def test_yaml_runner_run(mock_async_p, mock_expect, mock_files):
    with patch("builtins.open", side_effect=mock_files):
        runner = YAMLRunner()

        yaml_content = """
        parameters:
          - name: emp_id
            default: "000"
        steps:
          - action: goto
            url: http://test.com
          - action: fill
            label: ID
            value: "{{emp_id}}"
          - action: verify
            type: text
            value: Success
        """

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=yaml_content)):

            # Setup async mocks for playwright
            mock_p = mock_async_p.return_value.__aenter__.return_value
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_context.add_init_script = AsyncMock()

            mock_page.goto = AsyncMock()
            mock_page.get_by_label = MagicMock()
            mock_page.get_by_label.return_value.fill = AsyncMock()
            mock_page.get_by_text = MagicMock()

            # expect(locator).to_be_visible() is awaited
            mock_expect.return_value.to_be_visible = AsyncMock()
            mock_expect.return_value.to_have_url = AsyncMock()

            success = await runner.run("dummy.yaml", parameters={"emp_id": "456"})

            assert success is True
            mock_page.goto.assert_called_once_with("http://test.com")
            mock_page.get_by_label.assert_called_with("ID")
            mock_page.get_by_label.return_value.fill.assert_called_with("456")
            mock_expect.assert_called()


