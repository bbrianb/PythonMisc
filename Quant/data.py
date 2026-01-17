from no_authentication_endpoints import no_authentication_endpoints

o: no_authentication_endpoints = no_authentication_endpoints()

data = o.candle_sticks_in_pandas('KXCBDECISIONCANADA', 'KXCBDECISIONCANADA-25OCT-C25',60)

print(data)