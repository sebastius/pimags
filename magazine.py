#Mostly written by ChatGPT because i wanted to learn a few new tricks.
import requests
from bs4 import BeautifulSoup
import os
import argparse
from urllib.parse import unquote

def get_latest_issue(magazine):
    # Construct the URL for the magazine's issue list
    url = f"https://{magazine}.raspberrypi.com/issues"

    # Download the webpage
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <a> tags containing issue links
    issue_links = soup.find_all("a", href=True)

    # Extract the issue numbers from the links
    issue_numbers = []
    for link in issue_links:
        href = link["href"]
        if href.startswith("/issues/"):
            issue_number = href.split("/")[2]
            issue_numbers.append(int(issue_number))

    # Find the highest issue number
    latest_issue = max(issue_numbers)
    return latest_issue

def download_magpi_pdf(magazine, issue):
    # If issue argument is 'latest', get the latest available issue number
    if issue == "latest":
        issue = get_latest_issue(magazine)

    # Construct the URL
    url = f"https://{magazine}.raspberrypi.com/issues/{issue}/pdf/download"

    try:
        # Download the webpage
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Find the <iframe src=""> tag and extract the data between the quotes
        iframe_tag = soup.find("iframe", src=True)
        src_data = iframe_tag["src"]

        # Construct the download URL and download the file
        download_url = f"https://{magazine}.raspberrypi.com/" + src_data
        response = requests.get(download_url)
        response.raise_for_status()

        # Decode the filename and save the file to disk
        filename = unquote(os.path.basename(download_url))
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"File saved as {filename}")
        return True
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Download MagPi PDF")

    # Add the magazine argument with choices
    parser.add_argument("magazine", choices=["magpi", "hackspace"], help="Name of the magazine, either magpi or hackspace")
    parser.add_argument("issue", nargs="?", help="Issue number ('latest' for the latest issue, omit for all issues)")

    # Parse the command-line arguments
    args = parser.parse_args()
    # If issue is not provided, download all available issues
    if args.issue is None:
        issue = 1
        while download_magpi_pdf(args.magazine, issue):
            issue += 1
    else:
        # Call the function with the provided arguments
        download_magpi_pdf(args.magazine, args.issue)

    # Call the function with the provided arguments
    download_magpi_pdf(args.magazine, args.issue)

