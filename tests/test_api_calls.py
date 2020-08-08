import json
from collections import Counter
from unittest import mock

import icu_ea_api

from payments import NetPaymentLoader


def _test_payments_data():
    with open('test_payments_data.json', 'r') as f:
        return json.loads(f.read())
    
def _test_products():
    return [{"Name": 'Net Booking', "ID": 32468}] 


@mock.patch( 'icu_ea_api.ICUEActivitiesAPI')
def test_load_payments_by_year(mock_api):
    mock_api.list_online_sales.return_value = _test_payments_data()
    mock_api.list_products.return_value = _test_products()
    payment_loader = NetPaymentLoader(mock_api, ['Net Booking'])
    counter = payment_loader.get_net_payments()
    assert counter == Counter({'sc2118': 5})

@mock.patch( 'icu_ea_api.ICUEActivitiesAPI')
def test_load_payments_no_payments(mock_api):
    mock_api.list_online_sales.return_value = [] 
    mock_api.list_products.return_value = _test_products()
    payment_loader = NetPaymentLoader(mock_api, ['Net Booking'])
    counter = payment_loader.get_net_payments()
    assert counter == Counter()

@mock.patch( 'icu_ea_api.ICUEActivitiesAPI')
def test_load_payments_no_products(mock_api):
    mock_api.list_online_sales.return_value = _test_payments_data()
    mock_api.list_products.return_value = [] 
    payment_loader = NetPaymentLoader(mock_api, ['Net Booking'])
    counter = payment_loader.get_net_payments()
    assert counter == Counter()

@mock.patch( 'icu_ea_api.ICUEActivitiesAPI')
def test_load_payments_no_payments_no_products(mock_api):
    mock_api.list_online_sales.return_value = [] 
    mock_api.list_products.return_value = [] 
    payment_loader = NetPaymentLoader(mock_api, ['Net Booking'])
    counter = payment_loader.get_net_payments()
    assert counter == Counter()
