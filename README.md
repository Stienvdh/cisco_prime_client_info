# Installation

1. Clone this repository

```
$ git clone https://github.com/Stienvdh/cisco_prime_client_info
$ cd cisco_prime_client_info
```

2. Fill in the `.env` file

```
PRIME_HOST=<your-prime-host>
PRIME_USERNAME=<your-prime-username>
PRIME_PASSWORD=<your-prime-password>
```

3. Install all requirements

```
$ pip3 install -r requirements.txt
```

4. Set up your `input.csv` file in the root of your local repository. (Note: Use `File > Save As` to convert a Excel file to a CSV file)

5. Run the script

```
$ python3 main.py
```

6. Find your output generated in `output.csv`.