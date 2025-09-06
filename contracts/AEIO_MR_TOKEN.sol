// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.0.1/contracts/token/ERC20/ERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.0.1/contracts/access/Ownable.sol";

/**
 * @title AEIO_MR_TOKEN
 * @dev The official currency of the Arkaios, Ethora, and Amerio ecosystem.
 * A fixed-supply ERC20 token where the entire supply is minted to the deployer.
 * This token will be the lifeblood of the IA Governed DAO.
 */
contract AEIO_MR_TOKEN is ERC20, Ownable {
    uint256 public constant INITIAL_SUPPLY = 1_000_000_000 * (10 ** 18); // 1 Billion tokens

    constructor(address initialOwner) ERC20("Arkaios Ethora Amerio Omnitoken", "AEIO-MR") Ownable(initialOwner) {
        _mint(msg.sender, INITIAL_SUPPLY);
    }
}
