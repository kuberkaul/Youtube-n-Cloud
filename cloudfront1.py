import boto

s3 = boto.connect_s3()

bucket_name = "myyoutube"
bucket = s3.get_bucket(bucket_name)


import boto
from boto.cloudfront.distribution import DistributionConfig
from boto.cloudfront.exception import CloudFrontServerError

import re




def get_domain_from_xml(xml):
    results = re.findall("<DomainName>([^<]+)</DomainName>", xml)
    return results[0]

#custom class to hack this until boto v2.0 is released
class HackedStreamingDistributionConfig(DistributionConfig):

    def __init__(self, connection=None, origin='', enabled=False,
                 caller_reference='', cnames=None, comment='',
                 trusted_signers=None):
        DistributionConfig.__init__(self, connection=connection,
                                    origin=origin, enabled=enabled,
                                    caller_reference=caller_reference,
                                    cnames=cnames, comment=comment,
                                    trusted_signers=trusted_signers)

    #override the to_xml() function
    def to_xml(self):
        s = '<?xml version="1.0" encoding="UTF-8"?>\n'
        s += '<StreamingDistributionConfig xmlns="http://cloudfront.amazonaws.com/doc/2010-07-15/">\n'

        s += '  <S3Origin>\n'
        s += '    <DNSName>%s</DNSName>\n' % self.origin
        if self.origin_access_identity:
            val = self.origin_access_identity
            s += '    <OriginAccessIdentity>origin-access-identity/cloudfront/%s</OriginAccessIdentity>\n' % val
        s += '  </S3Origin>\n'


        s += '  <CallerReference>%s</CallerReference>\n' % self.caller_reference
        for cname in self.cnames:
            s += '  <CNAME>%s</CNAME>\n' % cname
        if self.comment:
            s += '  <Comment>%s</Comment>\n' % self.comment
        s += '  <Enabled>'
        if self.enabled:
            s += 'true'
        else:
            s += 'false'
        s += '</Enabled>\n'
        if self.trusted_signers:
            s += '<TrustedSigners>\n'
            for signer in self.trusted_signers:
                if signer == 'Self':
                    s += '  <Self/>\n'
                else:
                    s += '  <AwsAccountNumber>%s</AwsAccountNumber>\n' % signer
            s += '</TrustedSigners>\n'
        if self.logging:
            s += '<Logging>\n'
            s += '  <Bucket>%s</Bucket>\n' % self.logging.bucket
            s += '  <Prefix>%s</Prefix>\n' % self.logging.prefix
            s += '</Logging>\n'
        s += '</StreamingDistributionConfig>\n'

        return s

    def create(self):
        response = self.connection.make_request('POST',
            '/%s/%s' % ("2010-11-01", "streaming-distribution"),
            {'Content-Type' : 'text/xml'},
            data=self.to_xml())

        body = response.read()
        if response.status == 201:
            return body
        else:
            raise CloudFrontServerError(response.status, response.reason, body)


cf = boto.connect_cloudfront()

s3_dns_name = "myyoutube.s3.amazonaws.com"
comment = "example streaming distribution"
oai = "E1AW1XGTSL6Z0F"

#Create a distribution that does NOT need signed URLS
hsd = HackedStreamingDistributionConfig(connection=cf, origin=s3_dns_name, comment=comment, enabled=True)
hsd.origin_access_identity = oai
basic_dist = hsd.create()
print("Distribution with basic URLs: %s" % get_domain_from_xml(basic_dist))

import base64
import time


# Reference : http://stackoverflow.com

