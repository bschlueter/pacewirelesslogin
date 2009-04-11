#!/usr/bin/env python

try:
    import pycurl
except ImportError:
    print "Install pycurl already, won't you?"
    raise
import sys,re,os
from StringIO import StringIO
import getopt

def pwn_login(name,password, verbose):
    login_url='https://pacewireless.pace.edu/login.pl'
    crl = pycurl.Curl()
    buffer = StringIO()
    login_form_data = '_FORM_SUBMIT=1&which_form=reg&destination=&source=&bs_name='+name+'&bs_password='+password
    crl.setopt(pycurl.POSTFIELDS, login_form_data)
    crl.setopt(pycurl.URL, login_url)
    crl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    crl.perform()
    if verbose:
        print buffer.getvalue()
    #Checking condition
    logout_regex = re.compile('action=logout;r=\w*')
    if logout_regex.search(buffer.getvalue()):
        print "Successful log-in."
        return 1
    else:
        logged_in_regex = re.compile('You are already logged in')
        if logged_in_regex.search(buffer.getvalue()):
            print "You're already logged in."
            return 2
        else:
            invalid_login_regex = re.compile('You have an error: Invalid name or password')
            if invalid_login_regex.search(buffer.getvalue()):
                print "Invalid credentials. You will be reported to the authorities."
                return 3
            else:
                print "Login Failed! Unknown error."
                return 0
    crl.close()

def pwn_logout(verbose):
    login_url='https://pacewireless.pace.edu/login.pl?action=logout;r=PJQlK2A3708'
    buffer = StringIO()
    crl = pycurl.Curl()
    crl.setopt(pycurl.URL, login_url)
    crl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    crl.perform()
    if verbose:
        print buffer.getvalue()
    try:
        logout_regex = re.compile('You have successfully logged out.')
        if logout_regex.search(buffer.getvalue()):
            print "Successful logout."
    except IndexError:
            try:
                invalid_login_regex = re.compile('This link is not valid for your current session.')
                alt_invalid_regex = re.compile('404 - File Not Found')
                if invalid_login_regex.search(buffer.getvalue()) or alt_invalid_regex.search(buffer.getvalue()):
                    print "Login Failed! The program was likely corrupted."
            except IndexError:
                    print "Login Failed! Unknown error."
    crl.close()

def main():
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vlu:p:', ['logout','username=','password='])
    except getopt.error, msg:
        print 'python PaceWirelessLogin [-v] [-l| -u username -p password] [--logout| --username=username --password=password]'
        sys.exit(2)
    name,password = '',''
    # Process options
    verbose = '-v' in dict(opts)
    if '--logout' in dict(opts) or '-l' in dict(opts):
        pwn_logout(verbose)
    else:
        for option, arg in opts:
            if option == '--username' or option == '-u':
                name = arg
            elif option == '--password' or option == '-p':
                password = arg
        while not name:
            name = raw_input('Please enter Pace username: ')
        while not password:
            password = raw_input('Please enter Pace password: ')
        pwn_login(name, password, verbose)

if __name__=='__main__':
    main()