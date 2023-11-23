import vensebur.EODHDdata


df = vensebur.EODHDdata.data.download(ticker="TSLA",
                                      start="2023-10-10", end="2023-10-12")

print(df)
