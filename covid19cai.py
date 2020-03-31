import json
from flask import Flask, request, jsonify 
import requests
import objectpath
import os
from googletrans import Translator

app = Flask(__name__) 
port = int(os.getenv("PORT", 9009)) #definicion de puerto de salida

@app.route('/casos', methods=['POST']) 
def index():

	postRece = json.loads(request.get_data())
	language = str(postRece['conversation']['language'])
	pais = str(postRece['conversation']['memory']['pais']['raw']).capitalize()

	translator = Translator()
	translated = translator.translate(pais, src='es', dest='en')
	country = translated.text.capitalize()

	URL = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query?f=json&where=(Confirmed > 0) AND (Deaths>0) AND (Recovered > 0) AND (Country_Region='{}')&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Deaths desc,Country_Region asc,Province_State asc&outSR=102100&resultOffset=0&resultRecordCount=250&cacheHint=true".format(country)
	HEADERS = {'Content-Type': 'application/json'}

	s = requests.session()

	r = s.get(url=URL,headers=HEADERS)

	print(r)

	country_exists = r.json()['features']

	if country_exists is not None and len(country_exists)>=1:

		cases = str(r.json()['features'][0]['attributes']['Confirmed'])
		deaths = str(r.json()['features'][0]['attributes']['Deaths'])
		recovered = str(r.json()['features'][0]['attributes']['Recovered'])

		if language == 'es':

			messageCAI = 'La cantidad de casos confirmados de COVID19 en {} son: {}, contanto con {} recuperados y {} fallecidos.'.format(pais,cases,recovered,deaths) 
			print(messageCAI)

		else:
			messageCAI = 'The total confirmed cases of COVID19 in {} are: {}, with {} recovered and {} deaths.'.format(country,cases,recovered,deaths)
			print(messageCAI)


		return jsonify( 
			    status=200, 
			    replies=[{'type': 'text','content': messageCAI}],
			    conversation= postRece['conversation']
			    )
	else:

		if language == 'es':
			messageCAI = 'Aún no se cuentan con casos confirmados para {}, o el nombre del país es incorrecto.'.format(pais)

		else:
			messageCAI = 'There is not confirmed cases yet in {}, or the country name is incorrect.'.format(country)

		return jsonify( 
			    status=200, 
			    replies=[{'type': 'text','content': messageCAI}],
			    conversation= postRece['conversation']
			    )


@app.route('/errors', methods=['POST']) 
def errors(): 
  json.loads(request.get_data())
  return jsonify(status=200) 
 
app.run(host='0.0.0.0',  port=port) #importante indicar host para deployment en plataforma