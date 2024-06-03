from http import HTTPStatus

import pytest


@pytest.mark.asyncio
def test_get_auth_history_returns_unauthorized_if_no_token(make_get_request) -> None:
    response = await make_get_request("/api/v1/auth/history")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
