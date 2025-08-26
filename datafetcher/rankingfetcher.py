import os
import bs4
import undetected_chromedriver as uc
import pandas as pd
import re
import logging

class RankingScraper:
    def __init__(self, dates):
        self.base_url = 'https://www.atptour.com/en/rankings/singles?rankRange=0-5000&dateWeek='
        self.soup = None
        self.options = uc.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        self.options.add_argument('--lang=en-US,en')
        self.options.add_argument('--window-size=1920,1080')
        self.driver = uc.Chrome(options=self.options)
        self.dates = dates

    def fetch_page(self, date) -> bs4.BeautifulSoup:
        self.driver.get(self.base_url + date)
        soup = bs4.BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    def create_dataframe(self, save: bool) -> str:
        for date in self.dates:
            file_path = f'datafetcher/data/rankings/data_atp_rankings_{date}.csv'
            if os.path.exists(file_path):
                print(f"File {file_path} already exists. Skipping save.")
                continue
            soup = self.fetch_page(date)

            data = []
            # option_selected = soup.find_all('option', attrs={'value': 'Current Week'})
            # Extract the ranking date from the option with a value that matches a date pattern

            ranking_date = None
            # for opt in option_selected:
            #     if re.match(r'\d{4}\.\d{2}\.\d{2}', opt.text.strip()):
            #         ranking_date = opt.text.strip()
            #         break
            
            trs = soup.find_all('tr')

            for tr in trs:
                span_last_name = tr.find('span', class_='lastName')
                td_rank = tr.find('td', class_='rank')

                if span_last_name is not None and td_rank is not None:
                    last_name = span_last_name.text.strip()
                    rank = td_rank.text.strip()
                    data.append({'lastName': last_name, 'rank': rank, 'rankingDate': date})

            df = pd.DataFrame(data)

            if save:
                df.to_csv(file_path, index=False)
                logging.info(f"Data saved to {file_path}")
                print(f"Data saved to atp_rankings_{date}.csv")
        return "Saved all dataframes to disk."
    
class RankingCombiner:
    def __init__(self):
        self.dataframes = []

    def combine_dataframes(self):
        rankings_dir = 'datafetcher/data/rankings'
        all_files = [f for f in os.listdir(rankings_dir) if f.startswith('data_atp_rankings_') and f.endswith('.csv')]
        for file in all_files:
            file_path = os.path.join(rankings_dir, file)
            if os.path.exists(file_path):
                print(f"Loading file: {file_path}")
                df = pd.read_csv(file_path)
                self.dataframes.append(df)
            else:
                logging.warning(f"File {file_path} does not exist. Skipping.")
        combined_df = pd.concat(self.dataframes, ignore_index=True)
        return combined_df


if __name__ == "__main__":
    # with open('datafetcher/data/rankings/all_dates.txt', 'r') as f:
    #     dates = eval(f.read())
    # rs = RankingScraper(dates)
    # df = rs.create_dataframe(save=True)
    rc = RankingCombiner()
    combined_df = rc.combine_dataframes()
    print(combined_df.head())