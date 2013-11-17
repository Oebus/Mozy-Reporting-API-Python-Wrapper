import requests
import time

'''
GetToken()
Returns a valid token object from Reporting API auth/exchange

Example:
new_token = getToken("5Qhx6kLoGuej3y03RCa6Bly0HSQmp3R1GaBwex26BQlpTRi9mMDak7diBIV9vMKM")
'''
def getToken(API_key,auth_url="http://services.mozy.com/auth/exchange",xpartner_id=None):

	#sets up headers
	request_header = {
		"Accept":"application/vnd.mozy.bifrost+json;v=1",
		"Api-Key": API_key
		}

	if xpartner_id:
		request_header["X-MozyPartner"] = str(xpartner_id)

	#gets the token
	auth_request = requests.get(auth_url, headers=request_header)

	#decodes json to python dict
	data = auth_request.json()

	#calculates expiration timestamp
	token_expiration = int(time.time()) + int(data["expires"]) - 5
	
	return Auth_Token(data["token_type"],data["token"],token_expiration,request_header,auth_url)

class Auth_Token: #defines token object
	def __init__(self, tok_type,tok_string,tok_exp,tok_head,tok_url):
		self.type = tok_type
		self.string = tok_string
		self.expiration = tok_exp
		self.header = tok_head
		self.auth_url = tok_url

	#make sure the token has not expired, returns regenerated token if expired
	def Validate(self):
		if time.time() < self.expiration:
			return self
		else:
			return self.Regenerate()

	#get a new token based on previous header data
	def Regenerate(self):
		if "X-MozyPartner" in self.header:
			return getToken(self.header["Api-Key"],self.auth_url,self.header["X-MozyPartner"])
		else:
			return getToken(self.header["Api-Key"],self.auth_url)

'''
fetchReport()
Returns a report in python dictionary format

Example:
foo = fetchReport(token,"backup_status","partner","544098")

where 'token' is a token object obtained from getToken
'''
def fetchReport(token,report_type,scope,report_id=None):

	report_types_accepted = ["resources","backup_status"]
	scopes_accepted = ["partner","user_group","user","machine"]

	#validate args
	if report_type not in report_types_accepted:
		raise Exception("Report_type \"{}\" invalid.".format(report_type))

	if scope not in scopes_accepted:
		raise Exception("Scope \"{}\" invalid.".format(scope))

	if report_type == "resources" and scope == ("user" or "machine"):
		raise Exception("Resource reports can only be run on partners and user groups.")

	#this exception can be removed once plural calls are supported in production
	###################################################################################
	if not report_id:
		raise Exception("Plural calls are not yet supported. Provide partner ID.")
	###################################################################################

	#check token expiration, regenerate if necessary
	request_token = token.Validate()

	#set request_url based on desired report
	request_url = "https://services.mozy.com/reports/{}/{}/{}".format(report_type,scope,report_id)

	request_header = {
		"Accept":"application/vnd.mozy.bifrost+json;v=1",
		"Authorization":"{} {}".format(request_token.type,request_token.string)
	}

	report_request = requests.get(request_url, headers=request_header)
	
	data = report_request.json()
	return data

def main(): #test script can go here
	pass

if __name__ == '__main__':
    main()