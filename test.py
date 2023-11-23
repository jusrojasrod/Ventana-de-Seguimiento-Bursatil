import vensebur.EODHDdata.data as data


df = data.download(ticker="TSLA",
                   start="2023-10-10", end="2023-10-12")

print(df)
