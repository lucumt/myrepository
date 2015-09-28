# -*- coding:utf-8 -*-

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from planning.items import PlanningItem

import json
import urlparse

class PlanningSpider(Spider):

    name = 'planning-spider'
    allowed_domains = ['iso-ne.com']

    baseurl = 'http://www.iso-ne.com/api/1/get/documents.json?type=doc&type=ceii'
    baseurl += '&fq=-searchable%3Ano+AND+crafterSite%3Aisone+AND'
    baseurl += '+%2Bpublish_date_dt%3A[*%20TO%20*]+AND+-publishingVersion_i%3A[0%20TO%20*]'
    baseurl += '&q=-searchable%3Ano+AND+'

    facetquery = '+&facet=true&facet.limit=500&facet.field=key_issue.item.value_smv'
    facetquery += '&facet.field=document_committee.item.value_smv'
    facetquery += '&facet.field=events.item.key&facet.field=document_type.item.value_smv'
    facetquery += '&facet.field=file.item.fileType_s'

    def start_requests(self):
        '''
        Parse the start urls, each start url has a unique parse method the parse the item details.
        '''

        urls = [
            'http://www.iso-ne.com/system-planning/system-plans-studies/rsp',
            'http://www.iso-ne.com/system-planning/system-plans-studies/celt',
            'http://www.iso-ne.com/system-planning/system-plans-studies/emissions',
            'http://www.iso-ne.com/system-planning/system-plans-studies/interconnection-request-studies',
            'http://www.iso-ne.com/system-planning/transmission-planning/proposed-plan-applications',
            'http://www.iso-ne.com/system-planning/transmission-planning/transmission-cost-allocations',
            'http://www.iso-ne.com/system-planning/transmission-planning/interconnection-request-queue',
            'http://www.iso-ne.com/system-planning/transmission-planning/ptf',
            'http://www.iso-ne.com/system-planning/transmission-planning/ferc-form-no-715-reports',
            'http://www.iso-ne.com/system-planning/resource-planning/installed-capacity-requirements',
            'http://www.iso-ne.com/system-planning/resource-planning/nonprice-retirement',
            'http://www.iso-ne.com/system-planning/resource-planning/gads-reporting',
            'http://www.iso-ne.com/system-planning/system-forecasting/energy-efficiency-forecast',
            'http://www.iso-ne.com/system-planning/system-forecasting/distributed-generation-forecast',
            'http://www.iso-ne.com/system-planning/system-forecasting/load-forecast',
            'http://www.iso-ne.com/system-planning/key-study-areas/eastern-connecticut',
            'http://www.iso-ne.com/system-planning/key-study-areas/greater-boston',
            'http://www.iso-ne.com/system-planning/key-study-areas/greater-hartford',
            'http://www.iso-ne.com/system-planning/key-study-areas/maine',
            'http://www.iso-ne.com/system-planning/key-study-areas/neews',
            'http://www.iso-ne.com/system-planning/key-study-areas/pittsfield-greenfield',
            'http://www.iso-ne.com/system-planning/key-study-areas/sema-ri',
            'http://www.iso-ne.com/system-planning/key-study-areas/swct',
            'http://www.iso-ne.com/system-planning/key-study-areas/vt-nh'
            ]

        for url in urls:
            if url == urls[0]:
                baseurl = self.form_rsp()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Regional System Plan and Related Analyses'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[1]:
                baseurl = self.form_celt()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'CELT Reports'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[2]:
                baseurl = self.form_emissions()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Emissions Reports'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[3]:
                baseurl = self.form_studies()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Interconnection Request Studies'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[4]:
                baseurl = self.form_applications()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Transmission Planning - Proposed Plan Applications'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[5]:
                baseurl = self.form_allocations()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Transmission Planning - Transmission Cost Allocation'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[6]:
                baseurl = self.form_request_queue()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Transmission Planning - Interconnection Request Queue'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[7]:
                baseurl = self.form_ptf()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Transmission Planning - PTF Catalog'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[8]:
                baseurl = self.form_715_reports()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Transmission Planning - FERC Form 715 Reports'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[9]:
                baseurl = self.form_capacity_requirements()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Resource Planning - Installed Capacity Requirements'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[10]:
                baseurl = self.form_nonprice_retirement()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Resource Planning - Nonprice Retirement Requests and Determination Letters'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[11]:
                baseurl = self.form_gads_reporting()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Resource Planning - GADS Reporting'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[12]:
                baseurl = self.form_efficiency_forecast()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Energy-Efficiency Forecast'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[13]:
                baseurl = self.form_generation_forecast()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Energy-Efficiency Forecast'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[14]:
                baseurl = self.form_load_forecast()
                params = {'source':'ISO-NE', 'where':'ISO-NE', 'type':'Load Forecast'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[15]:
                baseurl = self.form_connecticut()
                params = {'source':'ISO-NE', 'where':'CT', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[16]:
                baseurl = self.form_boston()
                params = {'source':'ISO-NE', 'where':'MA', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[17]:
                baseurl = self.form_hartford()
                params = {'source':'ISO-NE', 'where':'CT', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[18]:
                baseurl = self.form_maine()
                params = {'source':'ISO-NE', 'where':'ME', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[19]:
                baseurl = self.form_neews()
                params = {'source':'ISO-NE', 'where':'CT,RI,MA', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[20]:
                baseurl = self.form_greenfield()
                params = {'source':'ISO-NE', 'where':'MA', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[21]:
                baseurl = self.form_sema_ri()
                params = {'source':'ISO-NE', 'where':'MA,RI', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[22]:
                baseurl = self.form_swct()
                params = {'source':'ISO-NE', 'where':'CT', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)
            elif url == urls[23]:
                baseurl = self.form_vt_nh()
                params = {'source':'ISO-NE', 'where':'VT', 'type':'Key Study Areas'}
                yield Request(baseurl, meta={'params':params}, callback=self.parse_item_count)               
            else:
                pass

    def parse_item_count(self, response):
        '''
        Find the total records of each request url and then parse the item details.
        '''

        responsedata = json.loads(response.body)
        url = response.url[0:-1]+bytes(responsedata['response']['numFound'])+'&sort=publish_date_dt%20desc'
        params = response.meta['params']
        yield Request(url, meta={'params':params}, callback=self.parse_item)

    def parse_item(self, response):
        '''
        Parse the detail item information and return it.
        '''

        records = []
        params = response.meta['params']
        responsedata = json.loads(response.body)
        for document in responsedata['response']['documents']:
            pitem = PlanningItem()
            pitem['source'] = params['source']
            pitem['where'] = params['where']
            pitem['type'] = params['type']
            pitem['title'] = document['document_title_s']
            pitem['date'] = document['createdDate']
            pitem['url'] = urlparse.urljoin('https://smd.iso-ne.com', document['file.item.key'])
            if document.get('document_description'):
                pitem['description'] = document['document_description']
            records.append(pitem)
        return records

    def form_rsp(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-plans-studies/rsp
        '''

        requesturl = self.baseurl+' ('
        requesturl += 'document_type.item.value_smv%3A%22System%20Maps%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Planning%20Projects%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Planning%20Guides%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Regional%20System%20Plans%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22CT%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22MA%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22ME%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22NH%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Regional%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22RI%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22VT%20System%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Planning%20Reports%22'
        requesturl += ' )'
        requesturl += '+&start=0&rows=1'
        return requesturl

    def form_celt(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-plans-studies/celt
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22CELT%20Forecast%20Details%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22CELT%20Reports%22'
        requesturl += ')'
        requesturl += '+&start=0&rows=1'
        return requesturl

    def form_emissions(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-plans-studies/emissions
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Emissions%20Reports%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_studies(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-plans-studies/interconnection-request-studies
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22CT%20Queue%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22MA%20Queue%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22ME%20Queue%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22NH%20Queue%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22RI%20Queue%20Studies%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22VT%20Queue%20Studies%22'
        requesturl += ')'
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_applications(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/transmission-planning/proposed-plan-applications
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Proposed%20Plan%20Forms%22'
        requesturl += '+OR+document_type.item.value_smv%3A%2218.4%20Proposed%20Plan%20Application%20Approvals%20%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22I.3.9%20Proposed%20Plan%20Application%20Approvals%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Proposed%20Plan%20Application%20Status%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_allocations(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/transmission-planning/transmission-cost-allocations
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22TCA%20Application%20Determination%20Letters%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22TCA%20Application%20Projects%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Glenbrook%20Cables%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Maine%20Power%20Reliability%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22VELCO%20Southern%20Loop%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22NSTAR%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22SWCT%20Reliability%20Phase%201%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22TCA%20Application%20Project%20Costs%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22Seabrook%205-Breaker%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22SWCT%20Reliability%20Phase%202%20TCA%20Application%20Project%20Materials%22'
        requesturl += '+OR+document_type.item.value_smv%3A%22TCA%20Application%20Status%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_request_queue(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/transmission-planning/interconnection-request-queue
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Interconnection%20Status%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_ptf(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/transmission-planning/ptf
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22PTF%20Catalogs%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_715_reports(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/transmission-planning/ferc-form-no-715-reports
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22FERC%20Form%20No.%20715%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_capacity_requirements(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/resource-planning/installed-capacity-requirements
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Installed%20Capacity%20Requirements%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_nonprice_retirement(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/resource-planning/nonprice-retirement
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Nonprice%20Retirement%20Letters%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_gads_reporting(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/resource-planning/gads-reporting
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22GADS%20Materials%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_efficiency_forecast(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-forecasting/energy-efficiency-forecast
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Energy%20Efficiency%20Forecasts%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_generation_forecast(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-forecasting/distributed-generation-forecast
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22Energy%20Efficiency%20Forecasts%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_load_forecast(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/system-forecasting/load-forecast
        '''

        requesturl = self.baseurl+'('
        requesturl += 'document_type.item.value_smv%3A%22CELT%20Forecast%20Details%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_connecticut(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/eastern-connecticut
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Eastern%20CT%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_boston(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/greater-boston
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Greater%20Boston%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_hartford(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/greater-hartford
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Greater%20Hartford%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_maine(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/maine
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Maine%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_neews(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/neews
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22New%20England%20East%20West%20Solution%20(NEEWS)%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_greenfield(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/pittsfield-greenfield
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Pittsfield%20and%20Greenfield%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_sema_ri(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/sema-ri
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Southeastern%20Massachusetts%20and%20Rhode%20Island%20(SEMA/RI)%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_swct(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/swct
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Southwest%20Connecticut%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl

    def form_vt_nh(self):
        '''
        Build the request url for http://www.iso-ne.com/system-planning/key-study-areas/vt-nh
        '''

        requesturl = self.baseurl+'('
        requesturl += 'key_issue.item.value_smv%3A%22Vermont%20and%20New%20Hampshire%20Key%20Study%20Area%22'
        requesturl += ')'
        requesturl += self.facetquery
        requesturl += '&start=0&rows=1'
        return requesturl