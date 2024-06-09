from typing import Callable, Sequence
from unittest.mock import AsyncMock, patch

import pytest

from src.custom_client import CustomClient


class TestSetEmoticonPicker:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_premium, expected_picker",
        [(True, CustomClient._sample), (False, CustomClient._choice)],
    )
    async def test_set_emoticon_picker_premium(
        test_client_for_custom_client: CustomClient,
        is_premium: bool,
        expected_picker: Callable,
    ) -> None:
        mock_user: AsyncMock = AsyncMock()
        mock_user.is_premium = is_premium
        test_client_for_custom_client.is_premium = None
        with patch.object(
            target=test_client_for_custom_client,
            attribute="get_me",
            new_callable=AsyncMock,
        ) as mock_get_me:
            mock_get_me.return_value = mock_user
            await test_client_for_custom_client.set_emoticon_picker()
            assert test_client_for_custom_client.emoticon_picker == expected_picker
        return None


class TestSetPremium:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_premium", [True, False, None])
    async def test_set_premium(
        test_client_for_custom_client: CustomClient, is_premium: bool
    ) -> None:
        mock_user: AsyncMock = AsyncMock()
        mock_user.is_premium = is_premium
        with patch.object(
            target=test_client_for_custom_client,
            attribute="get_me",
            new_callable=AsyncMock,
        ) as mock_get_me:
            mock_get_me.return_value = mock_user
            await test_client_for_custom_client._set_premium()
            if is_premium is None:
                assert test_client_for_custom_client.is_premium is None
            else:
                assert test_client_for_custom_client.is_premium == is_premium
        return None


class TestChoice:
    @staticmethod
    def validate_choice(emoticons: Sequence[str]) -> None:
        chosen_emoticons: Sequence[str] = CustomClient._choice(emoticons=emoticons)
        assert isinstance(chosen_emoticons, Sequence)
        assert len(chosen_emoticons) <= 1
        if chosen_emoticons:
            assert chosen_emoticons[0] in emoticons
        else:
            assert chosen_emoticons == []
        return None

    @classmethod
    @pytest.mark.parametrize(
        "emoticons_fixture",
        [
            "many_emoticons",
            "one_emoticon",
            "no_emoticons",
        ],
    )
    def test_n_of_emoticons_after_choosing(
        cls,
        emoticons_fixture: str,
        request: pytest.FixtureRequest,
    ) -> None:
        emoticons: Sequence[str] = request.getfixturevalue(emoticons_fixture)
        cls.validate_choice(emoticons=emoticons)
        return None


class TestSample:
    @staticmethod
    def validate_sample(emoticons: Sequence[str], expected_length: int) -> None:
        sampled_emoticons: Sequence[str] = CustomClient._sample(emoticons=emoticons)
        assert isinstance(sampled_emoticons, Sequence)
        assert len(sampled_emoticons) == expected_length
        for emoticon in sampled_emoticons:
            assert emoticon in emoticons
        assert len(set(sampled_emoticons)) == len(sampled_emoticons)
        return None

    @classmethod
    @pytest.mark.parametrize(
        "emoticons_fixture, expected_length",
        [
            ("many_emoticons", 3),
            ("three_emoticons", 3),
            ("two_emoticons", 2),
            ("one_emoticon", 1),
            ("no_emoticons", 0),
        ],
    )
    def test_n_of_emoticons_after_sampling(
        cls,
        emoticons_fixture: str,
        expected_length: int,
        request: pytest.FixtureRequest,
    ) -> None:
        emoticons: Sequence[str] = request.getfixturevalue(emoticons_fixture)
        cls.validate_sample(emoticons=emoticons, expected_length=expected_length)
        return None
