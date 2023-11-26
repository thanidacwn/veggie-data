import json
import pandas as pd
from decouple import config
from yelp_api import YelpAPI

PLACEHOLDER_IMAGE = ('https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website'
                     '-design-mobile-app-no-photo-available_87543-11093.jpg')

print("\nThe search method using parameter from this documentation: \n"
      "https://docs.developer.yelp.com/reference/v3_business_search\n")
state = input("The state to query, ex: NY,TX,NJ (It'll find best matches for the inputted state): ") or 'NYC'
print("\nThe categories format using lists on the restaurants section of this website: \n"
      "https://docs.developer.yelp.com/docs/resources-categories\n")
category = input("The categories to query, ex: ,kebab,sushi,bbq (Follow this format to input multiple categories): ")
limit = input("How many restaurants would you like to query? (Maximum: 50): ") or '50'
file_directory = input("Which file should .csv should be written to? (ex: test_data.csv): ") or 'test_data.csv'
write_mode = input("Select write mode to write or append (ex: w)(ex: a)") or 'w'

with YelpAPI(config("API_KEY"), timeout_s=5.0) as yelp_api:
    search_results = yelp_api.search_query(location=state, categories="vegan,vegetarian" + category,
                                           term="restaurants", sort_by="best_match", limit=limit, radius=40000)
    json_results = json.dumps(search_results, indent=4)
    df = pd.json_normalize(search_results["businesses"])  # make json to DataFrame
    df = df.drop(['id', 'alias', 'is_closed', 'review_count', 'rating', 'transactions', 'phone', 'display_phone',
                  'distance', 'coordinates.latitude', 'coordinates.longitude', 'location.address1',
                  'location.address2',
                  'location.address3', 'location.zip_code', 'location.country'],
                 axis=1)  # drop all unnecessary columns
    df = df.replace(r'^\s*$', None, regex=True)  # fill the blank cell with NaN
    df['menu_link'] = "Check The Website for a Menu"  # add non-existed column to match current .csv template
    # change the name of element to match the template
    df = df.rename(columns={'name': 'restaurant_text', 'image_url': 'image', 'url': 'restaurant_link',
                            'categories': 'category', 'location.city': 'city', 'location.state': 'state',
                            'location.display_address': 'location', 'price': 'price_rate'})
    col_order = ['restaurant_text', 'location', 'category', 'restaurant_link', 'menu_link', 'price_rate',
                 'city', 'state', 'image']  # order of the original .csv template
    df['price_rate'] = df['price_rate'].replace('$', 'Cheap')  # change $ to 'Cheap'
    df['price_rate'] = df['price_rate'].replace('$$', 'Moderate')  # change $$ to 'Moderate'
    df['price_rate'] = df['price_rate'].replace('$$$', 'Expensive')  # change $$$ to 'Expensive'
    df['price_rate'] = df['price_rate'].replace('€', 'Cheap')  # change € to 'Cheap'
    df['price_rate'] = df['price_rate'].replace('€€', 'Moderate')  # change €€ to 'Moderate'
    df['price_rate'] = df['price_rate'].replace('€€€', 'Expensive')  # change €€€ to 'Expensive'
    df['price_rate'] = df['price_rate'].fillna(value='Moderate')  # fill empty price rate as moderate
    df['image'] = df['image'].fillna(value=PLACEHOLDER_IMAGE)  # fill empty image with placeholder
    df['category'] = df['category'].apply(lambda x: ', '.join(
        'Vegan Options' if c['title'] == 'Vegan' else
        'Vegetarian Friendly' if c['title'] == 'Vegetarian' else
        c['title'] for c in x))  # format the category t0 match the template
    df['location'] = df['location'].apply(lambda x: ', '.join(x))  # format the location t0 match the template
    df = df[col_order]  # change the DataFrame column order to match the original one
    df = df.drop_duplicates()
    if write_mode == 'a':
        df.to_csv(file_directory, index=False, mode='a', header=False)  # This line is to append the .csv
    else:
        df.to_csv(file_directory, index=False, mode='w')  # Drop the index column before convert to .csv
