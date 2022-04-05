//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

//ToDOS
//Stake tokens -- done
//Unstake tokens
//Issue tokens -- done
//Add more allowed tokens -- done
//Get Ethvalue -- done

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    //Mapping token address to staker address - amount
    mapping(address => mapping(address => uint256)) public stakingBalance;
    //An array of tokens 'types' that can be stake
    address[] public allowedTokens;
    //An array of stakers
    address[] public stakers;
    //A mapping of each unique token staked per sender(eth, etc)
    mapping(address => uint256) public UniqueTokensStaked;

    //token address to priceFeed address mapping to get chainlink priceFeed for each token
    mapping(address => address) public tokenPriceFeedMapping;

    IERC20 public dappToken;

    constructor(address _dappTokenAddress) {
        //Our dapp reward token
        dappToken = IERC20(_dappTokenAddress);
    }

    //This function  sets the token to price feed address when a token is added
    function setPriceFeedTokenMapping(address token, address priceFeed) public {
        tokenPriceFeedMapping[token] = priceFeed;
    }

    //issues dapp reward tokenss
    function issueTokens() public onlyOwner {
        //for each staker in the array
        //get the value of the stakers stake
        //issue a reward based on that value
        for (
            uint256 stakersIndex = 0;
            stakers.length > stakersIndex;
            stakersIndex++
        ) {
            address receipient = stakers[stakersIndex];
            uint256 userTotalValue = getUserTotalValue(receipient);

            //send them a token reward based on their total staked value
            dappToken.transfer(receipient, userTotalValue);
        }
    }

    //This function gets the total value of the tokens staked bring them to a single unit token/usd value

    function getUserTotalValue(address user) public view returns (uint256) {
        uint256 totalValue = 0;
        require(UniqueTokensStaked[user] > 0, "No tokens staked");
        //for every total value of the a token staked by a specified user add it to the totalValue and return it
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokens.length > allowedTokensIndex;
            allowedTokensIndex++
        ) {
            totalValue =
                totalValue +
                getValueOfUsersTokenAmount(
                    user,
                    allowedTokens[allowedTokensIndex]
                );
            return totalValue;
        }
    }

    function getValueOfUsersTokenAmount(address user, address token)
        public
        view
        returns (uint256)
    {
        //No unique tokens staked
        if (UniqueTokensStaked[user] <= 0) {
            return 0;
        }

        //Unique token staked

        //get the usd value of the current token (used in the for loop for getUserTotalValue)
        (uint256 price, uint256 decimals) = getTokenValue(token);

        //return the converted value
        return ((stakingBalance[token][user] * price) / 10**decimals);

        //price of the token
    }

    //this function gets the usd/token value for a particular token and returns its decimals and price in unit256
    function getTokenValue(address token)
        public
        view
        returns (uint256, uint256)
    {
        //priceFeed address
        address priceFeedAddress = tokenPriceFeedMapping[token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );

        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = priceFeed.decimals();
        return (uint256(price), uint256(decimals));
    }

    //Function to stake tokens

    function stakeTokens(uint256 _amount, address _token) public {
        //what token can they stake
        require(_amount > 0, "Amount must be more than 0");
        require(tokenIsAllowed(_token), "Token is not allowed");

        //how much can they stake
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] =
            stakingBalance[_token][msg.sender] +
            _amount;
        if (UniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function unstakeTokens(address _token) public {
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "Staking balance is 0");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        UniqueTokensStaked[msg.sender] = UniqueTokensStaked[msg.sender] - 1;
    }

    function updateUniqueTokensStaked(address user, address token) internal {
        if (stakingBalance[token][user] <= 0) {
            UniqueTokensStaked[user] = UniqueTokensStaked[user] + 1;
        }
    }

    //Function to add token types which can be staked to the token array
    function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    //Test if the token given as a param is allowed for staking
    function tokenIsAllowed(address _token) public returns (bool) {
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokens.length > allowedTokensIndex;
            allowedTokensIndex++
        ) {
            if (allowedTokens[allowedTokensIndex] == _token) {
                return true;
            }
        }
        return false;
    }
}
