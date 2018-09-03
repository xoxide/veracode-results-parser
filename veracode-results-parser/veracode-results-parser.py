import sys
import requests
import yaml
from requests.auth import HTTPBasicAuth
import defusedxml.lxml as lxml
from lxml.etree import XMLSyntaxError, XMLSchema
import time


def main():
    scan_ready = False
    config = get_config()
    schemas = get_schemas()
    buildinfo = get_local_build_info(schemas['build_info'])

    http_params = config.get('veracode')
    http_params['url'] = BUILD_INFO_URL
    http_params['buildId'] = buildinfo.get('build_id')
    http_params['appId'] = buildinfo.get('app_id')
    http_params['schema'] = schemas.get('build_info')
    http_params['type'] = 'build_info'

    while not scan_ready:

        remote_info = api_request(http_params)

        if remote_info['status'] == 'Results Ready':
            print('Ready to Scan!')
            scan_ready = True

            http_params['schema'] = schemas.get('detailed_report')
            http_params['url'] = DETAILED_REPORT_URL
            http_params['type'] = 'detailed_report'
            detailed_report = api_request(http_params)

            print(detailed_report)

            if (detailed_report['high_flaws'] + detailed_report['very_high_flaws'] + detailed_report['sca_vulns']) > 0:
                print('Build Failed!')
            else:
                print('Build Passed!')

        else:
            print('Scan not finished!')
            time.sleep(300)


# Accesses Veracode's API
def api_request(params):

    if params['type'] == 'build_info':
        payload = {'build_id': params['buildId'], 'app_id': params['appId']}
    else:
        payload = {'build_id': params['buildId']}

    try:
        r = requests.get(params['url'], params=payload, auth=HTTPBasicAuth(params['username'], params['password']))
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)

    try:
        returned_xml = lxml.fromstring(r.content)

        if not params['schema'].validate(returned_xml):
            raise ValueError('Schema Validation of ' + params['type'] + ' failed')

        if returned_xml.tag == 'error':
            raise ValueError(returned_xml.text)

        if params['type'] == 'build_info':
            data = parse_build_info(returned_xml)
        else:
            data = parse_detailed_report(returned_xml)
    except ValueError as e:
        print(e)
        sys.exit(1)
    except XMLSyntaxError:
        print('XML Syntax Error')
        sys.exit(1)
    except AttributeError as e:
        print('Remote XML return error: ' + str(e))
        sys.exit(1)

    return data


def get_config():
    try:
        with open('veracode.yaml', 'r') as file:
            config = yaml.load(file)
            file.close()
        return config
    except IOError:
        print('Invalid Config File')
        sys.exit(1)
    except yaml.scanner.ScannerError:
        print('Invalid yaml syntax')
        sys.exit(1)


def get_schemas():
    try:
        dr_xmlschema_doc = lxml.parse('detailedreport.xsd')
        bi_xmlschema_doc = lxml.parse('buildinfo.xsd')
        dr_xmlschema = XMLSchema(dr_xmlschema_doc)
        bi_xmlschema = XMLSchema(bi_xmlschema_doc)
        schemas = {'detailed_report': dr_xmlschema, 'build_info': bi_xmlschema}
    except IOError:
        print('Invalid Schema File')
        sys.exit(1)
    except XMLSyntaxError:
        print('XML Syntax Error ')
        sys.exit(1)
    except AttributeError as e:
        print('Local XML file error: ' + str(e))
        sys.exit(1)
    return schemas


def get_local_build_info(schema):
    try:
        buildinfo_xml = lxml.parse('build_info.xml')
        if not schema.validate(buildinfo_xml):
            print('Schema validation failed on local build info file')
            sys.exit(1)
        buildinfo_xml = buildinfo_xml.getroot()
        buildinfo = parse_build_info(buildinfo_xml)
    except IOError:
        print('Invalid File Local Build File')
        sys.exit(1)
    except XMLSyntaxError:
        print('XML Syntax Error ')
        sys.exit(1)
    except AttributeError as e:
        print('Local XML file error: ' + str(e))
        sys.exit(1)
    return buildinfo


# Pulls info out of the buildinfo xml tree
def parse_build_info(build_info_xml):
    appid = build_info_xml.get('app_id')
    buildid = build_info_xml.get('build_id')
    status = build_info_xml.find('.//{https://analysiscenter.veracode.com/schema/4.0/buildinfo}analysis_unit').get('status')

    build_info = {'app_id': appid, 'status': status, 'build_id': buildid}

    return build_info


def parse_detailed_report(detailed_report_xml):
    sev4flaws = 0
    sev5flaws = 0

    modules = detailed_report_xml.find('.//{https://www.veracode.com/schema/reports/export/1.0}modules')
    for module in modules:
        sev4flaws = module.get('numflawssev4')
        sev5flaws = module.get('numflawssev5')

    sca_vulns = detailed_report_xml.find('.//{https://www.veracode.com/schema/reports/export/1.0}software_composition_analysis').get('components_violated_policy')

    detailed_report = {'high_flaws': int(sev4flaws), 'very_high_flaws': int(sev5flaws), 'sca_vulns': int(sca_vulns)}

    return detailed_report


BUILD_INFO_URL = 'https://analysiscenter.veracode.com/api/5.0/getbuildinfo.do'
DETAILED_REPORT_URL = 'https://analysiscenter.veracode.com/api/4.0/detailedreport.do'

if __name__ == '__main__':
    main()
