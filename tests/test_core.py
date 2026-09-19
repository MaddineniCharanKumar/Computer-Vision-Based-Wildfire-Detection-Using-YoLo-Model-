import pytest
from fireguard.risk import calculate_risk
from fireguard.domain import area_proxy,growth_rate

def test_risk_is_bounded(): assert 0 <= calculate_risk({'visual':100})['score'] <= 100
def test_area_proxy_is_not_physical_area(): assert area_proxy((0,0,.5,.2)) == .1
def test_growth(): assert growth_rate(10,15)==50
