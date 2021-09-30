from bs4 import BeautifulSoup


def parsehtml(filename):
    f = open(filename, encoding='UTF8')
    content = f.read()
    # parse HTML
    soup = BeautifulSoup(content, 'html.parser')

    # actual code

    results = soup.find('table', attrs={'id': 'cont_win_2_Table1'})
    # print(results)

    first_result = results

    tableelements = first_result.find_all('tr')
    weekdays = ['Sunday', 'Monday', 'Tuesday',
                'Wednesday', 'Thursday', 'Friday', 'Saturday']
    countevents = 0
    eventarr = []

    # Concatenate each event with its corresponding day
    for element in tableelements:
        # print(element)
        # print(element.text)
        if element.text in weekdays:
            currentday = element.text
        else:
            eventarr.append(currentday + ', ' + element.text)
            # print(eventarr[countevents])
            # countevents += 1

    count1 = 0
    # cleaning up each event element
    for event in eventarr:

        # removing edge case of ----- (undefined capacity)
        event = event.replace('-----', '- 00 -')

        # changing delimiters
        event = event.replace(' - ', ',')
        event = event.replace(', ', ',')
        event = event.replace(' : ', ',')

        # removing keywords
        event = event.replace(' At ', ',')
        event = event.replace(' At', ',No Location')
        event = event.replace('الجيزة الرئيسي,', '')
        # reminder to add sheikh zayed
        event = event.replace('الجيزة الر��يسي,', '')
        event = event.replace('ملحق الكلية بالشيخ زايد,', ',')
        event = event.replace('even From ', '')
        event = event.replace('odd From ', '')
        event = event.replace('From ', '')
        event = event.replace(' To ', ',')
        event = event.replace(' ,', ',')

        # printing result
        # print(event)

        # updating list
        eventarr[count1] = event
        count1 += 1

    return eventarr
