# PROGRAMMER: Olivier Gobron
# DATE CREATED: 11/11/2020
# REVISED DATE:
# PURPOSE: This file contains the code to scrap the repair cost of phones from https://greenmind.dk/


from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re


def extract_phone_repair_cost():
    """
    This function extracts the repair cost from https://greenmind.dk/

        Args:

        Output:
            df : DataFrame containing the phone names and the repair cost for all types of reparations

    """
    # Initialization of the dataframe
    df = pd.DataFrame(columns=["phone_name", "reparation", "cost"])

    # Specification of the brand names that appear in the url
    brands = ["samsung", "priser-apple/apple-iphone", "oneplus", "huawei", "lg", "sony", "nokia", "htc"]

    for brand in brands:
        # we scrap the data brand by brand
        url = "https://greenmind.dk/reparation/" + brand
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        print("extracting data from {} ...".format(url))
        # we extract the urls corresponding to each of the phones on the page of the brand
        phones_urls = soup.find_all("a", class_="vc_general vc_btn3 vc_btn3-size-lg vc_btn3-shape-square vc_btn3-style-flat vc_btn3-block vc_btn3-color-grey")
        phones_urls = [x.get('href') for x in phones_urls]

        for phones_url in phones_urls:
            # we scrap the data phone by phone for each brand
            try:
                html = urlopen(phones_url)
                soup = BeautifulSoup(html, "html.parser")

                table = soup.find_all("td", style="")
                table = [x.contents[0] for x in table]
                table = np.reshape(table, [int(len(table) / 4), 4])

                for n, new_entry in enumerate(table):
                    new_row = {'phone_name': new_entry[0] + " " + new_entry[1], 'reparation': new_entry[2],
                           'cost': new_entry[3]}
                    # print("extracting data for {} ...".format(new_row["phone_name"]))
                    df = df.append(new_row, ignore_index=True)
            except:
                print("Impossible to extract data from {} ...".format(phones_url))

    return df


def filter_screen_reparation(df):
    """
    This function keep only the rows correponding to screen reparation

        Args:
            df : DataFrame containing all reparations type and cost for available data on https://greenmind.dk/

        Output:
            df : DataFrame containing only screen reparation cost for available data on https://greenmind.dk/

    """
    # we find the indexes where the name of the reparation type contains skærm or glas
    index = []
    vals = df["reparation"].values
    for val in vals:
        if (re.match("skærm", val.lower()) is not None) | (re.match("glas", val.lower()) is not None):
            index.append(True)
        else:
            index.append(False)
    # we extract the relevant rows
    # we remove the duplicates for which a phone have several screen options (we keep the most expensive one that
    # correspond to a replacement with an original screen
    df = df.iloc[index].sort_values(by=["phone_name", "cost"]).drop_duplicates(subset="phone_name", keep='last')
    return df


def convert_price(price):
    """
    This function convert a price in a str format ("? kr.") into float.

        Args:
            price: price in a string format ( ?? kr.)
        Output:
            price: Transformed price in an float format

    """
    price = price.replace("Kontakt os for pris", "")[:-4]
    if price == "":
        return None
    else:
        return float(price)


def get_screen_repair_cost_greenmind():
    """
    Main function that extract and preprocess data extracted from https://greenmind.dk/
    It scraps the data from the website, filter reparations that correspond to screen repair price, and preprocess the
    data to save a DataFrame containing name of phones and corresponding screen repair cost.

        Args:
            None

        Output:
            df: DataFrame containing name of phones and corresponding screen repair cost

    """

    print("Starting extraction of the repair cost from https://greenmind.dk/")

    df = extract_phone_repair_cost()

    # we keep only the screen reparations cost
    df = filter_screen_reparation(df)

    # conversion of price from str to float
    df["cost"] = df["cost"].apply(convert_price)

    # remove duplicated words in the names of phone (such as OnePlus OnePlus 3 for example)
    df["phone_name"] = df["phone_name"].apply(lambda x: " ".join(list(dict.fromkeys(x.split()))))

    # rename iphone SE first and second generation
    df["phone_name"] = df["phone_name"].apply(lambda x: x.replace("(1. gen.)", "").replace("(2. gen.)", "(2020)"))

    # we remove the reparation type as they all are screen repair
    df = df[["phone_name", "cost"]]

    # reset index
    df = df.reset_index().drop("index", axis=1)

    # manual_adjustments:
    df["phone_name"] = df["phone_name"].apply(lambda x: manual_match(x))

    df.to_pickle("../data/greenmind_reparations_cost.pkl")

    print("Data saved in ../data/greenmind_reparations_cost.pkl")
    return df


def manual_match(phone_name):
    """
    Perform a manual match of some of the model name with name used on https://www.gsmarena.com/

        Args:
            phone_name (str): name of the phone to modify

        Outputs:
            phone_name (str): modified name of the phone that matches on gsmarena
    """
    manual_matching = {"HTC One M8": "HTC One (M8)",
                       "Huawei Honor U8860": "Honor U8860",
                       "LG Nexus 4": "LG Nexus 4 E960",
                       "LG Optimus 2X P990": "LG Optimus 2X",
                       "LG Optimus 4X HD": "LG Optimus 4X HD P880",
                       "Samsung Galaxy Nexus": "Samsung Galaxy Nexus I9250",
                       "Samsung Galaxy Note": "Samsung Galaxy Note T879",
                       "Samsung Galaxy Note 10.1": "Samsung Galaxy Note 10.1 N8000",
                       "Samsung Galaxy Note 2": "Samsung Galaxy Note II N7100",
                       "Samsung Galaxy R": "Samsung I9103 Galaxy R",
                       "Samsung Galaxy S2": "Samsung I9100 Galaxy S II",
                       "Samsung Galaxy S2 Plus": "Samsung I9105 Galaxy S II Plus",
                       "Samsung Galaxy S3": "Samsung I9300 Galaxy S III",
                       "Samsung Galaxy S3 Mini": "Samsung I8190 Galaxy S III mini",
                       "Samsung Galaxy S4": "Samsung I9500 Galaxy S4",
                       "Samsung Galaxy S4 Mini": "Samsung I9190 Galaxy S4 mini",
                       "Samsung Galaxy S8 Plus": "Samsung Galaxy S8+",
                       "Sony Xperia Z Tablet": "Sony Xperia Tablet Z LTE",
                       "Sony Xperia Z2 Tablet": "Sony Xperia Z2 Tablet LTE"}

    if phone_name in manual_matching.keys():
        phone_name = manual_matching[phone_name]
    else:
        pass
    return phone_name


#if __name__ == '__main__':
#    get_screen_repair_cost_greenmind()
