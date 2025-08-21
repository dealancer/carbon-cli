import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConfig:
    """Test configuration functions."""
    
    @patch('config.boto3.session.Session')
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY': 'test-key',
        'AWS_SECRET_KEY': 'test-secret'
    })
    def test_get_s3_client(self, mock_session):
        from config import get_s3_client
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        result = get_s3_client()
        
        mock_session.assert_called_once()
        assert result == mock_client

    @patch('config.get_s3_client')
    @patch.dict(os.environ, {
        'AWS_BUCKET': 'test-bucket',
        'CARBON_PROJECT': 'test-project'
    })
    def test_get_config_exists(self, mock_get_s3_client):
        from config import get_config
        mock_s3_client = MagicMock()
        mock_get_s3_client.return_value = mock_s3_client
        
        test_config = {'assistant_id': 'test-assistant-123'}
        mock_response = {
            'Body': MagicMock()
        }
        mock_response['Body'].read.return_value = json.dumps(test_config).encode()
        mock_s3_client.get_object.return_value = mock_response
        
        result = get_config()
        assert result == test_config

    @patch('config.get_s3_client')
    @patch.dict(os.environ, {
        'AWS_BUCKET': 'test-bucket',
        'CARBON_PROJECT': 'test-project'
    })
    def test_get_config_not_exists(self, mock_get_s3_client):
        from config import get_config
        mock_s3_client = MagicMock()
        mock_get_s3_client.return_value = mock_s3_client
        mock_s3_client.get_object.side_effect = Exception("NoSuchKey")
        
        result = get_config()
        assert result == {}

    @patch('config.get_s3_client')
    @patch.dict(os.environ, {
        'AWS_BUCKET': 'test-bucket',
        'CARBON_PROJECT': 'test-project'
    })
    def test_save_config(self, mock_get_s3_client):
        from config import save_config
        mock_s3_client = MagicMock()
        mock_get_s3_client.return_value = mock_s3_client
        
        test_config = {'assistant_id': 'new-assistant-456'}
        save_config(test_config)
        
        mock_s3_client.put_object.assert_called_once()


class TestAI:
    """Test AI functions."""
    
    @patch('ai.get_config')
    @patch('ai.ai_client')
    def test_get_assistant_exists(self, mock_ai_client, mock_get_config):
        from ai import get_assistant
        mock_get_config.return_value = {'assistant_id': 'existing-assistant-123'}
        
        result = get_assistant()
        
        assert result == 'existing-assistant-123'
        mock_ai_client.beta.assistants.update.assert_called_once()

    @patch('ai.get_config')
    @patch('ai.save_config')
    @patch('ai.ai_client')
    def test_get_assistant_create_new(self, mock_ai_client, mock_save_config, mock_get_config):
        from ai import get_assistant
        mock_get_config.return_value = {}
        mock_assistant = MagicMock()
        mock_assistant.id = 'new-assistant-456'
        mock_ai_client.beta.assistants.create.return_value = mock_assistant
        
        result = get_assistant()
        
        assert result == 'new-assistant-456'
        mock_ai_client.beta.assistants.create.assert_called_once()
        mock_save_config.assert_called_once_with({'assistant_id': 'new-assistant-456'})

    @patch.dict(os.environ, {
        'CARBON_WORK_DIR': '/test/work',
        'CARBON_PROJECT_FILENAME': 'test-project.zip'
    })
    @patch('ai.ai_client')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test file content')
    def test_upload_file(self, mock_file, mock_ai_client):
        from ai import upload_file
        mock_file_object = MagicMock()
        mock_file_object.id = 'file-123'
        mock_ai_client.files.create.return_value = mock_file_object
        
        result = upload_file()
        
        assert result == 'file-123'
        mock_ai_client.files.create.assert_called_once()

    @patch('ai.get_assistant')
    @patch('ai.process_thread')
    @patch('ai.ai_client')
    def test_run_thread_success(self, mock_ai_client, mock_process_thread, mock_get_assistant):
        from ai import run_thread
        mock_get_assistant.return_value = 'assistant-123'
        mock_run = MagicMock()
        mock_run.status = 'completed'
        mock_run.id = 'run-456'
        mock_ai_client.beta.threads.runs.create_and_poll.return_value = mock_run
        
        run_thread('thread-123')
        
        mock_ai_client.beta.threads.runs.create_and_poll.assert_called_once_with(
            assistant_id='assistant-123',
            thread_id='thread-123'
        )
        mock_process_thread.assert_called_once_with('thread-123', 'run-456')

    @patch.dict(os.environ, {
        'CARBON_WORK_DIR': '/test/work'
    })
    @patch('ai.ai_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_save_file_success(self, mock_print, mock_file, mock_ai_client):
        from ai import save_file
        mock_content = MagicMock()
        mock_content.read.return_value = b'test file data'
        mock_ai_client.files.content.return_value = mock_content
        
        result = save_file('file-123', 'test.txt')
        
        # The function returns a relative path from the work directory
        assert 'test.txt' in result
        mock_ai_client.files.content.assert_called_once_with(file_id='file-123')

    @patch.dict(os.environ, {
        'CARBON_WORK_DIR': '/test/work'
    })
    @patch('ai.ai_client')
    @patch('builtins.print')
    def test_save_file_failure(self, mock_print, mock_ai_client):
        from ai import save_file
        mock_ai_client.files.content.side_effect = Exception('Network error')
        
        result = save_file('file-123', 'test.txt')
        
        assert result is None


class TestMain:
    """Test main CLI function."""
    
    @patch('run.validate_vars')
    @patch('run.create_thread_for_issue')
    def test_main_create_issue(self, mock_create_thread, mock_validate_vars):
        from run import main
        test_args = ['run.py', 'create', 'issue']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_PROJECT_FILENAME",
            "CARBON_REQUEST", 
            "CARBON_ISSUE_ID"
        ])
        mock_create_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.map_thread_to_pr_out_of_issue')
    def test_main_map_pr(self, mock_map_thread, mock_validate_vars):
        from run import main
        test_args = ['run.py', 'map', 'pr']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_ISSUE_ID",
            "CARBON_PR_ID"
        ])
        mock_map_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.update_thread_for_issue')
    def test_main_update_issue(self, mock_update_thread, mock_validate_vars):
        from run import main
        test_args = ['run.py', 'update', 'issue']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_ISSUE_ID",
            "CARBON_REQUEST"
        ])
        mock_update_thread.assert_called_once()

    def test_main_insufficient_args(self):
        from run import main
        test_args = ['run.py']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="No command or object provided"):
                main()

    def test_main_invalid_command(self):
        from run import main
        test_args = ['run.py', 'invalid', 'issue']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="Invalid command 'invalid' or object 'issue' provided"):
                main()


class TestIntegration:
    """Integration tests for common workflows."""
    
    @patch('ai.get_config')
    @patch('ai.save_config')
    @patch('ai.upload_file')
    @patch('ai.run_thread')
    @patch('ai.ai_client')
    @patch.dict(os.environ, {
        'CARBON_ISSUE_ID': 'issue-123',
        'CARBON_REQUEST': 'Test request'
    })
    def test_create_issue_workflow(self, mock_ai_client, mock_run_thread, 
                                 mock_upload_file, mock_save_config, mock_get_config):
        from ai import create_thread_for_issue
        
        # Setup mocks
        mock_get_config.return_value = {}
        mock_upload_file.return_value = 'file-123'
        mock_thread = MagicMock()
        mock_thread.id = 'thread-456'
        mock_ai_client.beta.threads.create.return_value = mock_thread
        
        # Execute workflow
        create_thread_for_issue()
        
        # Verify the workflow
        mock_upload_file.assert_called_once()
        mock_ai_client.beta.threads.create.assert_called_once()
        assert mock_run_thread.call_count == 3  # Called 3 times in the workflow
        mock_save_config.assert_called_once()
        
        # Verify final config state - the function should save some config
        mock_save_config.assert_called_once()
        saved_config = mock_save_config.call_args[0][0]
        assert 'threads_by_issue' in saved_config