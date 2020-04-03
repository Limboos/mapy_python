import requests
import bs4
import pandas as pd
def downloading_data():
    res= requests.get('https://www.gov.pl/web/koronawirus/wykaz-zarazen-koronawirusem-sars-cov-2')
    res.raise_for_status()
    soup =  bs4.BeautifulSoup(res.text, "lxml")
    print(soup.title.text)
    pre = soup.find_all('pre')
    table = soup.find("pre").find(text=True)
    split_table = table.split(",")
    second_split = split_table[2].split("\\")
    data=[]
    for el in second_split:
        if el=='r':
            second_split.remove(el)
    for el in second_split:
        data.append(el[1:].split(";"))
    data.pop(-1)
    file = pd.DataFrame(data=data,
                        columns=data[0])
    file.columns=['Województwo','Zarazeni','Liczba zgonow','TERYT']
    file = file.drop(0)
    print(file)
    file.to_csv("dane_MZ.csv")


