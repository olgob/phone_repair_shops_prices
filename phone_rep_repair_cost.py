# PROGRAMMER: Olivier Gobron
# DATE CREATED: 11/11/2020
# REVISED DATE:
# PURPOSE: This file contains the code to scrap the repair cost of phones from https://www.phone-rep.dk/


from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd


def get_brand_df(brand, url, tablepress_id):
    """
    Get the urls of each brands

        Args:
            brand (str): brand name
            url (str): url
            tablepress_id (int): number corresponding to the desired table-id when we scrap the data

        Outputs:
            df (pd.DataFrame): dataframe containing the phone repair cost of a brand

    """
    print("extracting data from {} ...".format(url))
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    df = pd.DataFrame()
    df["phone_name"] = [x.contents[0] for x in
                        soup.find("table", id="tablepress-" + tablepress_id).find_all("td", class_="column-1")]
    df["cost"] = [x.contents[0] for x in
                          soup.find("table", id="tablepress-" + tablepress_id).find_all("td", class_="column-3")]
    df["cost"] = df["cost"].apply(
        lambda x: int(x.replace("TBA", "0 kr").replace("Ring til os", "0 kr").replace(".", "")[:-3]))
    df = df.replace(0, float("NaN"))
    df["phone_name"] = df["phone_name"].apply(lambda x: brand + " " + x)
    return df


def get_screen_repair_cost_phonerep():
    """
    Extract the repair costs from https://www.phone-rep.dk/

        Args:
            None

        Outputs:
            df (pd.DataFrame): dataframe containing the screen repair costs for all phone models available.

    """
    print("Starting extraction of the repair cost from https://www.phone-rep.dk/")

    df_samsung = get_brand_df(brand="Samsung", url="https://www.phone-rep.dk/reparation-af-samsung/", tablepress_id="1")
    df_huawei = get_brand_df(brand="Huawei", url="https://www.phone-rep.dk/reparation-af-huawei/", tablepress_id="6")
    df_sony = get_brand_df(brand="Sony", url="https://www.phone-rep.dk/reparation-af-sony/", tablepress_id="26")
    df_lg = get_brand_df(brand="LG", url="https://www.phone-rep.dk/reparation-af-lg/", tablepress_id="3")
    df_oneplus = get_brand_df(brand="OnePlus", url="https://www.phone-rep.dk/reparation-af-one-plus/",
                              tablepress_id="5")
    df_nokia = get_brand_df(brand="Nokia", url="https://www.phone-rep.dk/reparation-af-nokia/", tablepress_id="4")
    df_motorola = get_brand_df(brand="Motorola", url="https://www.phone-rep.dk/reparation-af-motorola/",
                               tablepress_id="7")

    df = pd.DataFrame()

    # df_lg["name"] = df_lg["name"].apply(lambda x: x.replace("LG LG", "LG"))

    # df_oneplus["name"] = df_oneplus["name"].apply(lambda x: x.replace(" Skærm", ""))
    # df_oneplus.drop(11, inplace=True)
    # df_oneplus.drop(12, inplace=True)

    df = df.append([df_huawei, df_samsung, df_sony, df_lg, df_oneplus, df_nokia, df_motorola], ignore_index=True)

    df["phone_name"] = df["phone_name"].apply(lambda x: x.replace("(Original)", "")
                                              .replace("Skærm", "")
                                              .replace("/ ", "")
                                              .replace("()", "")
                                              .replace("One Plus", "OnePlus")
                                              .replace("& ", "")
                                              .strip())

    # remove duplicated words in the names of phone (such as OnePlus OnePlus 3 for example)
    df["phone_name"] = df["phone_name"].apply(lambda x: " ".join(list(dict.fromkeys(x.split()))))

    df = df.dropna(subset=["cost"], axis=0)
    df = df.drop([199, 200])

    screen_price = df[df["phone_name"] == "Nokia Lumia 630 635"]["cost"].values[0]
    df.append(pd.Series({"phone_name": "Nokia Lumia 630", "cost": screen_price}),
              ignore_index=True)
    df = df.append(pd.Series({"phone_name": "Nokia Lumia 635", "cost": screen_price}),
                   ignore_index=True)
    df = df.drop(df[df["phone_name"] == "Nokia Lumia 630 635"].index, axis=0)

    # manual adjustment
    df["phone_name"] = df["phone_name"].apply(lambda x: x.replace("Huawei Honor", "Honor"))
    df["phone_name"] = df["phone_name"].apply(lambda x: manual_match(x))

    df.to_pickle("../data/repair_cost_phone_republic.pkl")
    print("Data saved in ../data/repair_cost_phone_republic.pkl")

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
    manual_matching = {"Honor 5": "Huawei Y5II",
                       "Huawei Ascend Mate 7": "Huawei Ascend Mate7",
                       "Huawei P Smart Plus": "Huawei P Smart+ 2019",
                       "Huawei P8 Lite": "Huawei P8 Lite (2017)",
                       "Huawei P8 Max": "Huawei P8max",
                       "Huawei Y5 (2018)": "Huawei Y5 Prime (2018)",
                       "Huawei Y5II 3G Honor 5": "Huawei Y5II",
                       "Huawei Y6 4G": "Huawei Y6 (2019)",
                       "Huawei Y6 Pro 4G": "Huawei Y6 Pro (2019)",
                       "Samsung Galaxy A3 (2015)": "Samsung Galaxy A3 (2016)",
                       "Samsung Galaxy A5 (2015)": "Samsung Galaxy A5 (2016)",
                       "Samsung Galaxy A5 (2018)": "Samsung Galaxy A5 (2017)",
                       "Samsung Galaxy A7 (2015)": "Samsung Galaxy A7 (2016)",
                       "Samsung Galaxy A8 Plus (2018)": "Samsung Galaxy A8+ (2018)",
                       "Samsung Galaxy J1 (2015)": "Samsung Galaxy J1",
                       "Samsung Galaxy J4 Plus (2018)": "Samsung Galaxy J4+",
                       "Samsung Galaxy J6 (2018)": "Samsung Galaxy J6",
                       "Samsung Galaxy J6 Plus (2018)": "Samsung Galaxy J6+",
                       "Samsung Galaxy Note 10": "Samsung Galaxy Note10",
                       "Samsung Galaxy Note 10 Plus": "Samsung Galaxy Note10+",
                       "Samsung Galaxy Note 8": "Samsung Galaxy Note8",
                       "Samsung Galaxy Note 9": "Samsung Galaxy Note9",
                       "Samsung Galaxy S10 Plus": "Samsung Galaxy S10+",
                       "Samsung Galaxy S20 Plus": "Samsung Galaxy S20+",
                       "Samsung Galaxy S4": "Samsung I9500 Galaxy S4",
                       "Samsung Galaxy S4 Mini": "Samsung I9190 Galaxy S4 mini",
                       "Samsung Galaxy S6 Edge Plus": "Samsung Galaxy S6 edge+",
                       "Samsung Galaxy S8 Plus": "Samsung Galaxy S8+",
                       "Samsung Galaxy S9 Plus": "Samsung Galaxy S9+",
                       "Sony Xperia M4 Aqua + Dualsim": "Sony Xperia M4 Aqua Dual"
                       }

    if phone_name in manual_matching.keys():
        phone_name = manual_matching[phone_name]
    else:
        pass
    return phone_name
