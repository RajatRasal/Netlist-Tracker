"""
Net payment tracker
"""
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, TypeVar, Any, DefaultDict, TypedDict, Sequence

import pandas as pd
import numpy as np

PaymentMap = Dict[str, int]
# CinMap = TypeVar('CinMap')
class CinMap(TypedDict):
    cid: Sequence[str]
    name: Sequence[str]


@dataclass
class PaymentEntry:
    date: date
    cid: str
    quantity: int


@dataclass
class NetPlayer:
    cid: str
    paid: bool


@dataclass(frozen=True)
class NetList:
    players: List[NetPlayer]
    date: date


def load_payments(data_file: str, freenet_file: Optional[str] = None) -> PaymentMap:
    csv = pd.read_csv(data_file, dtype={'CID/Card Number': object})
    payment_records = csv[['CID/Card Number', 'Quantity']]
    payments: DefaultDict[str, int] = defaultdict(int)

    for cid, quantity in payment_records.values:
        payments[str(cid)] += quantity

    # TODO: Add 1 to every free netter

    return dict(payments)

def load_cid_map(data_file: str, freenet_file: Optional[str] = None) -> CinMap:
    csv = pd.read_csv(data_file, dtype={'CID/Card Number': object})
    csv = csv.rename(columns={'CID/Card Number': 'cid'})
    cin_map = csv[['cid', 'First Name', 'Surname']]
    cin_map['name'] = cin_map[['First Name', 'Surname']] \
            .apply(lambda x: ' '.join(x), axis=1)
    # TODO: Add kv pair for every free net person free netter
    return cin_map[['cid', 'name']]

def __fix_input_names(name: str) -> str:
    if pd.isna(name):
        return None

    # TODO: Remove hack in regex for test cases
    # +[0-9]? is needed because test cases have names such as 'Name1 Surname2'
    # The regex group at the end is for people with double barrelled surnames.
    res = re.search('[A-Za-z]+[0-9]? *[A-Za-z]+[0-9]?( *[A-Za-z]+[0-9]?)?', name)

    if res:
        # if there are any excess spaces between firstname and surname, we
        # remove them before returning
        return re.sub(' +', ' ', res[0])

    return None

def load_netlists(data_file: str, cid_map: CinMap) -> List[NetList]:
    """
    Assuming that the cid_map has all the cids that are needed.
    """
    try:
        csv = pd.read_csv(data_file)
    except UnicodeDecodeError:
        csv = pd.read_csv(data_file, encoding='latin')

    netlists = []
    for _date, _netplayers in csv.items():
        _date_obj = datetime.strptime(_date, '%d/%m/%Y').date()
        netplayers = _netplayers.apply(__fix_input_names)
        netplayers.dropna(inplace=True)
        joined = pd.merge(netplayers.to_frame(), cid_map, how='left',
                          left_on=_date, right_on='name')

        netplayers = []
        for row in joined.itertuples():
            if pd.isnull(row.cid):
                netplayers.append(NetPlayer(row._1, False))
            else:
                netplayers.append(NetPlayer(row.cid, False))

        netlist = NetList(netplayers, _date_obj)
        netlists.append(netlist)

    return netlists

def load_free_nets(data_file: str) -> Dict[str, int]:
    free_nets = pd.read_csv(data_file)
    free_nets_names = free_nets.values.flatten().tolist()
    free_nets_names = list(map(__fix_input_names, free_nets_names))
    free_nets_counter = Counter(free_nets_names)
    return dict(free_nets_counter)

def check_payments(netlists: List[NetList], payments: PaymentMap) -> List[NetList]:
    """
    Given all the netlists, mark each entry as paid or not paid.
    """
    updated_netlists = []
    for netlist in netlists:
        players = []
        for player in netlist.players:
            if payments.get(player.cid, None):
                paid_player = NetPlayer(cid=player.cid, paid=True)
                players.append(paid_player)
                payments[player.cid] -= 1
            else:
                players.append(player)
        updated_netlist = NetList(players=players, date=netlist.date)
        updated_netlists.append(updated_netlist)
    return updated_netlists

if __name__ == '__main__':
    payments = load_payments('./tests/member_nets_test.csv')
    cid_map = load_cid_map('./tests/members_test.csv')
    netlists = load_netlists('./tests/netlist_test_incorrect_name.csv', cid_map)
