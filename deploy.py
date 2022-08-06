from solcx import compile_standard
import json
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()
with open("./SimpleStorage.sol","r") as file:
    simple_storage_file=file.read()

#compile our solidity
compiled_sol=compile_standard(
    {
    "language": "Solidity",
    "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
    "settings":{
        "outputSelection":{
           "*": {
               "*": ["abi","metadata","evm.bytecode","evm.sourceMap"]
           }
        }
     }
    },
    solc_version="0.6.0",
)
print(compiled_sol)

with open("compiled_code.json","w") as file:
     json.dump(compiled_sol, file)

#get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
#get abi
abi=compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
print(abi)
# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id=5777
my_address="0x635e5047bc7D8142d22aBc35c06176D86D80Cf7f"
private_key=os.getenv("PRIVATE_KEY")
print(private_key)
# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi,bytecode=bytecode)
print(SimpleStorage)
# Get the latest transaction
nonce=w3.eth.getTransactionCount(my_address)    
print(nonce)
#1. Build a transaction
#2. Sign a transaction
#3. Send a transaction
transaction=SimpleStorage.constructor().buildTransaction(
       {"chainId":chain_id,"from":my_address,"nonce":nonce}
)
signed_txn= w3.eth.account.sign_transaction(transaction,private_key=private_key)
print(signed_txn)
#send this signed transaction
print("Deploying contract...")
tx_hash=w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# working with the contract,you always need
# Contract address
# Contract ABI
simple_storage=w3.eth.contract(address=tx_receipt.contractAddress,abi=abi)
# Call->Simulate making the call and getting a return value
# Transact->Actually make a state change
#inital value of a favourite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId":chain_id,"from":my_address,"nonce":nonce+1
})
signed_store_txn=w3.eth.account.sign_transaction(store_transaction,private_key=private_key)
send_store_txn=w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt=w3.eth.wait_for_transaction_receipt(send_store_txn)
print("Updated!")
print(simple_storage.functions.retrieve().call())