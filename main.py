from subprocess import check_output, run, CalledProcessError,STDOUT
from re import findall,match
from pandas import DataFrame
from tabulate import tabulate

# Read the sni.txt file and split it into a list of domain names
with open("sni.txt", "r") as my_file:
    data = my_file.read()
    sni_list = data.split("\n")

# Remove any empty strings from the sni_list
sni_list = list(filter(None, sni_list))

# Test all the domains in sni.txt file and put the results in a list called result
result = []
for i in sni_list:
    try:
        x = check_output(f"./tlsping {i}:443", shell=True,text=True,stderr=STDOUT)
        result.append(x)
        # print("ok", x)
    except CalledProcessError as e:
        result.append(e.output)
        # print("err", e.output)
        pass

# Extract all the avg tlsping values from the domains
avg_value_list = []
for j in result:
    if "error" in j:
        avg_value_list.append(findall(r":([^:]+)$", j)[0])
        continue
    # Use regular expressions to extract the "avg" value
    avg_value = findall(r"avg/.*?ms.*?(\d+\.?\d*)ms", j )[0]
    avg_value_list.append(avg_value)

# Create a dictionary with the domain names as keys and the avg values as values
domain_ping_dict = {sni_list[i]: (float(avg_value_list[i]) if match(r'^[\d\.]+$',avg_value_list[i]) else avg_value_list[i]) for i in range(len(sni_list))}

# Sort the dictionary by the values in ascending order, putting numbers first then strings
def sort_key(item):
    key, value = item
    # If value is a number (int or float), return tuple (0, value) to sort numbers first
    if isinstance(value, (int, float)):
        return (0, value)
    # If value is a string, return tuple (1, value) to put strings after numbers
    else:
        return (1, value)

sorted_dict = dict(sorted(domain_ping_dict.items(), key=sort_key))

# Convert the sorted dictionary to a pandas DataFrame and print it using tabulate
df = DataFrame(sorted_dict.items(), columns=['domains', 'pings(ms)'])
# run('clear')
print(tabulate(df, headers='keys', tablefmt='psql'))
