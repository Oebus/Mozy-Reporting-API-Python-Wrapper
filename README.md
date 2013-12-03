Mozy-Reporting-API-Python-Wrapper
=================================

Provides a simplified Python interface for the Mozy Reporting API


There are two main functions included in this library:

1. getToken()
Returns a valid token object from Reporting API auth/exchange

kwarg "auth_url" can be used to change the request url (for internal testing)
kwarg "xpartner_id" along with a specified sub-partner ID will return a token specific to the sub-partner

Example:
new_token = getToken("5Qhx6kLoGuej3y03RCa6Bly0HSQmp3R1GaBwex26BQlpTRi9mMDak7diBIV9vMKM")

2. fetchReport()
Returns a report in python dictionary format (default)

arg "return_request_object" will return the raw python Requests object
kwarg "wait_success" (dict object with keys "interval" and "timeout") will retry until timeout if the status code returned is 202 (report building)

Examples:
foo = fetchReport(token,"backup_status","partner","544098")
foo = fetchReport(token,"backup_status","partner","544098","return_request_object")
foo = fetchReport(token,"backup_status","partner","544098",wait_success={"interval":3,"timeout":15})

where 'token' is a token object obtained from getToken
