from django.shortcuts import render
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_accommodations(destination, checkin_date, checkout_date, limit=5):
    url = f"https://www.booking.com/searchresults.html?ss={destination}&checkin_monthday={checkin_date.day}&checkin_month={checkin_date.month}&checkin_year={checkin_date.year}&checkout_monthday={checkout_date.day}&checkout_month={checkout_date.month}&checkout_year={checkout_date.year}&order=price"    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    accommodations = []
    
    for item in soup.find_all('div', class_='c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4')[:limit]:
        try:
            name = item.find('div', class_='f6431b446c a15b38c233').text.strip()
        except AttributeError:
            name = 'N/A'
        
        try:
            price = item.find('span', class_='f6431b446c fbfd7c1165 e84eb96b1f').text.strip()
        except AttributeError:
            price = 'N/A'
        
        try:
            rating = item.find('div', class_='a3b8729ab1 d86cee9b25').text.strip()
            rating = rating.split('Scored')
        except AttributeError:
            rating = 'N/A'
        
        accommodations.append({
            'name': name,
            'price': price,
            'rating': rating[0]
        })
    
    return pd.DataFrame(accommodations)

def get_attractions(destination, limit=5):    
    base_url = "https://www.taiwan.net.tw"
    destination_map = {
        "Taipei": "0001090",
        "New Taipei": "0001091",
        "Keelung": "0001105",
        "Yilan": "0001106",
        "Taoyuan": "0001107",
        "Hsinchu County": "0001108",
        "Hsinchu": "0001109",
        "Miaoli": "0001110",
        "Taichung": "0001112",
        "Changhua": "0001113",
        "Nantou": "0001114",
        "Yunlin": "0001115",
        "Chiayi County": "0001116",
        "Chiayi": "0001117",
        "Tainan": "0001119",
        "Kaohsiung": "0001121",
        "Pingtung": "0001122",
        "Hualien": "0001124",
        "Taitung": "0001123",
    }
    
    if destination not in destination_map:
        return pd.DataFrame()
    
    url_no = destination_map[destination]
    url = f"{base_url}/m1.aspx?sNo={url_no}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
    
    attractions = []
    viewpoints = soup.find_all("div", class_="card")
    
    for viewpoint in viewpoints:
        name = viewpoint.find('div', class_='card-title').text.strip()
        attractions.append({
            'name': name
        })
    
    return pd.DataFrame(attractions)

def search(request):
    # Predefined list of destinations
    destinations = [
        "Taipei", "New Taipei", "Keelung", "Yilan", "Taoyuan",
        "Hsinchu County", "Hsinchu", "Miaoli", "Taichung", "Changhua",
        "Nantou", "Yunlin", "Chiayi County", "Chiayi", "Tainan",
        "Kaohsiung", "Pingtung", "Hualien", "Taitung"
    ]
    destinationc = [
        "台北市", "新北市", "基隆市", "宜蘭市", "桃園市",
        "新竹縣", "新竹市", "苗栗市", "台中市", "彰化縣",
        "南投市", "雲林縣", "嘉義縣", "嘉義市", "台南市",
        "高雄市", "屏東縣", "花蓮縣", "台東縣"
    ]
    destinations_with_chinese = zip(destinations, destinationc)
    
    if request.method == "POST":
        destination = request.POST.get("destination")
        checkin_date = request.POST.get("checkin_date")
        checkout_date = request.POST.get("checkout_date")
        
        if not destination or not checkin_date or not checkout_date:
            error = "All fields are required."
            return render(request, 'destinations/search.html', {'destinations': destinations_with_chinese, 'error': error})
        
        try:
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d')
        except ValueError:
            error = "Invalid date format. Please use YYYY-MM-DD."
            return render(request, 'destinations/search.html', {'destinations': destinations_with_chinese, 'error': error})
        
        accommodations = get_accommodations(destination, checkin_date, checkout_date)
        attractions = get_attractions(destination)
        
        return render(request, 'destinations/result.html', {
            'accommodations': accommodations.to_dict(orient='records'),
            'attractions': attractions.to_dict(orient='records')
        })
    
    return render(request, 'destinations/search.html', {'destinations': destinations_with_chinese})
