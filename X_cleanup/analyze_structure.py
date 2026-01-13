import requests
from bs4 import BeautifulSoup

def analyze_html_structure(url):
    print(f"Analyzing {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for Member Function blocks logic
    # In Doxygen, member functions are typically under 'h2.groupheader' ("Member Functions")
    # or inside 'div.memitem'
    
    memitems = soup.find_all('div', class_='memitem')
    print(f"Found {len(memitems)} 'div.memitem' blocks.")
    
    if memitems:
        # Inspect first few
        for i, item in enumerate(memitems[:3]):
            print(f"\n--- Item {i} ---")
            # Usually contains a .memproto (prototype) and .memdoc (documentation)
            proto = item.find('div', class_='memproto')
            doc = item.find('div', class_='memdoc')
            
            if proto:
                print("Proto:", proto.get_text(" ", strip=True)[:100] + "...")
            else:
                print("Proto: Not found")
                
            if doc:
                print("Doc:", doc.get_text(" ", strip=True)[:100] + "...")
            else:
                print("Doc: Not found")

if __name__ == "__main__":
    analyze_html_structure("https://docs.juce.com/master/classjuce_1_1AudioBuffer.html")
