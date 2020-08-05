#!/usr/bin/env python

import sys
import requests
import argparse
import json

class Message():
    summary = ""
    description = ""

    def __init__(self, summary, desscription):
        self.summary = summary
        self.description = desscription

    def __str__(self):
        return self.description


class NagiosResponse():
    unknown_messages = []
    critical_messages = []
    warning_messages = []
    ok_messages = []
    
    def set_ok(self, summary, description):
        self.ok_messages.append(Message(summary, description))

    def set_warning(self, summary, description):
        self.warning_messages.append(Message(summary, description))

    def set_critical(self, summary, description):
        self.critical_messages.append(Message(summary, description))

    def set_unknown(self, summary, description):
        self.unknown_messages.append(Message(summary, description))

    def get_result(self):
        result = ""
        exit_code = -1

        # check for unknown errors
        if len(self.unknown_messages) > 0:
            # format all the unknown error into a string
            unk_err = ".".join([str(x) for x in self.unknown_messages])
            result = "UNKNOWN - {0}.\n{1}.".format(self.unknown_messages[0].summary, unk_err)
            exit_code = 3
            
        # check for critical errors
        if len(self.critical_messages) > 0:
            # check if there were any unknown errors previously
            # in that case just append the critical messages but don't change status and exit code
            if result != "":
                crit_err = ".".join([str(x) for x in self.critical_messages])
                result = "{0}{1}.".format(result, crit_err)
            else:
                crit_err = ".".join([str(x) for x in self.critical_messages])
                result = "CRITICAL - {0}.\n{1}.".format(self.critical_messages[0].summary, crit_err)
                exit_code = 2
        
        # check for warning errors
        if len(self.warning_messages) > 0:
            # check if there were any unknown or critical errors previously
            # in that case just append the warning messages but don't change status and exit code
            if result != "":
                warn_err = ".".join([str(x) for x in self.warning_messages])
                result = "{0}{1}.".format(result, warn_err)
            else:
                warn_err = ".".join([str(x) for x in self.warning_messages])
                result = "WARNING - {0}.\n{1}.".format(self.warning_messages[0].summary, warn_err)
                exit_code = 1
        
        # if there were no error, set the status to ok
        if result == "":
            result = "OK - Success."
            exit_code = 0

        return result, exit_code
    
def check_b2safe(args,sf_warn,sf_crit,mf_warn,mf_crit):

    nagios_response = NagiosResponse()
    try:
        
        b2safe_response = requests.get(url=args.url, timeout=args.timeout, verify=args.verify)
        
        if b2safe_response.status_code != 200:
            desc = 'Service returned an unexpected response'
            err = 'Service returned a status code of {0} with the response, {1}'.format(b2safe_response.status_code, b2safe_response.text)
            nagios_response.set_critical(desc, err)
            return nagios_response

        if "sysinfo" not in b2safe_response.json():
            desc = 'sysinfo field was not found in the response'
            err = b2safe_response.text
            nagios_response.set_critical(desc, err)    
            return nagios_response

        if "Mem-free" not in b2safe_response.json()["sysinfo"]:
            desc = 'Mem-free field was not found in the response'
            err = b2safe_response.text
            nagios_response.set_critical(desc, err)    
            return nagios_response

        if "Swap-free" not in b2safe_response.json()["sysinfo"]:
            desc = 'Swap-free field was not found in the response'
            err = b2safe_response.text
            nagios_response.set_critical(desc, err)    
            return nagios_response
        
        mem_free_value = int(b2safe_response.json()["sysinfo"]["Mem-free"])

        if mem_free_value > mf_crit and mem_free_value > mf_crit:
            desc = 'Mem-free is critical'
            err = 'Mem-free value({0}) was higher than the accepted critical threshold({1})'.format(mem_free_value, mf_crit)
            nagios_response.set_critical(desc, err)    
        
        if mem_free_value > mf_warn and mem_free_value < mf_crit:
            desc = 'Mem-free is warning' 
            err = 'Mem-free value({0}) was higher than the accepted warning threshold({1})'.format(mem_free_value, mf_warn)
            nagios_response.set_warning(desc, err)    

        swap_free_value = int(b2safe_response.json()["sysinfo"]["Swap-free"])

        if swap_free_value > sf_warn and swap_free_value > sf_crit:
            desc = 'Swap-free is critical'
            err = 'Swap-free value({0}) was higher than the accepted critical threshold({1})'.format(swap_free_value, sf_crit)
            nagios_response.set_critical(desc, err)    

        if swap_free_value > mf_warn and swap_free_value < mf_crit:
            desc = 'Swap-free is warning'
            err = 'Swap-free value({0}) was higher than the accepted warning threshold({1})'.format(swap_free_value, sf_warn)
            nagios_response.set_warning(desc, err)    
        
        return nagios_response

    except requests.exceptions.SSLError as ssle:
        desc = 'SSL Error'
        err = str(ssle)
        nagios_response.set_critical(desc, err)
        return nagios_response

    except requests.exceptions.ConnectionError as ce:
        desc = 'Connection Error'
        err =  str(ce)
        nagios_response.set_critical(desc, err)
        return nagios_response

def parse_thresholds(th_name, th_string):
    warn_crit_values = th_string.split(';')

    if len(warn_crit_values) != 2:
        raise Exception('Bad format for {0} value.Format should be "{{warning-value}};{{critical-value}}", e.g. "400;500"'.format(th_name))
    
    try:
        w_value = int(warn_crit_values[0])
    except ValueError as ve:
        raise Exception('Warning threshold should be a valid integer')

    try:
        c_value = int(warn_crit_values[1])
    except ValueError as ve:
        raise Exception('Critical threshold should be a valid integer')
    
    return w_value, c_value


def print_help(errmsg):
        print('UNKNOWN - Invalid arguments.\n{0}.'.format(errmsg))
        sys.exit(3)


def main():

    parser = argparse.ArgumentParser(description='B2SAFE probe for accounting data.')
    parser.add_argument("--url", "-u", dest="url", help='The url where the json report can be found', required=True)
    parser.add_argument("--timeout", "-t", type=int, default=30, dest="timeout", help="Timeout in seconds", required=True)
    parser.add_argument("--swap-free", "-sf", type=str, dest="sf", help="Swap-free threshold string", required=True)
    parser.add_argument("--mem-free", "-mf", type=str, dest="mf", help="Mem-free threshold string", required=True)
    parser.add_argument("-verify", dest="verify", help="SSL verification for requests", action="store_true")
    parser.error = print_help
    arguments = parser.parse_args()


    try:
        sf_warn, sf_Crit = parse_thresholds("Swap-free", arguments.sf)

        mf_warn, mf_crit = parse_thresholds("Mem-free", arguments.mf)
    except Exception as e:
        print('UNKNOWN - Invalid arguments.\n{0}.'.format(str(e)))
        sys.exit(3)
    
    result, exit_code = check_b2safe(arguments, sf_warn, sf_Crit, mf_warn, mf_crit).get_result()
    print(result)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
