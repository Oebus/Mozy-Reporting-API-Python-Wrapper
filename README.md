Mozy-Reporting-API-Python-Wrapper
=================================

Provides a simplified Python interface for the Mozy Reporting API


There are two main functions included in this library:

1. getToken

Parameters: API_key, auth_url (optional), xpartnerid (optional)
	auth_url: default value http://services.mozy.com/auth/exchange
		can be used to obtain the token from another provider, used for internal testing purposes
	xpartnerid: default None
		can be provided to return a key specific to a sub-partner of the parent account
  
Returns: a token object which can be used to fetch a report from the API

Example:
new_token = getToken("5Qhx6kLoGuej3y03RCa6Bly0HSQmp3R1GaBwex26BQlpTRi9mMDak7diBIV9vMKM")

2. fetchReport

Parameters: token, report_type, scope, report_id
	token: the token object returned from getToken()
	report_type: either "resources" or "backup_status"
	scope: can be "partner", "user_group", "user", or "machine"*
	report_id: the id of the partner, user group, user, or machine

*resource reports can only be run for partners and user groups

Returns: the requested report as a Python dictionary object

Example:
foo = fetchReport(token,"backup_status","partner","544098")
