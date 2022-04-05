from brownie import (
    accounts,
    config,
    network,
    Contract,
    MockDai,
    MockWeth,
    MockV3Aggregator,
)

FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHIANS_ENV = ["development", "ganache-local"]
DECIMALS = 8
STARTING_PRICE = 2000000000000000000000


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHIANS_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


mock_contracts = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDai,
    "weth_token": MockWeth,
}


def get_contract(c_name):
    """This function will grab the contract addresses
    from the brownie config if defined otherwise it deploys a mock version
    of that contract and returns a mock contract

    args:
       contractname (string)

    Returns:
       brownie.network.contract.ProjectContract: most recently deployed version of the mock contract

    """
    contract_type = mock_contracts[c_name]
    if network.show_active() in LOCAL_BLOCKCHIANS_ENV:
        print(f"{c_name}")
        if len(contract_type) <= 0:
            deploy_mocks()
        # cv = mock_contracts["dai_usd_price_feed"]
        # print(f"000 cv contract {cv[-1]}")
        contract = contract_type[-1]
    else:
        contract_add = config["networks"][network.show_active()][c_name]
        contract = Contract.from_abi(
            contract_type._name, contract_add, contract_type.abi
        )

    return contract


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks")
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    print("MockV3Agg... Deployed")
    print("Deploying Mock Dai")
    dai_token = MockDai.deploy({"from": account})
    print(f"Mock dai deployed to {dai_token.address}")

    print("Deploying Mock Weth")
    weth_token = MockWeth.deploy({"from": account})
    print(f"Mock weth deployed to {weth_token.address}")
