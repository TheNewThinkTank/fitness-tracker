
import pytest
from unittest.mock import patch, Mock

import gspread

from test.conftest import src
from src.utils.google_sheet import get_sheet


@patch('src.helpers.google_sheet.gspread.authorize')
@patch('src.helpers.google_sheet.Credentials.from_service_account_file')
def test_get_sheet_success(mock_from_service_account_file, mock_authorize):
    # Arrange
    sheet_id = "test_sheet_id"
    sheet_title = "test_sheet_title"
    
    # Mocking the credentials and gspread client
    mock_creds = Mock()
    mock_client = Mock()
    mock_workbook = Mock()
    mock_sheet = Mock()
    
    mock_from_service_account_file.return_value = mock_creds
    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_workbook
    mock_workbook.worksheet.return_value = mock_sheet

    # Act
    result = get_sheet(sheet_id, sheet_title)
    
    # Assert
    mock_from_service_account_file.assert_called_once_with(
        "local_assets/credentials.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    mock_authorize.assert_called_once_with(mock_creds)
    mock_client.open_by_key.assert_called_once_with(sheet_id)
    mock_workbook.worksheet.assert_called_once_with(sheet_title)
    assert result == mock_sheet


def test_get_sheet_invalid_sheet():
    # This test will check how the function handles an invalid sheet title
    sheet_id = "test_sheet_id"
    sheet_title = "invalid_sheet_title"

    with patch('src.helpers.google_sheet.gspread.authorize') as mock_authorize:
        with patch('src.helpers.google_sheet.Credentials.from_service_account_file') as mock_from_service_account_file:
            mock_creds = Mock()
            mock_client = Mock()
            mock_workbook = Mock()

            mock_from_service_account_file.return_value = mock_creds
            mock_authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_workbook
            mock_workbook.worksheet.side_effect = gspread.exceptions.WorksheetNotFound

            with pytest.raises(gspread.exceptions.WorksheetNotFound):
                get_sheet(sheet_id, sheet_title)

            mock_workbook.worksheet.assert_called_once_with(sheet_title)


if __name__ == "__main__":
    pytest.main()
