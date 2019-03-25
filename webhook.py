 # -*- coding: utf-8 -*- 
#todo:other store types, directions, show photo 
import json, os, googlemaps, sys
from flask import Flask, request, make_response

reload(sys)
sys.setdefaultencoding("utf-8")

# Flask app should start in global layout
app = Flask(__name__)

gmaps = googlemaps.Client(key='your googlemaps api key')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    action = req.get("queryResult").get("action")
    places = req.get("queryResult").get("parameters").get("places")
    
    #如果location==None, api.ai的intent的places不要設成list
    if action == "locate&eat" and places:
        location = setLocation(places, (22.997463, 120.202570), 50000)
        if location is None:
            location = (22.997463, 120.202570)
        #print ('location:')
        #print (location)
        res = giveStoreNames(location, 200, 'restaurant', "餐廳")
    elif action == "locate&stay" and places:
        location = setLocation(places, (22.997463, 120.202570), 50000)
        if location is None:
            location = (22.997463, 120.202570)
        #print ('location:')
        #print (location)
        res = giveStoreNames(location, 200, 'lodging', "飯店")
    #elif action == "locate&search" and places:
        #location = setLocation(places, (22.997463, 120.202570), 50000)
        #res = searchDetails(places, location, 0)
 
    elif action == "eat":
        res = giveStoreNames((22.997463, 120.202570), 200, 'restaurant', "餐廳")
    elif action == "stay":
        res = giveStoreNames((22.997463, 120.202570), 200, 'lodging', "飯店")
    elif action == "search" and places:
        res = searchDetails(places, (22.997463, 120.202570), 200)

    else: 
        res = {
        "fulfillmentText": "抱歉可以說詳細一點嗎~~ 例如 我想吃XXX 或是 XXX附近有什麼吃的" 
    }

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return r

#決定搜尋位置，限制在台南附近
def setLocation(query, location, radius):
    place_details_results = gmaps.places(query, location, radius)
    for element in place_details_results['results']:
        if element['place_id']:
            place_details = gmaps.place(element['place_id'], 'zh-TW')
            for k,v in place_details['result'].iteritems():
                if k == 'formatted_address':
                    geocodeList = gmaps.geocode(v, language = 'zh-TW')
                    #print (geocodeList)
                    for key, value in geocodeList[0].iteritems():
                        if key == 'geometry':
                            latitude = value['location']['lat']
                            longtitude = value['location']['lng']
                            return (latitude, longtitude)

#給出某地點詳細資訊
def searchDetails(query, location, radius):
    #if no store, x remains 0
    x = 0
    place_details_results = gmaps.places(query, location, radius, 'zh-TW')
    response = "以下為您整理附近資訊: \n\n"
    for element in place_details_results['results']:
        if element['place_id']:
            place_details = gmaps.place(element['place_id'], 'zh-TW')
            #print ("place_details")
            #print (place_details)
            for k,v in place_details['result'].iteritems():
                if k == 'name':
                    x = 1
                    response = response+'店名: '+str(v)+'\n'
                elif k == 'formatted_phone_number':
                    response = response+'電話: '+str(v)+'\n' 
                elif k == 'formatted_address':
                    response = response+'地址: '+str(v)+'\n' 
                elif k == 'rating':
                    response = response+'評價: '+str(v)+'\n' 
                elif k == 'url':
                    response = response+'開啟Google地圖: '+str(v)+'\n' 
                elif k == 'website':
                    response = response+'店家網址: '+str(v)+'\n'
        response = response+'\n'
    
    if x == 0:
        response = "很遺憾，這附近太偏僻了，沒有找到店家"
    return {
        "fulfillmentText": response
    }

#列出某種類型的店數家
def giveStoreNames(location, radius, place_type, searchName):
    #if no store, x remains 0
    x = 0
    places_radar_result = gmaps.places_radar(location, radius, name = searchName, type = place_type)  
    response = "以下為您整理附近資訊: \n\n"
    #print ("places_radar_result")
    #print (places_radar_result)
    for element in places_radar_result['results']:
        if element['place_id']:
            place_details = gmaps.place(element['place_id'], 'zh-TW')
            #print ("place_details")
            #print (place_details)
            for k,v in place_details['result'].iteritems():
                if k == 'name':
                    x = 1
                    response = response+str(v)+", "

    response = response+'\n\n 請問您想去哪家呢?'
    if x == 0:
        response = "很遺憾，這附近太偏僻了，沒有找到店家" 
    return {
        "fulfillmentText": response
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print ("Starting app on port %d" %(port))
    app.run(debug=True, port=port, host='0.0.0.0')
