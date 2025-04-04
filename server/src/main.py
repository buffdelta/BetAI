from WebScraper import WebScraper

def main():
    webscraper = WebScraper()
    game_links = []
    game_links = webscraper.get_all_game_links_year(2005)
    print(game_links)

if __name__ == "__main__":
    main()
