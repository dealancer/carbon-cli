import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from run import main


class TestMain:
    @patch('run.validate_vars')
    @patch('run.create_thread_for_issue')
    def test_main_create_issue(self, mock_create_thread, mock_validate_vars):
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
        test_args = ['run.py', 'update', 'issue']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_ISSUE_ID",
            "CARBON_REQUEST"
        ])
        mock_update_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.update_thread_for_pr')
    def test_main_update_pr(self, mock_update_thread, mock_validate_vars):
        test_args = ['run.py', 'update', 'pr']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_PR_ID",
            "CARBON_REQUEST"
        ])
        mock_update_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.get_thread_by_issue')
    def test_main_retrieve_issue(self, mock_get_thread, mock_validate_vars):
        test_args = ['run.py', 'retrieve', 'issue']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_ISSUE_ID"
        ])
        mock_get_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.get_thread_by_pr')
    def test_main_retrieve_pr(self, mock_get_thread, mock_validate_vars):
        test_args = ['run.py', 'retrieve', 'pr']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_PR_ID"
        ])
        mock_get_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.delete_thread_for_issue')
    def test_main_delete_issue(self, mock_delete_thread, mock_validate_vars):
        test_args = ['run.py', 'delete', 'issue']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_ISSUE_ID"
        ])
        mock_delete_thread.assert_called_once()

    @patch('run.validate_vars')
    @patch('run.delete_thread_for_pr')
    def test_main_delete_pr(self, mock_delete_thread, mock_validate_vars):
        test_args = ['run.py', 'delete', 'pr']
        with patch.object(sys, 'argv', test_args):
            main()
        
        mock_validate_vars.assert_called_once_with([
            "CARBON_PR_ID"
        ])
        mock_delete_thread.assert_called_once()

    def test_main_insufficient_args(self):
        test_args = ['run.py']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="No command or object provided"):
                main()

    def test_main_one_arg_only(self):
        test_args = ['run.py', 'create']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="No command or object provided"):
                main()

    def test_main_invalid_command(self):
        test_args = ['run.py', 'invalid', 'issue']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="Invalid command 'invalid' or object 'issue' provided"):
                main()

    def test_main_invalid_object(self):
        test_args = ['run.py', 'create', 'invalid']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="Invalid command 'create' or object 'invalid' provided"):
                main()

    def test_main_invalid_command_object_combination(self):
        test_args = ['run.py', 'map', 'issue']
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(ValueError, match="Invalid command 'map' or object 'issue' provided"):
                main()