# quant-engine
boiler-plate code of a working quant engine, built with chatGPT o3

How it works:

| Layer                | Purpose                                                                              | Where to extend next                                                                               |
| -------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| **DataProvider**     | Thin wrapper around any data source (Yahoo, CCXT, CSV, Postgres, your own UCP feed). | • Add a `CCXTDataProvider` for live crypto <br> • Cache locally with DuckDB for speed              |
| **Strategy**         | Turns raw prices into *trade signals* (+1/–1).  Demo shows a 50/200 SMA cross.       | • Port your Uniswap TWAP logic <br> • Add factor models, reinforcement agents, ML pipelines        |
| **Portfolio / Risk** | Tracks cash, positions, simple P\&L.                                                 | • Position sizing, stop-loss, Kelly sizing <br> • Multi-asset bookkeeping, Value-at-Risk           |
| **Backtester**       | Orchestrates data → strategy → portfolio to spit out an equity curve.                | • Vectorised backtests (e.g. `vectorbt`) <br> • Walk-forward CV, parameter sweeps, slippage models |
