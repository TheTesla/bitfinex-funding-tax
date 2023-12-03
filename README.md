# Calculate bitfinex funding rewards in EUR for tax


Prepare environment and install dependencies:

```bash
python3 -m venv my_venv
source my_venv/bin/activate
pip3 install datetime bitfinex-api-py requests
```

You have to setup your alphavantage apikey in ``apikey.py`` and your bitfinex api credentials by calling: 

```bash
export BFX_KEY=yourkey 
export BFX_SECRET=yoursecret
```

then call:

```bash
python3 getfunding.py
```

This program is currently a dirty mess. Change your parameters in source code.

# Author

Stefan Helmert

