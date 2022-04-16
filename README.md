# token-farm

 A smart contract that allows users to stake tokens in a pool and get interest from the token staked and rewarded with an ERC20 token
 
 #### Dependencies
 Metamask
 React
 Brownie
 Node.js
 
 install node.js 
 install metamask(on your web browser) https://metamask.io/download/
 
 Backend
 ```
 Brownie
 pipx install brownie
 ```
 
 Edit the .env file
 ```
export PRIVATE_KEY = YOUR_ACCOUNT_PRIVATE_KEY
export WEB3_INFURA_PROJECT_ID = YOUR_INFURA_PROJECT_ID
export ETHERSCAN_TOKEN = YOUR_ETHERSCAN_TOKEN
 ```
 
 Deploy contracts
 ```
 brownie run scripts/deploy.py --network kovan
 ```
 
 Run the deploy script in the console
 Make sure Brownie is added to path.
 
Run the app
```
cd frontend
npm start
```
 
