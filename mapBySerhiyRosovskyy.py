import urllib.request, urllib.parse, urllib.error
from flask import Flask, render_template, request
import requests
import twurl
import json
import ssl


app = Flask(__name__)


def twitter_get(name, count):
    TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    while True:
        if (len(name) < 1):
            break
        url = twurl.augment(TWITTER_URL,
                            {'screen_name': name, 'count': count})
        connection = urllib.request.urlopen(url, context=ctx)
        data = connection.read().decode()

        js = json.loads(data)
        lst = []
        for i in js['users']:
            lst.append((i['location'], i['name']))
        return lst


def get_location(place):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=1600"
    for i in place.split():
        url += '+' + i
    url += "&key=AIzaSyBZ9WWdYr5xHTci_LHkm6RaBicWYENSNRA"
    params = {'sensor': 'false', 'address': place}
    r = requests.get(url, params=params)
    result = r.json()["results"]
    location = result[0]['geometry']['location']
    return (location['lat'], location['lng'])


def mapp(friends):
    import folium
    mapp = folium.Map()
    lst = []
    no = 0
    for i in friends:
        try:
            if i[0]:
                location = get_location(i[0])
                lst.append((location))
                print("{}'s location is {}, {}".format(i[1], location[0], location[1]))
                mapp.add_child(folium.Marker(location=[location[0], location[1]], popup=i[1], icon=folium.Icon()))
            else:
                no =+ 1
                continue
        except:
            continue
    mapp.save('templates/map.html')
    return no


@app.route("/")
def start():
    return render_template('index.html')


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
    print("Wait a minute :)")
    lst = twitter_get(name, count)
    f = mapp(lst)
    print("{} person didn't specify their location".format(f))
    return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)
