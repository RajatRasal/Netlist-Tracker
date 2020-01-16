"""
Rendering the net payments tracker
"""
from collections import Counter, defaultdict
from typing import Final

import pandas as pd
from flask import Flask, jsonify, render_template

from payments import check_payments, load_payments, load_cid_map, load_netlists, \
        load_free_nets, NetList

app: Final = Flask(__name__)


@app.route('/netlist', methods=['GET'])
def get_netlist():
    # Member + non-member net products
    payment_mem = load_payments('./Purchase_Group_Report 32468.csv')
    payment_non_mem = load_payments('./Purchase_Group_Report 32541.csv')
    payments = dict(Counter(payment_mem) + Counter(payment_non_mem))
    # Membership net products
    cid_map = load_cid_map('./Purchase_Group_Report 31651.csv')
    # Allocated Free Nets
    free_nets = load_free_nets('./freenet.csv')
    # Netlists
    netlists = load_netlists('./netlist.csv', cid_map)

    print(payments.get('01734392', 'NOT FOUND'))
    print(cid_map.loc[cid_map['name'] == 'Thomas Hinde', :])

    updated_netlists = check_payments(netlists, payments)

    # Replace the cid with the actual name
    for netlist in updated_netlists:
        for i in range(len(netlist.players)):
            cid = netlist.players[i].cid
            name = cid_map.loc[cid_map.cid == cid, 'name'].values
            name = name[0] if name else ''

            # Case when a name is not found anywhere in the records.
            if not name and not netlist.players[i].paid:
                # TODO: Remove this hack!
                # print('HERE:', free_nets.get(cid, None), cid)
                if free_nets.get(cid, None):
                    netlist.players[i].paid = True
                    free_nets[cid] -= 1
                else:
                    netlist.players[i].paid = None
                continue

            if not netlist.players[i].paid:
                if free_nets.get(name, None):
                    netlist.players[i].paid = True
                    free_nets[name] -= 1
            netlist.players[i].cid = name

    # Descending order of dates
    updated_netlists.reverse()

    unpaid = defaultdict(int)
    for netlist in updated_netlists:
        for player in netlist.players:
            if not player.paid:
                unpaid[player.cid] += 1

    for pair in sorted(unpaid.items(), key=lambda kv: kv[1]):
        print(pair)

    return render_template('netlist.html', netlists=updated_netlists)


if __name__ == '__main__':
    app.run(debug=True)
