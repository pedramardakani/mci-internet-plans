# List all MCI tariff plans
#
# Copyright (C) 2022 Pedram Ashofteh Ardakani <pedramardakani@pm.me>
#
# License GPLv3+: GNU General public license version 3 or later.  This is
# free software: you are free to change and redistribute it.  There is NO
# WARRANTY, to the extent permitted by law.

from selenium import webdriver

def save_to_disk(items, fields, filename):
    """
    Take a list of items, collect the given fields, and save to file
    """
    with open(filename, 'w') as f:

        import datetime
        now = datetime.datetime.now()
        f.write(f"# Date accessed: {str(now)}\n")

        for i, field in enumerate(fields):
            f.write(f"# Column {i+1}: {field}\n")

        # Insert all data
        rows = []
        for item in items:
            row = ""
            for field in fields:
                row += f"{item.get(field)} "

            # Row is ready
            f.write(f"{row}\n")





def get_items_in_page(driver, attributes, filter_by: dict={}):
    """
    Take the driver, collect the given attributes from pacakge list items,
    filter the results by the 'filter_by' option.

    'filter_by' is an optional dictionary. Its key and value are the
    attribute name and values we don't need. In the default example, it
    would be 'data-package-type: new-sub' which indicates this package is
    only for new subscribers.
    """

    # Read all tariff-plans available in this page
    li = driver.find_elements(by='class name', value='package-list-item')

    # Collect all items found in list
    items = []
    for item in li:
        info = {}

        # Filter-out unwanted items
        keep=True
        for k in filter_by.keys():
            if item.get_attribute(k) == filter_by.get(k):
                keep=False
                break

        if keep is False:
            continue

        # Store values tagged with attribute-name
        for att in attributes:
            info.update({
                att: item.get_attribute(att)
            })

        # Inserted all attributes, now append to all items
        items.append(info)

    # Done
    return items


def duration_to_num(items):

    for i, item in enumerate(items):
         d = str(item['data-duration'])
         if 'thirty-days' in d:
             item['data-duration'] = 30
         elif 'fourth-month' in d:
             item['data-duration'] = 30 * 4
         elif 'one-day' in d:
              item['data-duration'] = 1
         elif 'seven-days' in d:
              item['data-duration'] = 7
         elif 'two-month' in d:
              item['data-duration'] = 30 * 2

         items[i].update(item)

    return items


if __name__ == "__main__":

    # USER DEFINED VALUES
    # -------------------

    # Final results will be here
    output_name = "notrino-plans.dat"

    # Read all items in this page for given attributes
    attributes = (
        'data-price',
        'data-volume',
        'data-duration',
    )

    # Do not consider the packages that are only for new subscribers
    filter_list = ({ "data-package-type": "new-sub" } )




    # MAIN ROUTINE
    # ------------

    # Target URL
    target_url = 'https://mci.ir/notrino-plans'

    # Install geckodriver on your OS first, and then choose firefox
    driver = webdriver.Firefox()

    # Go to webpage
    driver.get(target_url)

    items = get_items_in_page(driver, attributes)

    # Get the rest of the packages on the following pages
    nextpage = driver.find_element(by='id', value='nextPageList')
    while( nextpage.get_property('disabled') is False ):
        nextpage.click()
        nextpage = driver.find_element(by='id', value='nextPageList')

        # Extending is better than appending since the items won't be nested!
        items.extend( get_items_in_page(driver, attributes, filter_by=filter_list) )

    items = duration_to_num(items)
    save_to_disk(items, attributes, output_name)
