import requests,json,os
#Certificate validation for https fails, so I disabled requests' verification for now
MAPS_ENDPOINT="https://maps.west-lindsey.gov.uk/map/Cluster.svc"
FIND_LOCATION="%s/findLocation"%MAPS_ENDPOINT
GETPAGE_LOCATION="%s/getpage"%MAPS_ENDPOINT
DEFAULT_USER_AGENT="Mozilla/5.0"
#store path to ca bundle for the maps endpoint. As requests' default bundle doesn't verify
BIN_SSL_ENVIRON="binssl"
DEFAULT_VERIFY=False
def getVerify():
    if os.getenv(BIN_SSL_ENVIRON):
        return os.getenv(BIN_SSL_ENVIRON)
    else:return DEFAULT_VERIFY
def getDefaultSession():
    session=requests.Session()
    session.headers["User-Agent"]=DEFAULT_USER_AGENT
    return session
def findLocation(address,session=None,verify=None):
    if not session:session=getDefaultSession()
    params={"address":address,"callback":"getAddressesCallback","script":"\\Cluster\\Cluster.AuroraScript$"}
    if verify is None:
        try:return session.get(FIND_LOCATION,params=params)
        except requests.exceptions.SSLError:return findLocation(address,session,verify=getVerify())
    else:return session.get(FIND_LOCATION,params=params,verify=verify)
def getPage(x,y,id,session=None):
    if not session:session=getDefaultSession()
    return session.get(GETPAGE_LOCATION,params={"script":"\\Cluster\\Cluster.AuroraScript$","taskId":"bins","format":"json","updateOnly":"true","query":"x=%s;y=%s;id=%s"%(x,y,id)})
def parseFindLocation(res):
    if res.statusCode==200:
        t=res.text
    else:return {"success":False}
