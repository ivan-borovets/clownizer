from typing import Sequence
from unittest.mock import AsyncMock, patch

import pytest

from custom_client import CustomClient


class TestSetEmoticonPicker:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_premium, expected_picker",
        [(True, CustomClient._sample), (False, CustomClient._choice)],
    )
    async def test_set_emoticon_picker_premium(
        test_client, is_premium, expected_picker
    ) -> None:
        mock_user = AsyncMock()
        mock_user.is_premium = is_premium
        test_client.is_premium = None
        with patch.object(
            target=test_client, attribute="get_me", new_callable=AsyncMock
        ) as mock_get_me:
            mock_get_me.return_value = mock_user
            await test_client.set_emoticon_picker()
            assert test_client.emoticon_picker == expected_picker


class TestSetPremium:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_premium", [True, False, None])
    async def test_set_premium(test_client: CustomClient, is_premium) -> None:
        mock_user = AsyncMock()
        mock_user.is_premium = is_premium
        with patch.object(
            target=test_client, attribute="get_me", new_callable=AsyncMock
        ) as mock_get_me:
            mock_get_me.return_value = mock_user
            await test_client._set_premium()
            if is_premium is None:
                assert test_client.is_premium is None
            else:
                assert test_client.is_premium == is_premium


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

    @classmethod
    def test_returns_one_emoticon_if_gt_one(cls, many_emoticons) -> None:
        cls.validate_choice(emoticons=many_emoticons)

    @classmethod
    def test_returns_one_emoticon_if_one(cls, one_emoticon) -> None:
        cls.validate_choice(emoticons=one_emoticon)

    @classmethod
    def test_returns_empty_if_empty(cls, no_emoticons) -> None:
        cls.validate_choice(emoticons=no_emoticons)


class TestSample:
    @staticmethod
    def validate_sample(emoticons: Sequence[str], expected_length: int) -> None:
        sampled_emoticons: Sequence[str] = CustomClient._sample(emoticons=emoticons)
        assert isinstance(sampled_emoticons, Sequence)
        assert len(sampled_emoticons) == expected_length
        for emoticon in sampled_emoticons:
            assert emoticon in emoticons
        assert len(set(sampled_emoticons)) == len(sampled_emoticons)

    @classmethod
    def test_returns_three_emoticons_if_gt_three(
        cls, many_emoticons: Sequence[str]
    ) -> None:
        cls.validate_sample(emoticons=many_emoticons, expected_length=3)

    @classmethod
    def test_returns_three_emoticons_if_three(
        cls, three_emoticons: Sequence[str]
    ) -> None:
        cls.validate_sample(emoticons=three_emoticons, expected_length=3)

    @classmethod
    def test_returns_two_emoticons_if_two(cls, two_emoticons: Sequence[str]) -> None:
        cls.validate_sample(emoticons=two_emoticons, expected_length=2)

    @classmethod
    def test_returns_one_emoticon_if_one(cls, one_emoticon: Sequence[str]) -> None:
        cls.validate_sample(emoticons=one_emoticon, expected_length=1)

    @classmethod
    def test_returns_empty_if_empty(cls, no_emoticons: Sequence[str]) -> None:
        cls.validate_sample(emoticons=no_emoticons, expected_length=0)
