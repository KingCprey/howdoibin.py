import requests,json
#Certificate validation for https fails, so I disabled requests' verification for now
MAPS_ENDPOINT="https://maps.west-lindsey.gov.uk/map/Cluster.svc"
FIND_LOCATION="%s/findLocation"%MAPS_ENDPOINT
GETPAGE_LOCATION="%s/getpage"%MAPS_ENDPOINT
DEFAULT_USER_AGENT="Mozilla/5.0"
def getDefaultSession():
    session=requests.Session()
    session.headers["User-Agent"]=DEFAULT_USER_AGENT
    return session
def findLocation(address,session=None):
    if not session:session=getDefaultSession()
    return session.get(FIND_LOCATION,params={"address":address,"callback":"getAddressesCallback","script":"\\Cluster\\Cluster.AuroraScript$"},verify=False)
def getPage(x,y,id,session=None):
    if not session:session=getDefaultSession()
    return session.get(GETPAGE_LOCATION,params={"script":"\\Cluster\\Cluster.AuroraScript$","taskId":"bins","format":"json","updateOnly":"true","query":"x=%s;y=%s;id=%s"%(x,y,id)})
def parseFindLocation(res):
    if res.statusCode==200:
        t=res.text
    else:return {"success":False}
