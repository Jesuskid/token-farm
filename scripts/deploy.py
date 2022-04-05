import json
from brownie import accounts, config, network, DappToken, TokenFarm
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3
import yaml
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp(frontend_update=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)

    # dapp, weth, fau/dai
    weth_token = get_contract("weth_token")
    print(weth_token)
    fau_token = get_contract("fau_token")

    dict_of_allowed_tokens = {
        dapp_token: get_contract("eth_usd_price_feed"),
        weth_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    if frontend_update:
        update_fontend()

    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_allowed_tokens, account):
    for token in dict_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)

        set_tx = token_farm.setPriceFeedTokenMapping(
            token.address, dict_allowed_tokens[token]
        )
        set_tx.wait(1)
        print("set tokens adn price feeds")
        return token_farm


def update_fontend():
    # send the build folder
    copy_folder("./build", "./front_end/src/chain-info")

    # send the yaml file to front end
    with open("brownie-config.yaml", "r") as b_config:
        config_dict = yaml.load(b_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie_config.json", "w") as bjson:
            json.dump(config_dict, bjson)


def copy_folder(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp(frontend_update=True)
