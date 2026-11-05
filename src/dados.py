GRANDEZAS = ["PM2.5", "PM10", "CO2", "temperatura", "umidade"]

# (id, descrição, cidade, uf, latitude, longitude) - dados ilustrativos
_LOCAIS = [
    ("S001", "Sensor ambiental do centro", "Chapecó", "SC", -27.1009, -52.6157),
    ("S002", "Sensor ambiental da zona norte", "Chapecó", "SC", -27.0748, -52.6240),
    ("S003", "Sensor ambiental do centro", "Xanxerê", "SC", -26.8770, -52.4040),
    ("S004", "Sensor ambiental da zona sul", "Xanxerê", "SC", -26.8900, -52.4100),
    ("S005", "Sensor ambiental do centro", "Concórdia", "SC", -27.2342, -52.0278),
    ("S006", "Sensor ambiental da zona leste", "Concórdia", "SC", -27.2200, -52.0100),
]

SENSORES = [
    {
        "_id": id_,
        "modelo": "AirMonitor-200",
        "descricao": desc,
        "localizacao": {"cidade": cidade, "uf": uf, "latitude": lat, "longitude": lon},
        "ativo": True,
        "grandezas": GRANDEZAS,
    }
    for id_, desc, cidade, uf, lat, lon in _LOCAIS
]
