import requests,json,os,argparse,random
from datetime import datetime
#Certificate validation for https fails, so I disabled requests' verification for now
MAPS_ENDPOINT="https://maps.west-lindsey.gov.uk/map/Cluster.svc"
FIND_LOCATION="%s/findLocation"%MAPS_ENDPOINT
GETPAGE_LOCATION="%s/getpage"%MAPS_ENDPOINT
DEFAULT_USER_AGENT="Mozilla/5.0"
#store path to ca bundle for the maps endpoint. As requests' default bundle doesn't verify
BIN_SSL_ENVIRON="binssl"

#literally just stores address in plaintext
ADDR_SAVE_LOCATION="~/.config/howdoibin.txt"

KEY_LOCATION_DATA="Locations"
KEY_ADDR="Description"
KEY_ID="Id"
KEY_X="X"
KEY_Y="Y"

KEY_NEXT_DAY="next_day"
KEY_NEXT_DATE="next_date"
KEY_NEXT_DATE_RAW="next_date_raw"
KEY_AFTER_DATE="after_date"
KEY_AFTER_DATE_RAW="after_date_raw"
KEY_USUAL_DAY="usual_collection_day"
KEY_PREVIOUS_DATE="previous_date"
KEY_TODAY="is_today"

BIN_COLOURS=["black","blue","green"]

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
    return session.get(GETPAGE_LOCATION,params={"script":"\\Cluster\\Cluster.AuroraScript$","taskId":"bins","format":"js","updateOnly":"true","query":"x=%s;y=%s;id=%s"%(x,y,id)},verify=False)
#gets the x,y,id from the address data
def _addr(addr):
    return addr[KEY_X],addr[KEY_Y],addr[KEY_ID]
def parseFindLocation(res):
    if res.status_code==200:
        t=res.text
        j_ext=None
        try:j_ext=json.loads(t[t.find("{"):t.rfind(");")])
        except:pass
        return True if j_ext else False,j_ext
    else:return False,None
#pass parsed find location json data
def extractAddresses(find_loc):
    if len(find_loc)>0:
        #returns a list index 0 True/False, 1 response data
        if find_loc[0]:
            find_data=find_loc[1]
            if KEY_LOCATION_DATA in find_data:
                locations=find_data[KEY_LOCATION_DATA]
                return locations
            else:raise ValueError("Either response format changed or request failed")
def findend(s,sub,start=None):
    find=s.find(sub,start)
    if find>=0:
        return find+len(sub)
    else:return find
def parseDate(s):return stripTime(datetime.strptime(s,"%d/%m").replace(year=datetime.today().year))
#remove unecessary parts to compare current day
def stripTime(d):return d.replace(hour=0,minute=0,second=0,microsecond=0)

#does not include collections for the current day
#will need to test on day of collection as may say "today"
#data to find, next collection, after next collection (next 2), usual collection day
def parseGetPage(res,verbose=0):
    lthan="\\u003c"
    gthan="\\u003e"
    quote="\\u0027"
    a=res.text
    alow=a.lower()
    _colours=["BLACK","BLUE","GREEN"]
    parsed={}
    #wasterBLACK, wasterBLUE, wasterGREEN
    span="waster%s"
    start=findend(a,"document.getElementById(\"DR1\")")
    for col in _colours:
        cstart=findend(a,span%col,start)
        if cstart==-1:continue
        cend=a.find("%s/li%s"%(gthan,lthan),cstart)
        csplit=a[cstart:cend].split()
        next_day=csplit[3].replace(",","")
        next_date=csplit[4][:csplit[4].find(lthan)]
        after_date=csplit[7].replace(".","")
        usual_collection_day=csplit[17][:csplit[17].find(lthan)]
        parsed[col]={}
        n=parseDate(next_date)
        a=parseDate(after_date)
        parsed[col][KEY_NEXT_DATE_RAW]=next_date
        parsed[col][KEY_NEXT_DATE]=n
        parsed[col][KEY_AFTER_DATE_RAW]=after_date
        parsed[col][KEY_AFTER_DATE]=a
        parsed[col][KEY_USUAL_DAY]=usual_collection_day
        #estimate the previous collection day by subtracting difference between after and next
        diff=a-n
        parsed[col][KEY_PREVIOUS_DATE]=stripTime(n-diff)
        parsed[col][KEY_TODAY]=parsed[col][KEY_PREVIOUS_DATE]==stripTime(datetime.today())
    return parsed
#return None if failed to load
def loadAddress():
    if os.path.isfile(ADDR_SAVE_LOCATION):
        try:
            with open(ADDR_SAVE_LOCATION,'r')as inp:
                return inp.read().strip()
        except:
            return None
def saveAddress(addr):
    with open(ADDR_SAVE_LOCATION,'w')as outp:
        outp.write(addr)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("address",nargs="?",help="The address to check")
    parser.add_argument("-c","--colour",help="An individual colour to check against")
    parser.add_argument("-b","--blue",action="store_true",help="Check blue bin date")
    parser.add_argument("-B","--black",action="store_true",help="Check black bin date")
    parser.add_argument("-g","--green",action="store_true",help="Check green bin date")
    parser.add_argument("-s","--save",action="store_true",help="Save supplied address for use next time")
    parser.add_argument("--today",action="store_true",help="Check if any bins should be out today")
    parser.add_argument("-v",action="store_true",help="Make application more verbose")
    parsed=parser.parse_arguments()
    print(parsed)
    tofind=parsed["address"] if parsed["address"] else
    if not addr:
        print("")
    if parsed["address"]:
        pass
if __name__=="__main__":
    main()
    """
    a=extractAddresses(parseFindLocation(findLocation("")))
    addr=random.choice(a)
    page=getPage(*_addr(addr))
    page_parsed=parseGetPage(page)
    """
