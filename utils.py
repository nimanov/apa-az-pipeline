import time
import requests
import datetime
from bs4 import BeautifulSoup


def request_handler(url, n_times=10, sleep_time=60):
    """
    Handles the request. This function is written for the case when there is no response from given url.
    It requests the website 10(n_times) times with 60(sleep_time) delay.
    If there is no response after requesting 10(n_times) times with 60(sleep_time) delay, the function logs
    the url to the "error.log" file and this url is skipped.
    Parameters
    ----------
    url: The url that is supposed to be scraped.
    n_times: Number of time of the request that has to be sent to the url consecutively.
    sleep_time: The delay time between each requests.

    Returns
    -------
    In successful case it returns the BeautifulSoup object of html of the page, returns "NOT RESPONDING" otherwise.

    """
    f_error_log = open("error.log", "a", encoding="utf-8")
    for i in range(n_times):
        try:
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        except Exception as e:
            msg = "ERROR " + str(datetime.datetime.now()) + " "
            f_error_log.write(msg + url + " ==> " + str(e) + "\n")
            f_error_log.write("Requesting again after " + str(sleep_time/60) + " minutes\n")
            f_error_log.write("----------------------------------------------------------------------------------\n")
            time.sleep(sleep_time)
            continue
        else:
            f_error_log.close()
            return soup
    f_error_log.close()
    return "NOT RESPONDING"


def could_not_scraped(url, additional_msg=""):
    """
    This function logs the url of the page, when this url could not scraped. The function is used together with
    "request_handler()" in a case the "request_handler()" returns "NOT RESPONDING", since that message implies that
    the given url could not scraped, could_not_scraped() logs the url to "could_not_scraped.log" file.
    Parameters
    ----------
    url: The url that could not scraped
    additional_msg: Additional message is wiritten to the log file.

    Returns
    -------
    Nothing is returned
    """
    msg = " -- COULD NOT SCRAPED -- URL: "
    f_could_not_scraped = open("could_not_scraped.log", "a", encoding="utf-8")
    f_could_not_scraped.write(additional_msg + str(datetime.datetime.now()) + msg + url + "\n")
    f_could_not_scraped.close()