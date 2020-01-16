"""
Tests for net payment tracker
"""
import os
from datetime import date

import pandas as pd

from payments import load_payments, PaymentEntry, NetPlayer, NetList, \
    check_payments, load_cid_map, load_netlists


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def test_net_payment_product_loader():
    test_file = os.path.join(TEST_DIR, 'member_nets_test.csv')
    net_payment = load_payments(test_file)
    assert net_payment == {'01336056': 2, '01337238': 1, '01502382': 2}

def test_load_cid_map():
    test_file = os.path.join(TEST_DIR, 'members_test.csv')
    actual = load_cid_map(test_file)
    expected = pd.DataFrame([
        ['01336056', 'Name1 Surname1'],
        ['01337238', 'Name2 Surname2'],
        ['01502382', 'Name3 Surname3']],
        columns=['cid', 'name'])
    assert actual.equals(expected)

def test_netlist_loader():
    test_file = os.path.join(TEST_DIR, 'netlist_test.csv')
    cin_map = pd.DataFrame([
        ['01336056', 'Name1 Surname1'],
        ['01337238', 'Name2 Surname2'],
        ['01502382', 'Name3 Surname3']],
        columns=['cid', 'name'])
    netlist1 = NetList([NetPlayer('01336056', False),
                        NetPlayer('01337238', False),
                        NetPlayer('01502382', False)],
                       date=date(2019, 10, 8)) 
    netlist2 = NetList([NetPlayer('01337238', False),
                        NetPlayer('01502382', False),
                        NetPlayer('01336056', False)],
                       date=date(2019, 10, 9)) 
    expected = [netlist1, netlist2]
    actual = load_netlists(test_file, cin_map)
    assert actual == expected

def test_netlist_loader_with_excess_spaces():
    test_file = os.path.join(TEST_DIR, 'netlist_test_with_spaces.csv')
    cin_map = pd.DataFrame([
        ['01336056', 'Name1 Surname1'],
        ['01337238', 'Name2 Surname2'],
        ['01502382', 'Name3 Surname3']],
        columns=['cid', 'name'])
    netlist1 = NetList([NetPlayer('01336056', False),
                        NetPlayer('01337238', False),
                        NetPlayer('01502382', False)],
                       date=date(2019, 10, 8)) 
    netlist2 = NetList([NetPlayer('01337238', False),
                        NetPlayer('01502382', False),
                        NetPlayer('01336056', False)],
                       date=date(2019, 10, 9)) 
    expected = [netlist1, netlist2]
    actual = load_netlists(test_file, cin_map)
    assert actual == expected

def test_netlist_loader_with_netplayer_name_not_found():
    test_file = os.path.join(TEST_DIR, 'netlist_test_incorrect_name.csv')
    cin_map = pd.DataFrame([
        ['01336056', 'Name1 Surname1'],
        ['01337238', 'Name2 Surname2'],
        ['01502382', 'Name3 Surname3']],
        columns=['cid', 'name'])
    netlist1 = NetList([NetPlayer('Name4 Surname1', False),
                        NetPlayer('01337238', False),
                        NetPlayer('01502382', False)],
                       date=date(2019, 10, 8)) 
    netlist2 = NetList([NetPlayer('01337238', False),
                        NetPlayer('01502382', False),
                        NetPlayer('01336056', False)],
                       date=date(2019, 10, 9)) 
    expected = [netlist1, netlist2]
    actual = load_netlists(test_file, cin_map)
    assert actual == expected

def do_not_test_check_free_net():
    netlist = NetList([NetPlayer('01336056', False),
                       NetPlayer('01337238', False),
                       NetPlayer('01502382', False)],
                      date(2019, 10, 5))
    actual = check_free_net(netlist, 'freenet_test.txt') 


def test_net_payment_checker_for_one_day():
    payments = {'01336056': 1, '01337238': 1, '01502382': 1}
    netlist1 = NetList([NetPlayer('01336056', False),
                        NetPlayer('01337238', False),
                        NetPlayer('01502382', False)],
                       date(2019, 10, 5))
    netlists = [netlist1]
    actual = check_payments(netlists, payments)

    netlists[0].players[0].paid = True 
    netlists[0].players[1].paid = True
    netlists[0].players[2].paid = True

    assert actual == netlists

def test_net_payment_checker_over_multiple_days():
    payments = {'133656': 1, '1337238': 1, '1502382': 1}
    netlist1 = NetList([NetPlayer('133656', False),
                        NetPlayer('1502382', False)],
                       date(2019, 10, 5))
    netlist2 = NetList([NetPlayer('1337238', False)],
                       date(2019, 10, 5))
    netlists = [netlist1, netlist2]
    actual = check_payments(netlists, payments)

    netlists[0].players[0].paid = True
    netlists[0].players[1].paid = True
    netlists[1].players[0].paid = True

    assert actual == netlists

def test_net_payment_checker_for_unpaid_nets_on_single_date():
    payments = {'133656': 2, '1337238': 1, '1502382': 1}
    netlist1 = NetList([NetPlayer('133656', False),
                        NetPlayer('1502382', False)],
                       date(2019, 10, 5))
    netlist2 = NetList([NetPlayer('1337238', False)],
                       date(2019, 10, 5))
    netlists = [netlist1, netlist2]
    actual = check_payments(netlists, payments)

    netlists[0].players[0].paid = True
    netlists[0].players[1].paid = True
    netlists[1].players[0].paid = True

    assert actual == netlists
    
def test_net_payment_checker_for_multiple_paid_nets_on_multiple_dates():
    payments = {'133656': 2, '1337238': 1, '1502382': 1}
    netlist1 = NetList([NetPlayer('133656', False),
                        NetPlayer('1502382', False)],
                       date(2019, 10, 5))
    netlist2 = NetList([NetPlayer('1337238', False), 
                        NetPlayer('133656', False)],
                       date(2019, 10, 5))
    netlists = [netlist1, netlist2]
    actual = check_payments(netlists, payments)

    netlists[0].players[0].paid = True
    netlists[0].players[1].paid = True
    netlists[1].players[0].paid = True
    netlists[1].players[1].paid = True

    assert actual == netlists

def test_net_payment_checker_for_unpaid_nets_on_multiple_dates():
    payments = {'133656': 1, '1337238': 1, '1502382': 1}
    netlist1 = NetList([NetPlayer('133656', False),
                        NetPlayer('1502382', False)],
                       date(2019, 10, 5))
    netlist2 = NetList([NetPlayer('1337238', False), 
                        NetPlayer('133656', False)],
                       date(2019, 10, 5))
    netlists = [netlist1, netlist2]
    actual = check_payments(netlists, payments)

    netlists[0].players[0].paid = True
    netlists[0].players[1].paid = True
    netlists[1].players[0].paid = True
    netlists[1].players[1].paid = False

    assert actual == netlists
