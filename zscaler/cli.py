import zscaler

import argparse


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='option_picked')

    parser_a = subparsers.add_parser('url_cat_lookup', help='This feature will provide category lookups for URL')
    parser_a.add_argument('--credentials', required=True, help='Path to credentials file')
    parser_a.add_argument('--url', required=True, help='URL to lookup for categorization')

    parser_c = subparsers.add_parser('url_cat_lookup_csv',
                                     help='This feature will provide category lookups for URLs in CSV format')
    parser_c.add_argument('--credentials', required=True, help='Path to credentials file.')
    parser_c.add_argument('--csv_file', required=True, help='Path to CSV file. See example csv format: ')

    parser_b = subparsers.add_parser('dc_lookup', help='This feature will provide 2 closest Zscaler datacenters')
    parser_b.add_argument('--cloud', choices=['zscaler.net', 'zscalerone.net', 'zscalertwo.net', 'zscalerthree.net',
                                              'zscloud.net'], help='Provide cloud name', dest='cloud', required=True)
    parser_b.add_argument('--vip_type', choices=['gre_vip', 'vpn_hostname', 'proxy_hostname'], help='baz help',
                          dest='vip_type', required=True)
    parser_b.add_argument('--location', required=True,
                          help='Provide location of egress sites - city,state,country. Ex. Los Angeles, California, United States')

    parser_d = subparsers.add_parser('dc_lookup_csv',
                                     help='This feature will provide 2 closest Zscaler datacenters for a list of locations in CSV')
    parser_d.add_argument('--cloud', required=True,
                          choices=['zscaler.net', 'zscalerone.net', 'zscalertwo.net', 'zscalerthree.net',
                                   'zscloud.net'], help='Provide cloud name')
    parser_d.add_argument('--vip_type', required=True, choices=['gre_vip', 'vpn_hostname', 'proxy_hostname'],
                          help='baz help')
    parser_d.add_argument('--location_csv', required=True,
                          help='Path to CSV file which has egress sites. See example format here: ')

    options = parser.parse_args()

    # print(options)

    if options.option_picked == 'url_cat_lookup_csv':
        print("URL Lookup CSV")

    if options.option_picked == 'url_cat_lookup':
        print("Performing URL Lookup...")

    if options.option_picked == 'dc_lookup':
        print("Performing DC Lookup...")
        cli_dc_lookup(options.cloud, options.vip_type, options.location)

    if options.option_picked == 'dc_lookup_csv':
        print("DC Lookup CSV...")
        cli_dc_lookup_csv(options.cloud, options.vip_type, options.location_csv)


def cli_dc_lookup(cloud, vip_type, location):
    dc_results = zscaler.dc_lookup(cloud, location)
    print("Resolved Location:", dc_results[location]['resolved_location'])
    print("Primary DC:", dc_results[location]['primary_dc'][vip_type])
    print("Secondary DC:", dc_results[location]['secondary_dc'][vip_type])


def cli_dc_lookup_csv(cloud, vip_type, csvfile):
    dc_results = zscaler.dc_lookup_csv(cloud, csvfile)

    # print(dc_results)
    for item in dc_results:
        for location in item:
            print("Provided Location:", location)
            print("Resolved Location:", item[location]['resolved_location'])
            print("Primary DC: ", item[location]['primary_dc'][vip_type])
            print("Secondary DC: ", item[location]['secondary_dc'][vip_type])
            print()


if __name__ == "__main__":
    main()
