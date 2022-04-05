from scripts.deploy import deploy_token_farm_and_dapp
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHIANS_ENV,
    get_account,
    get_contract,
    STARTING_PRICE,
)
from brownie import network, exceptions
import pytest
from web3 import Web3


def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHIANS_ENV:
        pytest.skip()
    account = get_account()
    no_owner_account = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp()
    price_feed_address = get_contract("eth_usd_price_feed")
    # Act
    token_farm.setPriceFeedTokenMapping(
        dapp_token.address, price_feed_address, {"from": account}
    )

    # assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address

    # non owners can't call set dapp token
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedTokenMapping(
            dapp_token.address, price_feed_address, {"from": no_owner_account}
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHIANS_ENV:
        pytest.skip()
    account = get_account()
    no_owner_account = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp()

    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})

    # Assert
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )

    assert token_farm.UniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHIANS_ENV:
        pytest.skip()
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    token_farm.issueTokens({"from": account})

    # Arrange
    assert dapp_token.balanceOf(account.address) == starting_balance + STARTING_PRICE
