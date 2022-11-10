import { useEffect, useState } from "react"
import { useEthers, useContractFunction } from "@usedapp/core"
import { constants, utils } from "ethers"
import TokenFarm from "../chain-info/TokenFarm.json"
import Erc20 from "../chain-info/ERC20.json"
import { Contract } from "@ethersproject/contracts"
// import networkMapping from "../chain-info/map.json"


const networkMapping: { [index: string]: any } = {
    "42": {
        "DappToken": [
            "0xFb581D4d6286D7E2E765E6e22836e8074Aa83085",
            "0x4fED0A880078a8508B9dB158ab42E0554cfFc0d4",
            "0xA346b9458F9706Ab222e0daf7684F370525a6801"
        ],
        "TokenFarm": [
            "0x6871d3713D95d209FAd74F2e1777fBcc47C3b5DA",
            "0xb60Be214603AFBA066C99D9575bBB9f9395F89c0",
            "0x294A900A76116Bd14B8E12922B44562978fFABba"
        ]
    }
}


export const useStakeTokens = (tokenAddress: string) => {
    // address
    // abi
    // chainId
    const { chainId } = useEthers()
    const { abi } = TokenFarm
    const tokenFarmAddress = chainId ? networkMapping[String(chainId)]["TokenFarm"][0] : constants.AddressZero
    const tokenFarmInterface = new utils.Interface(abi)
    const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface)

    const erc20ABI = Erc20.abi
    const erc20Interface = new utils.Interface(erc20ABI)
    const erc20Contract = new Contract(tokenAddress, erc20Interface)
    // approve
    const { send: approveErc20Send, state: approveAndStakeErc20State } =
        useContractFunction(erc20Contract, "approve", {
            transactionName: "Approve ERC20 transfer",
        })
    const approveAndStake = (amount: string) => {
        setAmountToStake(amount)
        return approveErc20Send(tokenFarmAddress, amount)
    }
    // stake
    const { send: stakeSend, state: stakeState } =
        useContractFunction(tokenFarmContract, "stakeTokens", {
            transactionName: "Stake Tokens",
        })
    const [amountToStake, setAmountToStake] = useState("0")

    //useEffect
    useEffect(() => {
        if (approveAndStakeErc20State.status === "Success") {
            stakeSend(amountToStake, tokenAddress)
        }
    }, [approveAndStakeErc20State, amountToStake, tokenAddress])


    const [state, setState] = useState(approveAndStakeErc20State)

    useEffect(() => {
        if (approveAndStakeErc20State.status === "Success") {
            setState(stakeState)
        } else {
            setState(approveAndStakeErc20State)
        }
    }, [approveAndStakeErc20State, stakeState])

    return { approveAndStake, state }
}