import ConfigParser
import grequests
import json
import sys
from logger import get_logger
import logging


logger = get_logger('reaper')

def exception_handler(request, exception):
    logger.error("Request %r failed: %r" % (request, exception))

def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    inbound_url_file = config.get('Reaper', 'inbound_urls')
    outbound_url_file = config.get('Reaper', 'outbound_urls')

    try:
        with open(inbound_url_file, 'rb') as f:
    	    #inbound_urls = [url.rstrip('\n') for url in f.readlines()]
	    inbound_lines = [line.split(",") for line in f.readlines()]
	    inbound_urls=[]
	    inbound_utags=[]
	    inbound_files=[]
	    inbound_ftags=[]
	    logger.info('Fetching inbound URLs')
	    for i in range(len(inbound_lines)):
		if inbound_lines[i][0].startswith('file://'):
			inbound_files.append(inbound_lines[i][0].partition('://')[2])
			inbound_ftags.append(inbound_lines[i][1].strip('\n'))
		else:
			inbound_urls.append(inbound_lines[i][0])
			inbound_utags.append(inbound_lines[i][1].strip('\n'))
    except EnvironmentError as e:
        logger.error('Reaper: Error while opening "%s" - %s' % (inbound_url_file, e.strerror))
        return

    try:
        with open(outbound_url_file, 'rb') as f:
            #outbound_urls = [url.rstrip('\n') for url in f.readlines()]
	    logger.info('Fetching outbound URLs')
            outbound_lines = [line.split(",") for line in f.readlines()]
            outbound_urls=[]
            outbound_utags=[]
	    outbound_files=[]
	    outbound_ftags=[]
            for i in range(len(outbound_lines)):
		if outbound_lines[i][0].startswith('file://'):
			outbound_files.append(outbound_lines[i][0].partition('://')[2])
                        outbound_ftags.append(outbound_lines[i][1].strip('\n'))
		else:
                	outbound_urls.append(outbound_lines[i][0])
                	outbound_utags.append(outbound_lines[i][1].strip('\n'))
    except EnvironmentError as e:
        logger.error('Reaper: Error while opening "%s" - %s' % (outbound_url_file, e.strerror))
        return

    ## Setting the User-Agent to something spiffy
    #headers = {'User-Agent': 'MLSecProject-Combine/0.1.2 (+https://github.com/mlsecproject/combine)'}
    headers = {'User-Agent': 'MLSecProject-Combine'}


    #logger.info('Fetching inbound URLs')
    #inbound_files=[]
    #for url in inbound_urls:
    #    if url.startswith('file://')
    #	    for url in inbound_urls:
    #         	inbound_files.append(url.partition('://')[2])
    #        	inbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in inbound_urls]
    inbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses if response]
    inbound_harvest=[]
    for response in inbound_responses:
	if response.status_code == 200:
		url_index=inbound_urls.index(response.url.strip())
		tmp=response.url, response.status_code, inbound_utags[url_index], response.text
		inbound_harvest.append(tmp)
    for i in range(len(inbound_files)):
        try:
            with open(inbound_files[i],'rb') as f:
                inbound_harvest.append(('file://'+inbound_files[i], 200, inbound_ftags[i], f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    #logger.info('Fetching outbound URLs')
    #outbound_files=[]
    #for url in outbound_urls:
    #    if url.startswith('file://'):
    #        outbound_files.append(url.partition('://')[2])
    #        outbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in outbound_urls]
    outbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    #outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses if response]
    outbound_harvest = []
    for response in outbound_responses:
        if response.status_code == 200:
                url_index=outbound_urls.index(response.url.strip())
		tmp=response.url, response.status_code, outbound_utags[url_index], response.text
                outbound_harvest.append(tmp)
    for i in range(len(outbound_files)):
        try:
            with open(outbound_files[i],'rb') as f:
                outbound_harvest.append(('file://'+outbound_files[i], 200, outbound_ftags[i], f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (ountbound_files[i], e.strerror))

    logger.info('Storing raw feeds in %s' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
