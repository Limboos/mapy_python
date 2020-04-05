import pandas as pd
import json
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import webbrowser
import web_scraping

web_scraping.downloading_data()
dane_gov_zarazeni_file = 'dane_MZ.csv'
zarazeni_gus = pd.read_csv(dane_gov_zarazeni_file, delimiter=',')
zarazeni_gus= zarazeni_gus.iloc[:, 1:5]
mapa_woj = gpd.read_file('wojewodztwa.shp')
mapa_woj = mapa_woj[['JPT_KOD_JE', "geometry"]]
mapa_woj.geometry =mapa_woj.geometry.simplify(0.005)
zarazeni_gus['TERYT_woj'] = zarazeni_gus.TERYT.apply(lambda x:  x[1:] if x[0]=='t' else str(x))
zarazeni_gus=zarazeni_gus.drop(0)
dane_mapa_woj = pd.merge(mapa_woj, zarazeni_gus, how='left', left_on='JPT_KOD_JE', right_on='TERYT_woj')
dane_mapa_woj_to_markers= dane_mapa_woj.drop(["JPT_KOD_JE", "TERYT_woj","Województwo","TERYT"], axis=1)
dane_mapa_woj = dane_mapa_woj.to_crs(epsg=2180) # zmiana układu

woj_geoPath = mapa_woj.to_json()
woj_geoPath_togeo = json.loads(dane_mapa_woj_to_markers.to_json())

bins = list(zarazeni_gus['Zarazeni'].quantile([0, 0.20, 0.40, 0.60, 0.80, 1]))
woj_geojson = [{'type': woj_geoPath_togeo['type'], 'features': [f]} for f in woj_geoPath_togeo['features']]
mapa = folium.Map([52, 19], zoom_start=6)

folium.Choropleth(geo_data=woj_geoPath,  # GeJSON z danymi geograficznymi obszarów
                  data=zarazeni_gus[0:],  # data frame z danymi do pokazania
                  columns=['TERYT_woj', 'Zarazeni'],  # kolumna z kluczem, kolumna z wartościami
                  key_on='feature.properties.JPT_KOD_JE',  # gdzie jests klucz w GeoJSON?
                  fill_color='YlOrRd',
                  fill_opacity=0.8,
                  line_opacity=0.3,
                  legend_name="Ilosc zakazonych w wojewodztwie",
                  bins=bins,
                  reset=True).add_to(mapa)

for gj in map(lambda gj: folium.GeoJson(gj), woj_geojson):
    props = gj.data['features'][0]['properties']
    gj.add_child(folium.Popup(str(props)))
    gj.add_to(mapa)


# zapisanie utworzonej mapy do pliku HTML
mapa.save(outfile='zar_woj.html')

# pokazujemy mapę
new = 2
url= "zar_woj.html"
webbrowser.open(url,new=new)