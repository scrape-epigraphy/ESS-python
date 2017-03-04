# ------------------------------------

__author__ = "Kaan Eraslan <kaaneraslan@gmail.com>"
__license__ = "MIT License, See LICENSE."

# Packages ------------------------

import bs4
import requests
import json
import unicodecsv as csv
from greek_accentuation.characters import base, strip_accents, strip_breathing, strip_length
import time

# ------------------------------------------

def get_page_url_text(url, header):
    """
    params:
    url, str.
    header, dict.

    return:
    pageAnalyse_cont, str.

    Simple. Take the url string,
    Take the header.
    Use get method on the url string
    with the specified header.
    """
    #
    if isinstance(url, str):
        pass
    #
    if isinstance(header, dict):
        pass
    #
    url_get = requests.Session()
    #
    try:
        url_brut = url_get.get(url, headers=header)
        if url_brut.status_code != 200:
        #
            raise ValueError("The response code is not 200, so no valid transaction occured.")
        else:
            pass
    except ValueError as bad_response:
        #
        url_brut = url_get.get(url, headers=header)
        # We try once more, for just in case...
        #
        if url_brut.status_code != 200:
            # Helas... World is such a cruel place sometimes.
            #
            print(bad_response + "\n\n")
            print(url_brut.status_code + "\n\n")
            print(url)
            #
            return None
        #
        else:
            pass
        #
    else:
        url_brut.encoding = "utf-8"
        pageAnalyse_cont = url_brut.text
#       pageAnalyse = url_brut.json()
    #
    return pageAnalyse_cont

def lemma_prep(lemma):
    """
    params: lemma, str.
    search_lemma, str.

    It takes a lemma, and
    strips the accents
    breathing marks
    and lenght marks
    """
    #
    if not isinstance(lemma, str):
        print("Parameter is not a string. The function is returning None. Here is the parameter that you've passed:\n\n")
        print(lemma)
        return
    else:
        lemma_strip_breathing = strip_breathing(lemma)
        lemma_strip_accent = strip_accents(lemma_strip_breathing)
        lemma_strip_length = strip_length(lemma_strip_accent)
        lemma_base_separe = [base(char) for char in lemma_strip_length]
        search_lemma = "".join(lemma_base_separe)
        #
        return search_lemma


def phi_search_url_prep(search_lemma="", phi_url_search=""):
    """
    params:
    search_lemma, str.
    phi_url_search, str.
    pageAnalyse_cont, str.

    return: phi_lem_search_dict, {}

    We start constructing our python dictionary for search page of the
    lemma.

    """
    #
    phi_lem_search_dict = {}
    phi_lem_search_dict["phi_lemma_searched"] = search_lemma
    phi_lem_search_dict["phi_lemma_search_url"] = phi_url_search + search_lemma
    #
    return phi_lem_search_dict


def phi_get_search_page(phi_lem_search_dict, phi_header):
    """
    params:
    phi_lem_search_dict, {}
    phi_header, {}
    return: phi_lem_search_dict, {}

    We add the search page to our dictionary.
    """
    #
    time.sleep(2)
    phi_lem_search_dict["phi_lemma_search_page"] = get_page_url_text(
        url=phi_lem_search_dict["phi_lemma_search_url"],header=phi_header)
    #
    return phi_lem_search_dict


def phi_page_verification(pageAnalyse_str):
    """
    params: pageAnalyse_str, str.
    return: True/False boolean

    Check if search had yielded any result at all. If not return None.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    url_verif = pageAnalyse.select_one("html body div div#error-page")
    #
    if url_verif is None:
        #
        return pageAnalyse_str
    else:
        #
        return None

def phi_search_page_test(phi_lem_search_dict):
    """
    params:
    phi_lem_search_dict, {}

    return:
    phi_lem_search_dict_modified, {}

    We take search page and see if it contains results.
    If it doesn't, we replace its value in our dictionary with None.
    """
    #
    phi_search_page = phi_lem_search_dict["phi_lemma_search_page"]
    phi_search_page_verfiy = phi_page_verification(phi_search_page)
    if phi_search_page_verfiy is None:
        phi_lem_search_dict["phi_lemma_search_page"] = None
    else:
        pass
    #
    return phi_lem_search_dict

def phi_lemma_url_all_search_pages(pageAnalyse_str, domain_url):
    """
    params: pageAnalyse_str, str.
    return: liste_url, list.

    Parse the search result page with BeautifulSoup to obtain the links to the other search pages if there is any.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    urls_css_result = pageAnalyse.select_one("html body div div#searchpage div.search table tbody tr td.num")
    #
    if urls_css_result is not None:
        #
        url_links = urls_css_result.find_all("a")
        liste_url = [domain_url + url.get("href") for url in url_links]
        #
    else:
        #
        liste_url = []
    #
    return liste_url


def phi_search_page_urls(phi_lem_search_dict, domain_url):
    """
    params: phi_lem_search_dict, {}

    return: phi_lem_search_dict, {}

    We take our search page dictionary and
    add the urls of other search pages containing
    results for the searched lemma

    """
    #
    phi_search_page = phi_lem_search_dict["phi_lemma_search_page"]
    if phi_search_page is not None:
        phi_lem_search_dict["phi_lemma_search_page_url_list"] = phi_lemma_url_all_search_pages(phi_search_page, domain_url=domain_url)
        #
    else:
        phi_lem_search_dict["phi_lemma_search_page_url_list"] = None
    #
    return phi_lem_search_dict



def phi_lemma_stats_general(phi_lem_search_dict, write_json=False, write_csv=False, path=""):
    """
    params:
    phi_lem_search_dict, str.
    write_json, boolean
    write_csv, boolean
    path, str.

    return: liste_dict_stat, [{},{},{},...]

    We take the statistics given by PHI in search page and arrange them in a python list of dicts.
    If write_json is changed to True, function writes this list of dicts as json to the path specified.
    If write_csv is changed to True, function writes the list of dicts as a csv file to the path specified.
    If both write flags stay false function returns a list of dicts

    """
    #
    if phi_lem_search_dict["phi_lemma_search_page"] is None:
        return None
    else:
        pass
    pageAnalyse_str = phi_lem_search_dict["phi_lemma_search_page"]
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    lemma_stats = pageAnalyse.select_one("html body div div#searchpage div.search table.stats tbody")
    #
    stat_lignes = lemma_stats.find_all("tr")
    #
    lemma_stat_liste = []
    #
    for stat in stat_lignes:
        #
        stat_dict = {}
        #
        stat_attestation = stat.find("td", class_="num a")
        stat_atte_txt = stat_attestation.get_text(strip=True)
        #
        stat_taux = stat.find("td", class_="num b")
        stat_taux_txt = stat_taux.get_text(strip=True)
        #
        stat_region = stat.find("td", class_="c")
        stat_reg_txt = stat_region.get_text(strip=True)
        #
        stat_dict["Attested_Numbers"] = stat_atte_txt
        stat_dict["Attestation_Ratio_Compared_to_Other_Lemmata_From_the_Region"] = stat_taux_txt
        stat_dict["Attestation_Region"] = stat_reg_txt
        #
        lemma_stat_liste.append(stat_dict)
    #
    if write_json == True and write_csv == True:
        with open(path+"/" + phi_lem_search_dict["phi_lemma_searched"] + "_stat_json.json","w", encoding="utf-8") as stat_json:
            json.dump(lemma_stat_liste, stat_json)
        #
        with open(path +"/" + phi_lem_search_dict["phi_lemma_searched"] + "_stat_csv.csv", "w", encoding="utf-8") as stat_csv:
            field_name_list = ["Attested_Numbers","Attestation_Ratio_Compared_to_Other_Lemmata_From_the_Region","Attestation_Region"]
            writerCsv = csv.DictWriter(stat_csv, fieldnames=field_name_list)
            writerCsv.writeheader()
            for lemma_stat in lemma_stat_liste:
                writerCsv.writerow(lemma_stat)
        #
    #
    elif write_json == True and write_csv == False:
        #
        with open(path + "/" + phi_lem_search_dict["phi_lemma_searched"] + "_stat_json.json","w", encoding="utf-8") as stat_json:
            json.dump(lemma_stat_liste, stat_json)
        #
    #
    elif write_json == False and write_csv == True:
        #
        with open(path + "/" + phi_lem_search_dict["phi_lemma_searched"] + "_stat_csv.csv", "w", encoding="utf-8") as stat_csv:
            field_name_list = ["Attested_Numbers","Attestation_Ratio_Compared_to_Other_Lemmata_From_the_Region","Attestation_Region"]
            writerCsv = csv.DictWriter(stat_csv, fieldnames=field_name_list)
            writerCsv.writeheader()
            for lemma_stat in lemma_stat_liste:
                writerCsv.writerow(lemma_stat)
            #
        #
    #
    elif  write_json == False and write_csv == False:
        return lemma_stat_liste

# ----------

def phi_lemma_stats_liste(phi_lem_search_dict_list):
    """
    params: phi_lem_search_dict_list, [{},{},{},...]
    return: phi_stats_liste, [].
    """
    #
    phi_stats_liste = []
    #
    for phi_lemma in phi_lem_search_dict_list:
        if phi_lemma["phi_lemma_search_page"] is not None:
            phi_lemma_stat_dict_liste = phi_lemma_stats_general(phi_lemma["phi_lemma_search_page"])
            for phi_lemma_stat_dict in phi_lemma_stat_dict_liste:
                phi_lemma_stat_dict["phi_lemma_searched"] = phi_lemma["phi_lemma_searched"]
                phi_stats_liste.append(phi_lemma_stat_dict)
    #
    return phi_stats_liste


def phi_get_lemma_total_search_page(phi_lem_search_dict, phi_header):
    """
    params: phi_lem_search_dict, {}
    return: phi_lem_search_dict, {}

    It checks if the search page have a result or results.
    Then it takes our search page urls in our dictionary, and gets their corresponding html representation.
    Then it deletes the phi_lemma_search_page key after adding its value to a newly created phi_lemma_search_page_list key.
    """
    #
    phi_lem_search_dict["phi_lemma_search_page_list"] = []
    if  phi_lem_search_dict["phi_lemma_search_page"] is not None and (phi_lem_search_dict["phi_lemma_search_page_url_list"] is None or len(phi_lem_search_dict["phi_lemma_search_page_url_list"]) == 0):
        phi_lem_search_dict["phi_lemma_search_page_list"] = phi_lem_search_dict["phi_lemma_search_page_list"].append(phi_lem_search_dict["phi_lemma_search_page"])
        phi_lem_search_dict.pop("phi_lemma_search_page", None)
    elif phi_lem_search_dict["phi_lemma_search_page_url_list"] is not None and len(phi_lem_search_dict["phi_lemma_search_page_url_list"]) > 0:
        phi_lem_search_dict["phi_lemma_search_page_list"] = phi_lem_search_dict["phi_lemma_search_page_list"].append(phi_lem_search_dict["phi_lemma_search_page"])
        phi_lem_search_dict.pop("phi_lemma_search_page", None)
        phi_search_page_url_list = phi_lem_search_dict["phi_lemma_search_page_url_list"]
        for phi_search in phi_search_page_url_list:
            phi_search_page = get_page_url_text(url=phi_search, header=phi_header)
            phi_lem_search_dict["phi_lemma_search_page_list"] = phi_lem_search_dict["phi_lemma_search_page_list"].append(phi_search_page)
            #
    return phi_lem_search_dict

# Burada Kaldın ----------------------------

def phi_lemma_indv_url(pageAnalyse_str, domain_url):
    """
    params: pageAnalyse, bs4.BeautifulSoup.
    return: liste_url, list.

    It takes the search page html as string.
    Finds the url of the text in which the
    searched lemma is attested.
    Then gets and creates the url.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    lemma_indv_css = pageAnalyse.select("html body div div#searchpage div.search div.dblclk div.matches div.sentr ul li a")
    #
    liste_url_indv = [domain_url + url.get("href") for url in lemma_indv_css]
    #
    return liste_url_indv


def phi_lemma_url_list(phi_lem_search_dict, phi_domain_url):
    """
    params: phi_lem_search_dict, {}
    return: phi_lem_search_dict, {}

    It takes the value of the search pages key in
    phi_lem_search_dict, and gives a list of
    urls in the concerning search page.

    """
    #
    phi_search_page_list = phi_lem_search_dict["phi_lemma_search_page_list"]
    phi_lem_search_dict["phi_lemma_text_url_list"] = []
    #
    for phi_search_page in phi_search_page_list:
        phi_url_liste = phi_lemma_indv_url(phi_search_page, domain_url = phi_domain_url)
        phi_lem_search_dict["phi_lemma_text_url_list"] = phi_lem_search_dict["phi_lemma_text_url_list"].append(phi_url_liste)
    #
    return phi_lem_search_dict


def phi_texte_dict_list(phi_lem_search_dict, phi_header, phi_main_url):
    """
    params:
    phi_lem_search_dict, {}
    phi_header, {}
    phi_main_url, str.

    return: phi_text_dict_total_list, []

    It takes the text url list, and gets the lemma
    pages of the corresponding url.
    Then maps the page, the lemma, and the url to
    a dictionary.
    Then appends the dictionary to a list.

    """
    #
    phi_text_dict_total_list = []
    phi_lemma_text_url_list = phi_lem_search_dict["phi_lemma_text_url_list"]
    #
    for phi_lemma_text_url in phi_lemma_text_url_list:
        phi_text_dict = {}
        time.sleep(1)
        phi_text_dict["phi_lemma_page"] = get_page_url_text(url=phi_main_url, header=phi_header)
        phi_text_dict["phi_lemma_text_url"] = phi_lemma_text_url
        phi_text_dict["phi_lemma_searched"] = phi_lem_search_dict["phi_lemma_searched"]
        phi_text_dict_total_list.append(phi_text_dict)
        #
    #
    return phi_text_dict_total_list


# Les informations liées au texte individuel -------------

def phi_lemma_region(text_pageAnalyse_str):
    """
    params:
    text_pageAnalyse_str, str.
    return: region, str.

    It takes the text page and returns the region
    indicated at title of the page.
    """
    #
    pageAnalyse = bs4.BeautifulSoup(text_pageAnalyse_str, "lxml")
    region_lemma = pageAnalyse.select_one("html body div div#textpage div.hdr1 span")
    #
    region = region_lemma.get_text(": ", strip=True)
    #
    return region


def phi_lemma_text_info(pageAnalyse_str):
    """
    params: pageAnalyse, bs4.BeautifulSoup.
    return: text_info, str.

    It takes the text page, and returns the
    information given under the title of the
    text.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    lemma_css_info = pageAnalyse.select_one("html body div div#textpage div.text div.tildeinfo span.ti")
    #
    text_info = lemma_css_info.get_text(" ", strip=True)
    #
    return text_info


def phi_lemma_text(pageAnalyse_str):
    """
    params: pageAnalyse, bs4.BeautifulSoup.
    return: lemma_text_dict, dict.

    It takes text page and maps the text to
    a dictionary by using line numbers as keys.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(pageAnalyse_str, "lxml")
    text_html = pageAnalyse.select_one("html body div div#textpage div.text div.greek table.grk")
    #
    # Count the lines --------
    #
    lines = text_html.find_all("tr")
    #
    list_lines = list(lines)
    list_number_lines = list(range(len(list_lines)))
    #
    lemma_text_dict_list = []
    #
    def no_class_attr(tag):
        """
        une fonctionne pour isoler les balises qui n'ont pas un attribut de 'class'
        """
        #
        return not tag.has_attr("class")
    #
    for no_line in list_number_lines:
        lemma_text_dict = {}
        line_txt_search = lines[no_line].find(no_class_attr)
        line_txt = line_txt_search.get_text(strip=True)
        lemma_text_dict["line_no"] = no_line + 1
        lemma_text_dict["line_text"] = line_txt
        #
        lemma_text_dict_list.append(lemma_text_dict)
    #
    return lemma_text_dict_list


def phi_lemma_line_variant(text_pageAnalyse_str):
    """
    params: text_pageAnalyse_str, str.
    return: lemma_text_dict, dict.

    It takes the text page, and searches the occurance
    of the lemma searched.
    It maps the line to a dictionary by using
    'phi_lemma_variant' and 'phi_lemma_variant_line_no' as keys.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(text_pageAnalyse_str, "lxml")
    text_html = pageAnalyse.select_one("html body div div#textpage div.text div.greek table.grk")
    #
    # Compter les lignes --------
    #
    lines = text_html.find_all("tr")
    #
    list_lines = list(lines)
    list_number_lines = list(range(len(list_lines)))
    #
    lemma_text_dict_list = []
    #
    def no_class_attr(tag):
        """
        une fonctionne pour isoler les balises qui n'ont pas un attribut de 'class'
        """
        #
        return not tag.has_attr("class")
    #
    for no_line in list_number_lines:
        if lines[no_line].find("span", class_="hit") is not None:
            lemma_text_dict = {}
            #
            lemma_search = lines[no_line].find("span", class_="hit")
            lemma_txt = lemma_search.get_text(strip=True)
            #
            lemma_text_dict["phi_lemma_variant"] = lemma_txt
            lemma_text_dict["phi_lemma_variant_line_no"] = no_line + 1
            lemma_text_dict_list.append(lemma_text_dict)
            #
        else:
            pass
    #
    return lemma_text_dict_list


def phi_text_id(text_pageAnalyse_str, domain_url):
    """
    params: pageAnalyse, bs4.BeautifulSoup.
    return: text_id, tuple.

    It takes a text page, finds the phi id.
    Returns a tuple with the id, and the url to the text.

    """
    #
    pageAnalyse = bs4.BeautifulSoup(text_pageAnalyse_str, "lxml")
    text_id_css = pageAnalyse.select_one("html body div div#textpage div.docref a")
    #
    text_url = domain_url + text_id_css.get("href")
    phi_id_no = text_id_css.get_text(strip=True)
    #
    text_id = (phi_id_no, text_url)
    #
    return text_id



def phi_text_page_parse(pageAnalyse_str, phi_main_url):
    """
    params: pageAnalyse_str, str.
    return: phi_page_dict, dict.

    It takes the precedent functions and maps their
    information to a dictionary.
    """
    #
    phi_page_dict = {}
    phi_page_dict["phi_text_id_no"] = phi_text_id(pageAnalyse_str, domain_url=phi_main_url)[0]
    phi_page_dict["phi_text_region"] = phi_lemma_region(pageAnalyse_str)
    phi_page_dict["phi_text_url"] = phi_text_id(pageAnalyse_str, domain_url=phi_main_url)[1]
    phi_page_dict["phi_text_info"] = phi_lemma_text_info(pageAnalyse_str)
    phi_page_dict["phi_text"] = phi_lemma_text(pageAnalyse_str)
    #
    return phi_page_dict


def phi_text_line_parse(text_pageAnalyse_str, phi_main_url="", lemma_searched=""):
    """
    params:
    text_pageAnalyse_str, str.
    domain_url, str.
    lemma_searched, str.

    return: phi_variante_liste, [{},{}, ...]

    It takes the text page, gives a list of dicts.
    The dictionary contains text id, and the line number,
    and the searched lemma.

    """
    #
    phi_variant_list = []
    phi_page_variants = phi_lemma_line_variant(text_pageAnalyse_str)
    for phi_variant in phi_page_variants:
        if len(phi_variant) > 0:
            phi_variant["phi_lemma_searched"] = lemma_searched
            phi_variant["phi_text_id"] = phi_text_id(text_pageAnalyse_str, domain_url=phi_main_url)
            phi_variant_list.append(phi_variant)
            #
    return phi_variant_list
