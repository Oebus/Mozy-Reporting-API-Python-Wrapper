import requests
import time

'''
getToken()
Returns a valid token object from Reporting API auth/exchange

kwarg "auth_url" can be used to change the request url (for internal testing)
kwarg "xpartner_id" along with a specified sub-partner ID will return a token specific to the sub-partner

Example:
new_token = getToken("5Qhx6kLoGuej3y03RCa6Bly0HSQmp3R1GaBwex26BQlpTRi9mMDak7diBIV9vMKM")
'''
def getToken(API_key,**kwargs):

	#get kwargs
	auth_url = kwargs.get("auth_url","http://services.mozy.com/auth/exchange")
	xpartner_id = kwargs.get("xpartner_id", None)

	#set up headers
	request_header = {
		"Accept":"application/vnd.mozy.bifrost+json;v=1",
		"Api-Key": API_key
		}

	if xpartner_id:
		request_header["X-MozyPartner"] = str(xpartner_id)

	#get the token
	auth_request = requests.get(auth_url, headers=request_header)

	#decode json to python dict
	data = auth_request.json()

	#calculate expiration timestamp
	token_expiration = int(time.time()) + int(data["expires"]) - 5
	
	return Auth_Token(data["token_type"],data["token"],token_expiration,request_header,auth_url)

class Auth_Token: #defines the token object
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
Returns a report in python dictionary format (default)

arg "return_request_object" will return the raw python Requests object
kwarg "wait_success" (dict object with keys "interval" and "timeout") will retry until timeout
	if the status code returned is 202 (report building)

Examples:
foo = fetchReport(token,"backup_status","partner","544098")
foo = fetchReport(token,"backup_status","partner","544098","return_request_object")
foo = fetchReport(token,"backup_status","partner","544098",wait_success={"interval":3,"timeout":15})

where 'token' is a token object obtained from getToken
'''
def fetchReport(token,report_type,scope,report_id=None,*args,**kwargs):
	
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

	#get request
	report_request = requests.get(request_url, headers=request_header)
	
	if "return_request_object" in args: #Option 1: return the raw request object
		return report_request

	elif "wait_success" in kwargs and report_request.status_code == 202: #Option 2: keep trying if status 202 returned
		sleep_timer = kwargs.get("wait_success")["interval"] #set interval
		time.sleep(sleep_timer)
		if "timer" not in kwargs["wait_success"]: #create a timer var to keep track
			kwargs["wait_success"]["timer"] = 0
		kwargs["wait_success"]["timer"] += sleep_timer #update the timer
		if kwargs.get("wait_success")["timeout"] <= kwargs.get("wait_success")["timer"]: #check the timer
			raise Exception("Request timeout exceeded. Status code: 202") #timeout
		else:
			return fetchReport(token,report_type,scope,report_id,*args,**kwargs) #recurse

	elif report_request.status_code != 202 and report_request.status_code != 200: #Successful API call but bad params
		raise Exception(report_request.json()["message"]) #give error message if one is returned by API

	else: #Option 3: if no errors, gimme the report in python dict format (default)
		return report_request.json()

def main(): #test script can go here
	pass

if __name__ == '__main__':
    main()