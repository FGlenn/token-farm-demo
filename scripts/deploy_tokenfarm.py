from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm
from web3 import Web3
import yaml
import json
import os
import shutil


def main():
    deploy_token_farm_and_token(frond_end_update=True)


KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_token(frond_end_update=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address, {"from": account}, publish_source=False
    )
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    #
    dictionairy_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dictionairy_of_allowed_tokens, account)
    if update_front_end():
        update_front_end()
    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dictionairy_of_allowed_tokens, account):
    for token in dictionairy_of_allowed_tokens:
        add_allowed_token_tx = token_farm.addAllowedToken(
            token.address, {"from": account}
        )
        add_allowed_token_tx.wait(1)
        set_pricefeed_tx = token_farm.setPriceFeedContract(
            token.address, dictionairy_of_allowed_tokens[token], {"from": account}
        )
        set_pricefeed_tx.wait(1)
    return token_farm


def update_front_end():
    print("Updating front end...")
    # The Build
    copy_folders_to_front_end("./build/contracts", "./front_end/src/chain-info")

    # The Contracts
    copy_folders_to_front_end("./contracts", "./front_end/src/contracts")

    # The ERC20
    copy_files_to_front_end(
        "./build/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.6.0/ERC20.json",
        "./front_end/src/chain-info/ERC20.json",
    )
    # The Map
    copy_files_to_front_end(
        "./build/deployments/map.json",
        "./front_end/src/chain-info/map.json",
    )

    # The Config, converted from YAML to JSON
    # This function loads the .yaml file into a dictionairy and dumps it into .json format  so our front_end can use it.
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(scr, dest):
    # If the path already exists in front_end, then remove it.
    if os.path.exists(dest):
        shutil.rmtree(dest)
    # If it doesn't exist, copy from the build folder.
    shutil.copytree(scr, dest)


def copy_files_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copyfile(src, dest)
