import requests
import json
import base58
import logging

class KOTO:
	DEFAULT_FEE = 0.0001

class KotoRPCException(Exception):
	def __init__(self, m, c, id, method, param):
		super(Exception, self).__init__(m, c, id, method, param)

	def message(self):
		return self.args[0]
	
	def code(self):
		return self.args[1]

	def id(self):
		return self.args[2]

	def method(self):
		return self.args[3]

	def param(self):
		return self.args[4]

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
			raise Exception("sendmany: invalid from_address format", fromaddr)

		for addr in toaddrset.keys():
			if not self.checkaddr(addr):
				raise Exception("sendmany: invalid to_address format", addr)

		for addr in subtraddrs:
			if not self.checkaddr(addr):
				raise Exception("sendmany: invalid subtractfeefromamount address format", addr)

		return self.dorpc("sendmany", [fromaddr, toaddrset, minconf, comment, subtraddrs])

	def gettransaction(self, tid, watchonly = False):
		return self.dorpc("gettransaction", [tid, watchonly])

	def z_shieldcoinbase(self, fromaddr, tozaddr, fee = 0.0001, limit = 50):
		if fromaddr != "*" and not self.checkaddr(fromaddr):
			raise Exception("z_shieldcoinbase: invalid fromaddr format", fromaddr)
		if not self.checkzaddr(tozaddr):
			raise Exception("z_shieldcoinbase: invalid tozaddr format", tozaddr)
		return self.dorpc("z_shieldcoinbase", [fromaddr, tozaddr, fee, limit])

	# fromaddr = kaddr or zaddr
	# toaddrset = [{"address":"kaddr or zaddr", "amount": num, "memo": "memo..."}, {...}, ...]
	def z_sendmany(self, fromaddr, toaddrset, minconf = 1, fee = 0.0001):
		if not self.checkaddr(fromaddr) and not self.checkzaddr(fromaddr):
			raise Exception("z_sendmany: invalid from_address format", fromaddr)

		for toaddr in toaddrset:
			if not toaddr.has_key("address") and not toaddr.has_key("amount"):
				raise Exception("z_sendmany: to_address may not have address or amount", toaddr)
			addr = toaddr["address"]
			if not self.checkaddr(addr) and not self.checkzaddr(addr):
				raise Exception("z_sendmany: invalid to_address format", addr)

		return self.dorpc("z_sendmany", [fromaddr, toaddrset, minconf, fee])

	def z_validateaddress(self, zaddr):
		return self.dorpc("z_validateaddress", [zaddr])
	
	def z_getoperationstatus(self, opidlist):
		return self.dorpc("z_getoperationstatus", [opidlist])
	
	def z_getoperationresult(self, opidlist):
		return self.dorpc("z_getoperationresult", [opidlist])
	
	def z_getbalance(self, addr, minconf = 1):
		if not self.checkaddr(addr) and not self.checkzaddr(addr):
			raise Exception("z_getbalance: invalid address format", addr)		
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



