import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import webbrowser

dane_gus_ludnosc_file = 'LUDN_2137_CTAB_20200327110716.csv'
dane_gus_bezrobocie_file = 'RYNE_1944_CTAB_20200327105843.csv'

ludnosc_gus = pd.read_csv(dane_gus_ludnosc_file, delimiter=';')
bezrobocie_gus = pd.read_csv(dane_gus_bezrobocie_file, delimiter=';')

ludnosc_gus = ludnosc_gus.iloc[:, 0:3]
ludnosc_gus.columns = ['TERYT', 'Nazwa', 'Ludnosc']

bezrobocie_gus = bezrobocie_gus.iloc[:, [0, 2]]
bezrobocie_gus.columns = ['TERYT', 'Bezrobotni']

dane_gus = pd.merge(ludnosc_gus, bezrobocie_gus, how='inner', on='TERYT') # łączymy dane ze sobą przy pomocy TERYT


dane_gus['Stopa_bezrobocia'] = 100 * dane_gus['Bezrobotni'] / dane_gus['Ludnosc'] #obliczanie wyskosci stop bezrobocia

mapa_woj = gpd.read_file('wojewodztwa.shp')
mapa_gmn = gpd.read_file('gminy.shp')

mapa_woj = mapa_woj[['JPT_KOD_JE', "geometry"]]
mapa_gmn = mapa_gmn[['JPT_KOD_JE', "geometry"]]
#dodanie zero do terytu bo wcześniej obcina
dane_gus['TERYT_gmn'] = dane_gus.TERYT.apply(lambda x: '0'+str(x) if len(str(x)) < 7 else str(x))
dane_gus['TERYT_woj'] = dane_gus.TERYT_gmn.apply(lambda s: s[:2])

dane_gus = dane_gus[dane_gus['TERYT'] != '0'] # usuwanie agreagtow, np cale panstwo
dane_gus_woj = dane_gus[dane_gus.TERYT_gmn.str[2:7] == '00000'] #same województwa
dane_gus_gmn = dane_gus[dane_gus.TERYT_gmn.str[4:7] != '000'] #same gminy
#rysowanie mapy zaczynam od połącznie tabel
dane_mapa_woj = pd.merge(mapa_woj, dane_gus_woj, how='left', left_on='JPT_KOD_JE', right_on='TERYT_woj')

dane_mapa_woj = dane_mapa_woj.to_crs(epsg=2180) # zmiana układu

# fig, ax = plt.subplots(1, figsize = (8,8)) #okreslenie wielkosci
# dane_mapa_woj.plot(column='Stopa_bezrobocia', ax=ax, cmap='YlOrRd', linewidth=0.8, edgecolor='gray')
# ax.axis('off')
# plt.show()
# FOLIUM GMINY
# uproszczenie geometrii
mapa_gmn.geometry = mapa_gmn.geometry.simplify(0.005) # mniejsza wartosc = bardziej dokładnie

# dane do GeOJSON na potrzeby Folium
gmn_geoPath = mapa_gmn.to_json()
mapa = folium.Map([52, 19], zoom_start=6)

folium.Choropleth(geo_data=gmn_geoPath,  # GeJSON z danymi geograficznymi obszarów
                  data=dane_gus_gmn,  # data frame z danymi do pokazania
                  columns=['TERYT_gmn', 'Stopa_bezrobocia'],  # kolumna z kluczem, kolumna z wartościami
                  key_on='feature.properties.JPT_KOD_JE',  # gdzie jests klucz w GeoJSON?
                  fill_color='YlOrRd',
                  fill_opacity=0.7,
                  line_opacity=0.2,
                  legend_name="Stopa bezrobocia w gminie").add_to(mapa)

# zapisanie utworzonej mapy do pliku HTML
mapa.save(outfile='bezrobocie_gminy.html')

# pokazujemy mapę
new = 2
url= "bezrobocie_gminy.html"
webbrowser.open(url,new=new)