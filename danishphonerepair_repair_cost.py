# PROGRAMMER: Olivier Gobron
# DATE CREATED: 11/11/2020
# REVISED DATE:
# PURPOSE: This file contains the code to scrap the repair cost of phones from https://danishphonerepair.dk/


from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_urls_brand():
    """
    Get the urls of each brands

        Args:
            None

        Outputs:
            urls_brand (str): list of urls
            brands (str): list of the brands names
    """
    url = "https://danishphonerepair.dk/reparationer/"
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    brands = []
    urls_brand = []
    brand_number = 0
    while True:
        # while there is still a url to extract
        try:
            brand = \
                soup.find_all("div", class_="et_pb_module et_pb_image et_pb_image_" + str(brand_number))[0].find("a")[
                    "href"]
            brands.append(brand.replace("/", "").replace("-", " ").replace("2", "").title().strip())
            brand_url = url + brand
            urls_brand.append(brand_url)
            brand_number += 1
        except IndexError:
            break
    return urls_brand, brands


def get_phones_specs(brand_url, brand):
    """
    Get phones specifications for a brand.

        Args:
            brand_url (str): url containing the phone models specification for this brand
            brand (str): name of the brand

        Outputs:
            df (pd.DataFrame): dataframe containing the phones repair cost for a brand
    """
    print("extracting data from ", brand_url, "...")

    df = pd.DataFrame(columns=["phone_name", "reparation", "cost"])
    brand_html = urlopen(brand_url)
    brand_soup = BeautifulSoup(brand_html, 'html.parser')
    phone_number = 0

    while True:

        try:
            phone_name = brand + " " + brand_soup.find_all("h5")[phone_number].contents[0]
            # print(phone_name)
            reparation_number = 0

            while True:
                # while there is a phone to extract
                try:
                    if reparation_number % 2 == 0:
                        reparation = \
                            brand_soup.find_all("tbody")[phone_number].find_all("td")[reparation_number].contents[0]
                        cost = \
                            brand_soup.find_all("tbody")[phone_number].find_all("td")[reparation_number + 1].contents[0]
                        phone_dict = {"phone_name": phone_name, "reparation": reparation, "cost": cost}
                        df = df.append(phone_dict, ignore_index=True)

                    reparation_number += 1

                except IndexError:
                    break

            phone_number += 1

        except IndexError:
            break

    return df


def lower_(text):
    """
    Lower case a text.

        Args:
            text (str): text to lowercase

        Output:
            text (str): lowercased text
    """
    try:
        return text.lower()
    except:
        pass


def detect_skærm(reparation_name):
    """
    Detect if the reparation is a screen reparation
    
        Args:
            reparation_name (str): name of the reparation

        Outputs:
            boolean: True if it is a screen reparation, else False
    """
    try:
        if "skærm" in reparation_name:
            return True
        else:
            return False
    except TypeError:
        return False


def convert_cost(cost):
    """
    Convert the cost of the reparation into float

        Args:
            cost (str): raw cost extracted

        Outputs:
            cost (float): cost of the reparation
    """
    try:
        cost = int(re.findall('[0-9]+', str(cost))[0])
    except:
        cost = None
    return cost


def modify_year(phone_name):
    """
    Put some parenthesis around year in the phone name

        Args:
            phone name (str):

        Outputs:
            phone_name (str):
    """
    try:
        year = re.findall("\d{4}", phone_name)[0]
        phone_name = phone_name.replace(year, "("+year+")")
    except:
        pass
    return phone_name


def get_screen_repair_cost_danishphonerepair():
    """
    Extract the repair costs from https://danishphonerepair.dk/

        Args:
            None

        Outputs:
            df (pd.DataFrame): dataframe containing the screen repair costs for all phone models available.

    """
    print("Starting extraction of the repair cost from https://danishphonerepair.dk/reparationer/")
    df = pd.DataFrame(columns=["phone_name", "reparation", "cost"])

    urls_brand, brands = get_urls_brand()
    for brand_url, brand in zip(urls_brand, brands):
        df = df.append(get_phones_specs(brand_url, brand))

    # filter reparations corresponding to screen repair
    df["reparation"] = df["reparation"].apply(lambda x: lower_(x))
    df = df[df["reparation"].apply(lambda x: detect_skærm(x))]

    # convert cost in float
    df["cost"] = df["cost"].apply(lambda x: convert_cost(x))

    # drop phone for which cost is unknown
    df = df.dropna()

    # drop duplicates keeping the more expensive cost and remove reparation column
    df = df.sort_values(by=["phone_name", "cost"]).drop_duplicates(subset=["phone_name"], keep="last")[
        ["phone_name", "cost"]]

    # remove duplicated words in the names of phone (such as OnePlus OnePlus 3 for example)
    df["phone_name"] = df["phone_name"].apply(lambda x: " ".join(list(dict.fromkeys(x.lower().split()))).title())

    # reset index
    df = df.reset_index()[["phone_name", "cost"]]

    # add parenthesis around year in the phone names
    df["phone_name"] = df["phone_name"].apply(lambda x: modify_year(x))

    # manual adjustment
    df["phone_name"] = df["phone_name"].apply(lambda x: manual_match(x))

    # save data
    df.to_pickle("../data/danishphonerepair_reparations_cost.pkl")
    print("Data saved in ../data/danishphonerepair_reparations_cost.pkl")

    return df

def manual_match(phone_name):
    """
    Manual match of phone names (possible to do it with regular expressions).
    Sorry not to have done it (shame bell!)

        Args:
            phone_name (str):

        Output:
            phone_name (str):
    """
    manual_matching = {"Htc M7": "HTC One",
                       "Htc M8": "HTC One (M8)",
                       "Htc M9": "HTC One M9",
                       "Huawei P Smart (2019)": "Huawei P smart 2019",
                       "Huawei P Smart Pro": "Huawei P smart Pro 2019",
                       "Huawei P8 Lite": "Huawei P8 Lite (2017)",
                       "Lg G3S": "LG G3 S",
                       "Nokia 5.1 Plus": "Nokia 5.1 Plus (Nokia X5)",
                       "Nokia 8.1": "Nokia 8.1 (Nokia X7)",
                       "Oneplus 1": "OnePlus One",
                       "Samsung Galaxy A8+": "Samsung Galaxy A8+ (2018)",
                       "Samsung Galaxy A9": "Samsung Galaxy A9 (2018)",
                       "Samsung Galaxy A90": "Samsung Galaxy A90 5G",
                       "Samsung Galaxy J5 (2015)": "Samsung Galaxy J5 (2016)",
                       "Samsung Galaxy Note": "Samsung Galaxy Note T879",
                       "Samsung Galaxy Note 10": "Samsung Galaxy Note10",
                       "Samsung Galaxy Note 10 +": "Samsung Galaxy Note10+",
                       "Samsung Galaxy Note 2": "Samsung Galaxy Note II N7100",
                       "Samsung Galaxy Note 5": "Samsung Galaxy Note5",
                       "Samsung Galaxy Note 8": "Samsung Galaxy Note8",
                       "Samsung Galaxy Note 9": "Samsung Galaxy Note9",
                       "Samsung Galaxy S4": "Samsung I9500 Galaxy S4",
                       "Samsung Galaxy S4 Mini": "Samsung I9190 Galaxy S4 mini",
                       "Samsung Galaxy S6 Edge +": "Samsung Galaxy S6 edge+",
                       "Sony Xperia Z3 Plus": "Sony Xperia Z3+",
                       "Sony Xperia Z4": "Sony Xperia Z4v"
                       }

    if phone_name in manual_matching.keys():
        phone_name = manual_matching[phone_name]
    else:
        pass
    return phone_name
