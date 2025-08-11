def generate_search_scheme(mode, params):
if mode == 'sector':
return "Sector scheme generated with params: " + str(params)
if mode == 'expanding_square':
return "Expanding square scheme generated with params: " + str(params)
return "Unknown scheme"