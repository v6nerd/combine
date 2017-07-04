cd /opt
sudo mkdir threatintel
sudo chown `whoami`:`whoami` /opt/threatintel
git clone https://github.com/mlsecproject/combine
cd combine
sudo apt-get install python-dev python-pip python-virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install grequests unicodecsv feedparser netaddr pygeoip sortedcontainers
cp /opt/combine/combine-example.cfg /opt/combine/combine.cfg

#python /opt/combine/reaper.py
#python /opt/combine/thresher.py
#python /opt/combine/baler.py
#/opt/logstash/logstash-plugin install logstash-output-csv


