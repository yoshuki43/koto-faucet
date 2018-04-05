import requests
import json
import base58
import logging
import inspect

class KOTO:
	DEFAULT_FEE = 0.0001

class KotoRPCErrorCode:
    #//! Standard JSON-RPC 2.0 errors
    RPC_INVALID_REQUEST  = -32600
    RPC_METHOD_NOT_FOUND = -32601
    RPC_INVALID_PARAMS   = -32602
    RPC_INTERNAL_ERROR   = -32603
    RPC_PARSE_ERROR      = -32700
    
    #//! General application defined errors
    RPC_MISC_ERROR                  = -1  #//! std::exception thrown in command handling
    RPC_FORBIDDEN_BY_SAFE_MODE      = -2  #//! Server is in safe mode and command is not allowed in safe mode
    RPC_TYPE_ERROR                  = -3  #//! Unexpected type was passed as parameter
    RPC_INVALID_ADDRESS_OR_KEY      = -5  #//! Invalid address or key
    RPC_OUT_OF_MEMORY               = -7  #//! Ran out of memory during operation
    RPC_INVALID_PARAMETER           = -8  #//! Invalid missing or duplicate parameter
    RPC_DATABASE_ERROR              = -20 #//! Database error
    RPC_DESERIALIZATION_ERROR       = -22 #//! Error parsing or validating structure in raw format
    RPC_VERIFY_ERROR                = -25 #//! General error during transaction or block submission
    RPC_VERIFY_REJECTED             = -26 #//! Transaction or block was rejected by network rules
    RPC_VERIFY_ALREADY_IN_CHAIN     = -27 #//! Transaction already in chain
    RPC_IN_WARMUP                   = -28 #//! Client still warming up
    
    #//! Aliases for backward compatibility
    RPC_TRANSACTION_ERROR           = RPC_VERIFY_ERROR
    RPC_TRANSACTION_REJECTED        = RPC_VERIFY_REJECTED
    RPC_TRANSACTION_ALREADY_IN_CHAIN= RPC_VERIFY_ALREADY_IN_CHAIN
    
    #//! P2P client errors
    RPC_CLIENT_NOT_CONNECTED        = -9  #//! Bitcoin is not connected
    RPC_CLIENT_IN_INITIAL_DOWNLOAD  = -10 #//! Still downloading initial blocks
    RPC_CLIENT_NODE_ALREADY_ADDED   = -23 #//! Node is already added
    RPC_CLIENT_NODE_NOT_ADDED       = -24 #//! Node has not been added before
    RPC_CLIENT_NODE_NOT_CONNECTED   = -29 #//! Node to disconnect not found in connected nodes
    RPC_CLIENT_INVALID_IP_OR_SUBNET = -30 #//! Invalid IP/Subnet
    
    #//! Wallet errors
    RPC_WALLET_ERROR                = -4  #//! Unspecified problem with wallet (key not found etc.)
    RPC_WALLET_INSUFFICIENT_FUNDS   = -6  #//! Not enough funds in wallet or account
    RPC_WALLET_ACCOUNTS_UNSUPPORTED = -11 #//! Accounts are unsupported
    RPC_WALLET_KEYPOOL_RAN_OUT      = -12 #//! Keypool ran out call keypoolrefill first
    RPC_WALLET_UNLOCK_NEEDED        = -13 #//! Enter the wallet passphrase with walletpassphrase first
    RPC_WALLET_PASSPHRASE_INCORRECT = -14 #//! The wallet passphrase entered was incorrect
    RPC_WALLET_WRONG_ENC_STATE      = -15 #//! Command given in wrong wallet encryption state (encrypting an encrypted wallet etc.)
    RPC_WALLET_ENCRYPTION_FAILED    = -16 #//! Failed to encrypt the wallet
    RPC_WALLET_ALREADY_UNLOCKED     = -17 #//! Wallet is already unlocked

KotoRPCErrorString = {}
for m in inspect.getmembers(KotoRPCErrorCode):
	if m[0][0:4] == "RPC_":
		if not KotoRPCErrorString.has_key(m[1]):
			KotoRPCErrorString[m[1]] = m[0]

def error2str(code):
	if KotoRPCErrorString.has_key(code):
		return KotoRPCErrorString[code]
	return "RPC_UNKNOWN_ERROR_CODE_%d" % code

class KotoRPCException(Exception):
	def __init__(self, m, c, id, method, param):
		super(Exception, self).__init__(m, c, error2str(c), id, method, param)

	def message(self):
		return self.args[0]
	
	def code(self):
		return self.args[1]

	def codestr(self):
		return self.args[2]

	def id(self):
		return self.args[3]

	def method(self):
		return self.args[4]

	def param(self):
		return self.args[5]

class KotoRPCInvalidValue(Exception):
	def __init__(self, m, v):
		super(Exception, self).__init__(m, v)

class KotoRPC:
	def __init__(self, username, password, host = "localhost", port = 8432, testnet = False):
		self.host = host
		self.port = port
		self.auth = (username, password)
		self.id = 0
		self.headers = {'content-type': 'application/json'}
		if not testnet:
			self.setmainnet(port)
		else:
			if port != 8432 and port != 18432:
				self.settestnet(port)
			else:
				self.settestnet()

	def setmainnet(self, port = 8432):
		self.addr_prefix = "\x18\x36"
		self.port = port

	def settestnet(self, port = 18432):
		self.addr_prefix = "\x18\xa4"
		self.port = port

	def checkaddr(self, addr):
		try:
			d = base58.b58decode_check(addr)
			if d[0:2] == self.addr_prefix:
				return True
			return False
		except:
			return False

	def checkzaddr(self, zaddr):
		result = self.z_validateaddress(zaddr)
		return result["isvalid"]

	def dorpc(self, method, params):
		url = "http://%s:%d" % (self.host, self.port)
		payload = {
			"jsonrpc": "1.0",
			"method": method,
			"params": params,
			"id": self.id
		}
		self.id += 1
		#print json.dumps(payload)
		response = requests.post(url, data=json.dumps(payload), headers=self.headers, auth=self.auth).json()
		if response["error"] != None:
			raise KotoRPCException(
				response["error"]["message"],
				response["error"]["code"],
				response["id"],
				method, params)
		return response["result"]

	def getinfo(self):
		return self.dorpc("getinfo", [])
	
	def getbalance(self, account = "", minconf = 1, includeWatchonly = False):
		return self.dorpc("getbalance", [account, minconf, includeWatchonly])

	# fromaddr = "" or "kaddr"
	# toaddrset = {"kaddr": amount, "kaddr": amount, ...}
	# subtraddrs = ["kaddr", "kaddr", ...]
	def sendmany(self, fromaddr, toaddrset, minconf = 1, comment = "", subtraddrs = []):
		if not fromaddr == "" and not self.checkaddr(fromaddr):
			raise KotoRPCInvalidValue("sendmany: invalid from_address format", fromaddr)

		for addr in toaddrset.keys():
			if not self.checkaddr(addr):
				raise KotoRPCInvalidValue("sendmany: invalid to_address format", addr)

		for addr in subtraddrs:
			if not self.checkaddr(addr):
				raise KotoRPCInvalidValue("sendmany: invalid subtractfeefromamount address format", addr)

		return self.dorpc("sendmany", [fromaddr, toaddrset, minconf, comment, subtraddrs])

	def gettransaction(self, tid, watchonly = False):
		return self.dorpc("gettransaction", [tid, watchonly])

	def z_shieldcoinbase(self, fromaddr, tozaddr, fee = 0.0001, limit = 50):
		if fromaddr != "*" and not self.checkaddr(fromaddr):
			raise KotoRPCInvalidValue("z_shieldcoinbase: invalid fromaddr format", fromaddr)
		if not self.checkzaddr(tozaddr):
			raise KotoRPCInvalidValue("z_shieldcoinbase: invalid tozaddr format", tozaddr)
		return self.dorpc("z_shieldcoinbase", [fromaddr, tozaddr, fee, limit])

	# fromaddr = kaddr or zaddr
	# toaddrset = [{"address":"kaddr or zaddr", "amount": num, "memo": "memo..."}, {...}, ...]
	def z_sendmany(self, fromaddr, toaddrset, minconf = 1, fee = 0.0001):
		if not self.checkaddr(fromaddr) and not self.checkzaddr(fromaddr):
			raise KotoRPCInvalidValue("z_sendmany: invalid from_address format", fromaddr)

		for toaddr in toaddrset:
			if not toaddr.has_key("address") and not toaddr.has_key("amount"):
				raise KotoRPCInvalidValue("z_sendmany: to_address may not have address or amount", toaddr)
			addr = toaddr["address"]
			if not self.checkaddr(addr) and not self.checkzaddr(addr):
				raise KotoRPCInvalidValue("z_sendmany: invalid to_address format", addr)

		return self.dorpc("z_sendmany", [fromaddr, toaddrset, minconf, fee])

	def z_validateaddress(self, zaddr):
		return self.dorpc("z_validateaddress", [zaddr])
	
	def z_getoperationstatus(self, opidlist):
		return self.dorpc("z_getoperationstatus", [opidlist])
	
	def z_getoperationresult(self, opidlist):
		return self.dorpc("z_getoperationresult", [opidlist])
	
	def z_getbalance(self, addr, minconf = 1):
		if not self.checkaddr(addr) and not self.checkzaddr(addr):
			raise KotoRPCInvalidValue("z_getbalance: invalid address format", addr)		
		return self.dorpc("z_getbalance", [addr, minconf])

if __name__ == '__main__':
	rpc = KotoRPC("kotorpcuser", "kotorpcpass", testnet = True)
	#rpc.settestnet()
	
	print(rpc.checkaddr("kmTgDpyuT7pA6dj78aHJSqsVNDfssQLqoZv"))
	print(rpc.checkaddr("k12ocUADnMiUyrzr1oh2fxhDPLVAb9R3yTL"))

	#tid = rpc.sendmany("", {"kmXhVgXahUv5uA93Y2MbdBNRwk2E9hfDjkQ": 1})
	#print tid
	#print rpc.gettransaction(tid)

	print(rpc.checkzaddr("zto5xuxcYqohanWqG2KuM2nHP44hzbVLMKHxW44NojpYEqrjWAKX3vm13hWFrPKwvVsLpBaEqRjJpQobsrVAtPbqq66QxeK"))



