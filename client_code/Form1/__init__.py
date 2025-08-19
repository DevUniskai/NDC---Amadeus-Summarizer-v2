from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import re
from datetime import datetime
import sys

def diff_day(date1, date2):  
   # Check if either date is 'Unknown Date'
  if date1 == "Unknown Date" or date2 == "Unknown Date":
    return 0  # Return 0 if dates are unknown, as no difference can be calculated
    
  # Convert strings to date objects
  date_object1 = datetime.strptime(date1, "%d %b %Y")
  date_object2 = datetime.strptime(date2, "%d %b %Y")

  # Calculate the difference in days
  difference_in_days = (date_object2 - date_object1).days

  # Print the difference
  # print("Difference in days:", difference_in_days)
  return difference_in_days

def get_index_multiple(list_item, search_text):
  for text in search_text:
    idx = get_index(list_item, text)
    if idx != -1:
      return idx
  return -1

def convert_time24h(time_str):
  try:
    return datetime.strptime(time_str.strip(), "%I:%M%p").strftime("%H:%M")
  except ValueError:
    return ""
  
def calculate_days_with_time(dep_time, arr_time):
    days_diff = 0

    # Convert times for comparison
    dep_time_obj = datetime.strptime(dep_time, "%H:%M").time()
    arr_time_obj = datetime.strptime(arr_time, "%H:%M").time()

    # If arrival time is earlier than departure time, it's an overnight flight (+1 day)
    if arr_time_obj < dep_time_obj:
        days_diff += 1

    return days_diff
  
def parse_flight_schedule(input_text):
    lines = input_text.strip().split('\n')
    if "Layover" in input_text:
        # Use the first function if "layover" is detected
        return parse_penawaran_1(input_text)
    elif "Non-stop" in lines:
        # Use the second function if "no stop" is detected
        return parse_penawaran_tes(input_text)

def parse_penawaran(input_text):
  print("\n Result Penawaran\n\n")
  lines = input_text.strip().split('\n')
  # print(lines)
  place_index = [ [x, y] for x,y in enumerate(lines) if len(y) == 3]
  flight_class = [ i.split(":") for idx, i in enumerate(lines) if "RBD Code" in i]
  flight_code = [ [idx, i.split(" ")[1:3]] for idx, i in enumerate(lines) if "logo SQ" in i]
  # print(place_index)
  date_time = []
  output_text = ""
  for place in place_index:
    split_datetime = lines[place[0]+1].split(" ")
    # print(split_datetime)
    time = split_datetime[0]
    date = " ".join([split_datetime[1].replace("(",""), split_datetime[2], split_datetime[3][:4]])
    # date = " ".join([split_datetime[1].replace("(",""), split_datetime[2]])
    date_time.append([time, date])
  # print(date_time)

  length = len(place_index)
  # print("*Singapore Airlines*")
  output_text += "*By Singapore Airlines*\n"
  for i in range(0, length, 2):
    flight_code_str = " ".join(flight_code[int(i/2)][1])
    flight_class_str = str(flight_class[int(i/2)][1])
    output_text += str(date_time[i][1] + " | " + place_index[i][1] + "-" + place_index[i+1][1] + " | " + date_time[i][0] + "-" + date_time[i+1][0])
    output_text += " | " + flight_code_str + " " + flight_class_str
    print(date_time[i][1], end="")
    print(" | " + place_index[i][1] + "-" + place_index[i+1][1] + " ", end="")
    print("| " + date_time[i][0] + "-" + date_time[i+1][0], end="")
    days = diff_day(date_time[i][1], date_time[i+1][1])
    if (days > 0):
      output_text += str("(+ " +str(days)+")")
      print("(+ " +str(days)+")", end="")
    
    output_text += "\n"
    print("")
  
  return output_text

def parse_penawaran_1(input_text):
    lines = [line.strip() for line in input_text.splitlines() if line.strip()]
    flights = []
    i = 0
    first_departure_date = None
    
    while i < len(lines):
        flight = {}

        if len(lines) - i >= 11:
            flight['departure_date'] = lines[i]
            flight['arrival_date'] = lines[i+1]
            flight['departure_time'] = lines[i + 2]
            flight['arrival_time'] = lines[i + 3]
            flight['departure_airport_code'] = lines[i + 4]
            flight['arrival_airport_code'] = lines[i + 5]
            flight['flight_code'] = lines[i + 9]
              
            if "Layover" in lines[i-1]:
              layover = lines[i-1]         
              
            if "Layover" not in lines[i-1]:
              first_departure_date = flight['departure_date']
              second_departure_date = flight['arrival_date']

              # Use the new function to handle both date and time
              if diff_day(first_departure_date, second_departure_date) > 0:
                days_diff = diff_day(first_departure_date, second_departure_date)
              else:
                days_diff = calculate_days_with_time(flight['departure_time'], flight['arrival_time']) # flight['departure_date'], flight['arrival_date'], 

              # Append (+1) if flight arrives the next day
              flight['arrival_time'] += f"(+{days_diff})" if days_diff > 0 else ""

            flights.append(flight)
            
            if i+12 <= len(lines) and "layover" in lines[i+11].lower():
                i += 12
            else:
                i += 11
        else:
            break

    output = "*By Singapore Airlines*\n"
    for flight in flights:
        output += f"{flight['departure_date']} | {flight['departure_airport_code']}-{flight['arrival_airport_code']} | {flight['departure_time']}-{flight['arrival_time']} | {flight['flight_code']}\n"
    output += f"_{layover}_"
    return output
  
# format input paling baru (perflight) pake yg ini
def parse_penawaran_newFormat(input_text):
    lines = input_text.strip().split('\n')
  
    flight_details = []
    current_flight_group = {
        'departure_date': '',
        'departure_airports': [],
        'arrival_airports': [],
        'departure_times': [],
        'arrival_times': [],
        'flight_numbers': []
    }
    i = 0
  
    while i < len(lines):
        line = lines[i].strip()

        if re.match(r"\d{2} [A-Za-z]{3} \d{4}", line):  # Match date
            if current_flight_group['departure_date'] == '':
                current_flight_group['departure_date'] = line

        if re.match(r"\d{2}:\d{2}", line):  # Match time
            if len(current_flight_group['departure_times']) == 0:
                current_flight_group['departure_times'].append(line)
            elif len(current_flight_group['arrival_times']) == 0:
                current_flight_group['arrival_times'].append(line)

        if re.match(r"^[A-Z]{3}$", line):  # Match airport code
            if len(current_flight_group['departure_airports']) == 0:
                current_flight_group['departure_airports'].append(line)
            elif len(current_flight_group['arrival_airports']) == 0:
                current_flight_group['arrival_airports'].append(line)

        if re.match(r"SQ\d{2,4}", line) or re.match(r"SQ\d{3,4}", line):  # Match flight number
            current_flight_group['flight_numbers'].append(line)

        # Append flight group when dates and all details are filled
        if all(len(current_flight_group[key]) == 1 for key in ['departure_airports', 'arrival_airports', 'departure_times', 'arrival_times', 'flight_numbers']):
            flight_details.append(current_flight_group.copy())
            # Reset the group for the next set of flights
            current_flight_group = {
                'departure_date': '',
                'departure_airports': [],
                'arrival_airports': [],
                'departure_times': [],
                'arrival_times': [],
                'flight_numbers': []
            }

        i += 1

    # Format the output
    output = ["*By Singapore Airlines*"]
    for flight_group in flight_details:
        departure_airports = "-".join(flight_group['departure_airports'])
        arrival_airports = "-".join(flight_group['arrival_airports'])
        departure_times = "-".join(flight_group['departure_times'])
        arrival_times = "-".join(flight_group['arrival_times'])
        flight_numbers = "-".join(flight_group['flight_numbers'])
        output.append(f"{flight_group['departure_date']} | {departure_airports}-{arrival_airports} | {departure_times}-{arrival_times} | {flight_numbers}")
  
    return "\n".join(output)
  
# (inputnya copast pas udah pilih jadwal) format per leg dari flight yang sama beda baris - masih mau dicari tau salah dimana
def parse_penawaran_new(input_text):
    lines = input_text.strip().split('\n')
    
    flight_details = []
    current_flight_group = {
        'departure_date': '',
        'arrival_date': '',
        'departure_airports': [],
        'arrival_airports': [],
        'departure_times': [],
        'arrival_times': [],
        'flight_numbers': [],
        'cabin_classes': []
    }
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        # Detect flight number and cabin class (flexible cabin class)
        if re.match(r"SQ\d{2,4}", line) and ":" in next_line:
            flight_number = line.strip()  # Get the flight number
            cabin_class = next_line.split(':')[-1].strip()  # Get cabin class, regardless of the text before ":"
            current_flight_group['flight_numbers'].append(flight_number)
            current_flight_group['cabin_classes'].append(cabin_class)

        # Detect departure airport and time
        if re.match(r"[A-Z]{3} \d{2}:\d{2}", line):
            parts = line.split()
            current_flight_group['departure_airports'].append(parts[0])
            current_flight_group['departure_times'].append(parts[1])

        # Detect arrival airport and time after a stop or time block
        if re.match(r"[A-Z]{3}", line) and ("stop" in next_line or re.match(r"\d{2}:\d{2}", next_line)):
            current_flight_group['arrival_airports'].append(line)
            current_flight_group['arrival_times'].append(next_line)

        # Detect dates
        if re.match(r"\d{2} [A-Za-z]{3} \d{4}", line):
            if current_flight_group['departure_date'] == '':
                current_flight_group['departure_date'] = line  # Assign the first date as departure date
            else:
                current_flight_group['arrival_date'] = line  # Assign the second date as arrival date
        
        # Append flight group when dates and all details are filled
        if len(current_flight_group['departure_airports']) == len(current_flight_group['flight_numbers']) and current_flight_group['arrival_date'] != '':
            flight_details.append(current_flight_group.copy())
            # Reset the group for the next set of flights
            current_flight_group = {
                'departure_date': '',
                'arrival_date': '',
                'departure_airports': [],
                'arrival_airports': [],
                'departure_times': [],
                'arrival_times': [],
                'flight_numbers': [],
                'cabin_classes': []
            }

        i += 1

    # Format the output
    output = ["*By Singapore Airlines*"]
    for flight_group in flight_details:
        # For each flight group, divide into individual legs
        for j in range(len(flight_group['flight_numbers'])):
            departure_airport = flight_group['departure_airports'][j]
            arrival_airport = flight_group['arrival_airports'][j] if j < len(flight_group['arrival_airports']) else "Unknown"
            departure_time = flight_group['departure_times'][j]
            arrival_time = flight_group['arrival_times'][j] if j < len(flight_group['arrival_times']) else "Unknown"
            flight_number = flight_group['flight_numbers'][j]
            cabin_class = flight_group['cabin_classes'][j]
            departure_date = flight_group['departure_date'] if j == 0 else flight_group['arrival_date']

            output.append(f"{departure_date} | {departure_airport}-{arrival_airport} | {departure_time}-{arrival_time} | {flight_number} {cabin_class}")
    
    return "\n".join(output)

# (inputnya copast pas udah pilih jadwal) format satu baris untuk 1 flight - masih mau dicari tau salah dimana
def parse_penawaran_tes(input_text):
    lines = input_text.strip().split('\n')
    
    flight_details = []
    current_flight_group = {
        'departure_date': '',
        'arrival_date': '',
        'departure_airports': [],
        'arrival_airports': [],
        'departure_times': [],
        'arrival_times': [],
        'flight_numbers': [],
        'cabin_classes': []
    }
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        before_line = lines[i-1].strip()
        before_line1 = lines[i-6].strip()
      
        # Detect flight number and cabin class (flexible cabin class)
        if re.match(r"SQ\d{3,4}", line) and ":" in next_line:
            flight_number = line.strip()  # Get the flight number
            cabin_class = next_line.split(':')[-1].strip()  # Get cabin class, regardless of the text before ":"
            current_flight_group['flight_numbers'].append(flight_number)
            current_flight_group['cabin_classes'].append(cabin_class)

        # Detect departure airport and time
        if re.match(r"[A-Z]{3} \d{2}:\d{2}", line) and "Singapore Airlines" in before_line1:
            parts = line.split()
            current_flight_group['departure_airports'].append(parts[0])
            current_flight_group['departure_times'].append(parts[1])
            print(parts)

        if re.match(r"[A-Z]{3}", line) and "stop" in next_line:
            current_flight_group['departure_airports'].append(line)
          
        # Detect arrival airport (next airport code after "stop" or time block)
        if re.match(r"[A-Z]{3} \d{2}:\d{2}", line) and "stop" in before_line:
            parts = line.split()
            current_flight_group['arrival_airports'].append(parts[0])
            current_flight_group['arrival_times'].append(parts[1])
            print(parts)
        
        # Detect dates
        if re.match(r"\d{2} [A-Za-z]{3} \d{4}", line):
            if current_flight_group['departure_date'] == '':
                current_flight_group['departure_date'] = line  # Assign the first date as departure date
            else:
                current_flight_group['arrival_date'] = line  # Assign the second date as arrival date
        
        # Append flight group when dates and all details are filled
        if len(current_flight_group['departure_airports']) == len(current_flight_group['flight_numbers']) and current_flight_group['arrival_date'] != '':
            flight_details.append(current_flight_group.copy())
            # Reset the group for the next set of flights
            current_flight_group = {
                'departure_date': '',
                'arrival_date': '',
                'departure_airports': [],
                'arrival_airports': [],
                'departure_times': [],
                'arrival_times': [],
                'flight_numbers': [],
                'cabin_classes': []
            }

        i += 1

    # Format the output
    output = ["*By Singapore Airlines*"]
    for flight_group in flight_details:
        departure_airports = "-".join(flight_group['departure_airports'])
        arrival_airports = "-".join(flight_group['arrival_airports'])
        departure_times = "-".join(flight_group['departure_times'])
        arrival_times = "-".join(flight_group['arrival_times'])
        flight_numbers = " - ".join([f"{num} {cls}" for num, cls in zip(flight_group['flight_numbers'], flight_group['cabin_classes'])])
        output.append(f"{flight_group['departure_date']} - {flight_group['arrival_date']} | {departure_airports}-{arrival_airports} | {departure_times}-{arrival_times} | {flight_numbers}")
    
    return "\n".join(output) 

def get_index(list_item, search_text):
  for idx, item in enumerate(list_item):
    if search_text in item:
      return idx
  return -1

def is_konfirmasi(input_text):
  lines = input_text.strip().split(' ')

  if "Booking" in lines:
    return True
  return False

def is_konfirmasi_new(input_text):
  # lines = input_text.strip().split(' ')
  if "Traveller Information" in input_text:
    return True
  return False
  
def parse_konfirmasi(input_text):
  print("\n Result Konfirmasi\n\n")
  lines = input_text.strip().split('\n')
  pass_idx = get_index(lines, "Passenger Details") + 2

  output_text =""
  # print("*Singapore Airlines*")
  #Get Passenger Data
  for i in lines[pass_idx:]:
    if("Contact Details" in i):
      break
    split_data = i.split("\t")
    no_urut = split_data[0]
    pass_data = no_urut + ". " + split_data[1]
    if(no_urut.isnumeric()):
      output_text += str(pass_data) + "\n"
      print(pass_data)

  print("")
  output_text += "\n"
  
  #Get Itin
  itin_idx = get_index(lines, "Itinerary Details") + 5
  order_idx = get_index(lines, "Order Details")
  pattern = r"\((.*?)\)"

  #Check Text if they copy until Order Detail
  check_text = lines[itin_idx:] if order_idx == -1 else lines[itin_idx:order_idx]
  # print(check_text)
  #Got Place
  place = re.findall(pattern, str(check_text))
  # print(place)
  length = len(place)
  length_check = len(check_text)
  start = 0
  datetime = []
  output_text +="*By Singapore Airlines*\n"
  for key, i in enumerate(check_text):
    if len(place) == start:
      break
    # print(i)
    if place[start] in i and place[start+1] in i:

      depart = i.split("\t")[1]
      arrival = i.split("\t")[3]

      depart_date = depart[:-6]
      depart_time = depart[-5:]

      arrival_date = arrival[:-6]
      arrival_time = arrival[-5:]

      flight_class = ""

      if key+4 <= length_check:
        if key+4 == length_check or len(check_text[key+4]) == 0:
          flight_class = check_text[key+3].split("\t")[-1][0]
        else:
          flight_class = check_text[key+4].split("\t")[0][0]
          
      flight_code = ""
      if(key == 0):
        flight_code = lines[itin_idx-2:][0]
      else:      
        flight_code = lines[itin_idx+key-2:][0]

      output_text += str(depart_date)
      print(depart_date, end="")
      output_text += str(" | " + place[start]+"-"+place[start+1]+" | ")
      print(" | " + place[start]+"-"+place[start+1]+" | ", end="")
      output_text += str(depart_time+"-"+arrival_time)
      print(depart_time+"-"+arrival_time, end="")

      #flight code and class
      output_text += " | " + str(flight_code) + " " + str(flight_class)
      print(" | " + str(flight_code) + " " + str(flight_class), end="")
      
      # print(i.split("\t"))
      days = diff_day(depart_date, arrival_date)
      if (days > 0):
        output_text += " (+ " +str(days)+")"
        print(" (+ " +str(days)+")", end="")
      start+=2
      output_text += "\n"
      print("")
  return output_text

def parse_konfirmasi_newPassengers(text):
    # Split the input by lines
    lines = text.strip().split('\n')
    
    # Find the index of the "Traveller Information" section
    traveller_info_index = lines.index("Traveller Information") + 2
    
    # Collect all passenger lines
    passenger_lines = []
    for i in range(traveller_info_index, len(lines)):
        # Stop when another section (like "Contact Details" or "Flight Information") begins
        if "Details" in lines[i] or "Flight Information" in lines[i]:
            break
        # Only append non-empty lines which are passenger details
        if lines[i].strip():
            passenger_lines.append(lines[i])

    # Now iterate through each passenger's details
    passengers_info = []
    for passenger_data in passenger_lines:
        passenger_details = passenger_data.split('\t')  # Assuming tab-separated fields
        
        # Extract title, first name (and other fields if needed)
        title = passenger_details[2].strip() if len(passenger_details[2].strip()) > 0 else ""
        first_name = passenger_details[0].strip() if len(passenger_details[0].strip()) > 0 else ""
        last_name = passenger_details[1].strip() if len(passenger_details[1].strip()) > 0 else ""
      
        # Add the formatted passenger details to the list
        passengers_info.append(f"{title} {first_name} {last_name}".strip())
    
    # Combine all passengers into one string
    passenger_output = ""
    for idx, passenger in enumerate(passengers_info, 1):
        passenger_output += f"{idx}. {passenger}\n"
        # print(idx, passenger)
    
    return passenger_output.strip()
  
def parse_konfirmasi_newFlightDetail(text):
    # Split the input by lines
    lines = text.strip().split('\n')
    
    # Find the index of the "Flight Information" section
    flight_info_index = lines.index("Flight Information") + 2
    
    # Extract the flight details (loop through lines following the Flight Information section)
    flight_details = []
    idx = flight_info_index
    
    while idx < len(lines):
        if "Traveller Information" in lines[idx]:
            break
        
        # Extract flight details from each line and ignore the "Details" lines
        if "Details" not in lines[idx]:  # Skip the "Details" line
            flight_data = lines[idx].split('\t')
            origin = flight_data[0].strip()
            destination = flight_data[1].strip()
            departure = flight_data[2].strip()
            arrival = flight_data[3].strip()
            flight_number = flight_data[4].strip()
            cabin_class = flight_data[5].strip()
            
            # Extract departure and arrival times
            departure_time = departure.split()[-1]
            arrival_time = arrival.split()[-1]
            departure_date = ' '.join(departure.split()[:3])  # Format the departure date

            # Combine the data in the desired format
            flight_details.append(f"{departure_date} | {origin}-{destination} | {departure_time}-{arrival_time} | {flight_number} {cabin_class}")
        idx += 1
    
    return "*By Singapore Airlines*\n" + "\n".join(flight_details)

def parse_konfirmasi_1(input_text):
  print("\n Result Konfirmasi\n\n")
  lines = [line.strip() for line in input_text.splitlines() if line.strip()]
  flightData = [line.replace("\t", " ") for line in lines if re.match(r'([A-Z]{3})\s+([A-Z]{3})\s+(\d{2} [A-Za-z]{3} \d{4} \d{2}:\d{2})\s+(\d{2} [A-Za-z]{3} \d{4} \d{2}:\d{2})\s+(SQ\d{3,4})\s+([A-Z])\s+([A-Z0-9]+)', line)]
  # passengerData = [line for line in lines if "ADT	SQ" in line]
  passengerData = [
    lines[i] for i in range(len(lines))
    if "View More" in lines[i] or (i + 2 < len(lines) and "View More" in lines[i + 2])
  ]

  flights = []
  passengers = []
  output_text = ""
  child_count = 0
  adult_count = 0
  infant_count = 0
  
  for data in flightData:
    flight = {}
    data = data.split()
    flight['departure_airport_code'] = data[0]
    flight['arrival_airport_code'] = data[1]
    flight['departure_date'] = data[2] + " " + data[3] + " " + data[4]
    flight['departure_time'] = data[5]
    flight['arrival_date'] = data[6] + " " + data[7] + " " + data[8]
    flight['arrival_time'] = data[9]
    flight['flight_code'] = data[10]
    flight['cabin_class'] = data[11]
    flights.append(flight)

  for data in passengerData:
    data = data.split("\t")

    # passengers.append(f"{data[2] if data[2] != '' else ''} {data[0]} {data[1]}")
    names = []
    krisflyer = ""
    passenger_type = ""

    for name in data:
      if "Traveller Information" in name:
        break
      if "Title" in name:
        break
      if re.match(r'^\d', name):
        break
      if name:
        names.append(name)
    
    if "CHD" in data:
      passenger_type = "CHD"
      child_count += 1
    elif "ADT" in data:
      passenger_type = "ADT"
      adult_count += 1
    elif "INF" in data:
      passenger_type = "INF"
      infant_count += 1
    
    if "SQ" in data:
      idx = data.index("SQ")
      if idx + 1 < len(data) and re.match(r'^\d+$', data[idx + 1]):
        krisflyer = data[idx + 1]

    full_name = " ".join(names)
    if krisflyer:
      full_name += f" #{krisflyer}"
    if passenger_type == "CHD":
      full_name += " *Child*"
    elif passenger_type == "INF":
      full_name += " *Infant*"
    if full_name:
      passengers.append(full_name)

  # if passenger cuma 1
  if len(passengers) == 1:
    output_text += f"{passengers[0]}\n"
  else:
    for i, passenger in enumerate(passengers, 1):
      output_text += f"{i}. {passenger}\n"
  
  output_text += "\n"
  output_text += "*By Singapore Airlines*\n"

  for flight in flights:
    output_text += f"{flight['departure_date']} | {flight['departure_airport_code']}-{flight['arrival_airport_code']} | {flight['departure_time']}-{flight['arrival_time']} | {flight['flight_code']} {flight['cabin_class']}\n"

  output_text += "\n"

  if adult_count:
    output_text += "*Adult : Rp*\n"
  if child_count:
    output_text += "*Child : Rp*\n"
  if infant_count:
    output_text += "*Infant : Rp*\n"

  output_text += "\n> *Ticketing Time Limit :*"
  
  return output_text

# Air Asia #
def is_penawaran(text):
  split_text = text.split("\n")
  print(split_text)
  if("Booking Details" in split_text[0]):
    return True
  return False

def handle_loc(text):
  split = text.split(" ")
  data=[]
  temp=""
  for key, item in enumerate(split):

    isLastItem = key == len(split)-1

    if(item == "-" or isLastItem):
      if isLastItem:
        temp += " " + item

      data.append(temp)
      temp = ""
      continue

    if(split[key-1] == "-"):
      continue

    if(len(temp)!=0):
      temp+= " "

    temp += item

  return str(data[0] + "-" + data[1])

def handle_time(text):
  split = text.split(" ")
  idx = split.index("-")
  start = split[idx-1][-5:]
  end = split[idx+1][:5]

  return str(start + "-" + end)

def parse_penawaran_air_asia(text):
  split_text = text.split("\n")
  print(split_text)

  output = "By Air Asia \n\n"
  depart_idx = split_text.index("Depart date")
  depart_date = split_text[depart_idx+1]
  depart_idx_end = split_text.index("Depart total")
  depart_list = split_text[depart_idx+2:depart_idx_end].copy()

  for i in range(0, len(depart_list), 2):
    depart_loc = depart_list[i]
    depart_time = handle_time(depart_list[i+1])
    output += str(depart_date + " | " + depart_loc + " | " + depart_time + "\n")

  return_idx = split_text.index("Return date") if "Return date" in split_text else None

  if(return_idx):
    return_total = split_text.index("Return total")
    return_list = split_text[return_idx+2:return_total].copy()
    return_date = split_text[return_idx+1]
    
    for i in range(0, len(return_list), 2):
      return_loc = return_list[i]
      return_time = handle_time(return_list[i+1])
      output += str(return_date + " | " + return_loc + " | " + return_time + "\n")

  return output

def parse_konfirmasi_air_asia(text):
  split = text.split("\n")
  output = ""
  schedule_output = "*By Air Asia*\n"
  idx = split.index("Flight summary")
  town = split[idx+1] + "-" + split[idx+3]
  idx = [index for index, item in enumerate(split) if "Departure:" in item][0]
  date = split[idx+2]
  idx = split.index("Booking status")
  time = split[idx+3]+"-"+split[idx+7]
  schedule_output += date + " | " + town + " | " + time + "\n"
  idx = split.index("Guest Name")
  length = len(split)
  
  
  for i in range(1, length-idx):
    if(len(split[idx+i]) == 0):
      continue
    name = split[idx+i].replace('(Adult)', '')
    output += name + "\n"
  
  output += "\n" + schedule_output
  return output

####AMADEUS#####
def is_confirmation_amd(text):
  split = text.split("\n")
  split = [i for i in split if "RTSVC" not in i]
  split = [i for i in split if len(i) != 0]
  if len(split[0]) == 6:
    return True
  else:
    return False

def clean_schedule_amd(text):
  flight_code = text[2] + text[3]
  subclass = text[4]
  
  raw_date = text[5]
  day = raw_date[:2]
  month = raw_date[2:]
  datetime = f"{day}{month}"
  
  city = text[6][2:]
  city = city[:3] + "-" + city[3:]
  
  dep_time = text[9][:2]+":"+text[9][2:]
  arr_time = text[10][:2]+":"+text[10][2:]

  # if diff_day(datetime, arr_time) > 0:
  #   days_diff = diff_day(datetime, arr_time)
  # else:
  days_diff = calculate_days_with_time(dep_time, arr_time)
  arr_time += f"(+{days_diff})" if days_diff > 0 else ""
  
  output = datetime + " " + city + " " + dep_time + "-" + arr_time + " " + flight_code + " " + subclass + "\n"
  return output

def remove_numeric_amd(text):
  # Remove leading number and dot (e.g., "1.")
  text = re.sub(r'^\d+\.', '', text)
  # Remove extra spaces
  text = text.strip()
  # Remove any leading/trailing periods
  text = text.strip('.')
  return text

def handle_name_amd(text):
  split = text.split("(")[0].strip()
  split = split.split("/")
  if len(split) < 2:
    return text.strip()

  last_name = split[0]
  front_name = split[1].split(" ")
  name = front_name[-1] + " " + ' '.join(front_name[0:len(front_name)-1]) + " " + last_name
  name = name.replace('FNU', '')
  name = re.sub(' +', ' ', name)
  return name

# Shared Airline Code Map
AIRLINE_MAP = {
    "SQ": "Singapore Airlines",
    "MH": "Malaysia Airlines",
    "QR": "Qatar Airways",
    "GA": "Garuda",
    "NH": "ANA",
    "JL": "Japan Airlines",
    "QF": "Qantas Airways",
    "3K": "Jetstar",
    "JQ": "Jetstar",
    "EK": "Emirates",
    "EY": "Etihad",
    "TK": "Turkish Airways",
    "CI": "China Airlines",
    "BR": "Eva Air",
    "CA": "Air China",
    "CZ": "China Southern Airlines",
    "MU": "China Eastern Airlines",
    "MF": "Xiamen Airlines",
    "KE": "Korean Airlines",
    "LH": "Lufthansa",
    "OZ": "Asiana Airlines",
    "VN": "Vietnam Airlines",
    "CX": "Cathay Pacific"
}

# Shared airline name resolver
def get_airline_name(code):
    return AIRLINE_MAP.get(code, "__ Airlines")

def handle_schedule_amd(text):
  split = text.split("\n")
  split = [i for i in split if "RTSVC" not in i]
  split = [i for i in split if len(i) != 0]
  flag = 1

  # Default airline name
  airline_name = "__ Airlines"

  # Try to detect airline code from the first valid line
  for line in split:
    parts = line.strip().split()
    if len(parts) > 1:
      airline_name = get_airline_name(parts[1])
      break

  output = f"*By {airline_name}*\n"

  for i in split:
    index = i.strip().split(" ")

    if len(index) < 11:  # not enough columns for a valid flight line
      continue
    
    # if code and number are gabung
    if len(index[2]) > 2:
      flight_code = index[2][:2] 
      flight_number = index[2][2:]  
      index = index[:2] + [flight_code, flight_number] + index[3:]
      # print(index)
      
    # kalau inputnya ada yang ga pakai '*'
    # print("before: " + index[6])
    if '*' not in index[6]:
      index[6] = index[6] + '*' + index[7]
      del index[7]
      # print("after: " + index[6])
      
    try:
      int(index[0])  # simple check to ensure valid flight line
      output += clean_schedule_amd(index)
    except:
      continue
  return output

def handle_confirmation_amd(text):
  split = text.split("\n")
  # print(split)
  split = [i for i in split if "RTSVC" not in i]
  split = [i for i in split if len(i) != 0]

  output = ""
  pnr = ""
  count=1
  flag=0
  passenger_names = []
  adult_count = 0
  child_count = 0
  airline_name = "__ Airlines"
  
  for idx, item in enumerate(split):
    if idx == 0:
      pnr = item
      # print("this is pnr: " + pnr + "\n")
    elif re.match(r'^\d+\.', item.strip()):
      # Passenger line detected
      lines = item.strip().split("\n")
      for i, line in enumerate(lines):
        if re.match(r'^\d+\.\w+\/\w+', line):
          # Split by passenger number markers like 1. 2. etc.
          name_segments = re.split(r'\s*(?=\d+\.)', line.strip())
          for segment in name_segments:
            segment = remove_numeric_amd(segment.strip())
            if not segment:
              continue
            formatted = handle_name_amd(segment).strip()

            # Extract the title more robustly
            match = re.search(r'\b(MR|MRS|MS|MSTR|MISS|CHD)\b', formatted.upper())
            title = match.group(1) if match else ""

            if title in ["MR", "MRS", "MS"]:
              adult_count += 1
            elif title in ["MSTR", "MISS", "CHD"]:
              child_count += 1
            passenger_names.append(formatted)
            count += 1
    else:
      index = item.strip().split(" ")
      if flag == 0:
        airline_name = get_airline_name(index[2][:2])  # flight code is part of index[2]
        output += f"\n*By {airline_name}*\n"
        flag = 1
        
      # if code and number are gabung
      if len(index[2]) > 2:
        flight_code = index[2][:2] 
        flight_number = index[2][2:]  
        index = index[:2] + [flight_code, flight_number] + index[3:]
      # print(index)

      # kalau inputnya ada yang ga pakai '*'
      # print("before: " + index[6])
      if '*' not in index[6]:
        index[6] = index[6] + '*' + index[7]
        del index[7]
        # print("after: " + index[6])
      
      output += clean_schedule_amd(index)

  # Now handle passenger names:
  passenger_output = ""
  if len(passenger_names) == 1:
    passenger_output += passenger_names[0] + "\n"
  else:
    for idx, name in enumerate(passenger_names, 1):
      passenger_output += f"{idx}. {name}\n"

  output = passenger_output + output

  if adult_count:
    output += "Adult : *Rp xxx*\n"
  if child_count:
    output += "Child : *Rp xxx*\n"
    
  output += "\n> Ticketing Time Limit :"
  
  return output

### END of AMADEUS FUNCTION LOGIC ###

### GARUDA ###
def clean_schedule_garuda(text):
  datetime = text[5]
  city = text[7][:3] + "-" + text[7][3:]
  dep_time = text[10][:2]+"."+text[10][2:]
  arr_time = text[11][:2]+"."+text[11][2:]
  flight_number = text[1] + text[2] + text[3]
  class_type = text[4]
  output = datetime + " | " + city + " | " + dep_time + "-" + arr_time + " | " + flight_number + " " + class_type + "\n"
  return output

def handle_confirmation_garuda(text):
  lines = [line.strip() for line in text.splitlines() if line.strip()]
  passengers = []
  flights = []
  ff_number = ""
  adult_count = 0
  child_count = 0

  output_text = ""

  for i, line in enumerate(lines):
    # Detect and extract all passenger lines like 1.RAZALI/IRSAN MR
    if re.match(r'^\d+\.\w+\/\w+', line):
      # Split by passenger number markers like 1. 2. etc.
      name_segments = re.split(r'\s*(?=\d+\.)', line.strip())
      for segment in name_segments:
        segment = remove_numeric_amd(segment.strip())
        if not segment:
          continue
        formatted = handle_name_amd(segment).strip()

        # Extract the title more robustly
        match = re.search(r'\b(MR|MRS|MS|MSTR|MISS|CHD)\b', formatted.upper())
        title = match.group(1) if match else ""

        if title in ["MR", "MRS", "MS"]:
          adult_count += 1
        elif title in ["MSTR", "MISS", "CHD"]:
          child_count += 1
        passengers.append(formatted)

    # Flight detail line
    elif " GA " in line and re.search(r'\bGA\d{2,4}\b', line):
      flights.append(line)

    # Frequent flyer
    elif "SSR FQTV GA" in line:
      match = re.search(r'GA(\d+)', line)
      if match:
        ff_number = match.group(1)

  # Output passenger names
  for idx, passenger in enumerate(passengers, 1):
    if idx == 1 and ff_number:
      output_text += f"{passenger} #{ff_number}\n"
    else:
      output_text += f"{idx}. {passenger}\n" if len(passengers) > 1 else f"{passenger}\n"

  output_text += "\n*By Garuda*\n"

  for line in lines:
    parts = re.split(r'\s+', line.strip())
    if len(parts) >= 12 and parts[1] == "GA":
      # print("DEBUG:", parts)
      # Fix GA185
      if len(parts[2]) > 2:
        parts = parts[:2] + [parts[2][:2], parts[2][2:]] + parts[3:]
        # Simple fix: remove the stray item if length is 1 at a known index
      if len(parts) > 13:
        del parts[10]

      # print("DEBUG (after):", parts)
      if len(parts) >= 12:
        output_text += clean_schedule_garuda(parts)

  if adult_count:
    output_text += "Adult : *Rp xxx*\n"
  if child_count:
    output_text += "Child : *Rp xxx*\n"

  output_text += "\n> Ticketing Time Limit :"

  return output_text
### END OF GARUDA LOGIC ###

### CITILINK ###
def parse_konfirmasi_citilink(text):
  print("\nResult Konfirmasi\n")
  lines = text.strip().split('\n')
  pass_idx = get_index(lines, "Penumpang & Daftar kursi") + 2
  inf_idx = get_index(lines, "Detil Penumpang") + 2
  output_text = ""
  num = 1

  # General regular expression to match any prefix consisting of uppercase letters followed by a space
  prefix_pattern = re.compile(r"^(MR|MS|MRS|MISS|MSTR|CAPT|PROF)\b", re.IGNORECASE)

  passengers = []
  infants = []

  # Get Passenger Data
  for index in range(pass_idx, len(lines)):
    line = lines[index].strip()
    # print(line)
    # Check if the line is part of the "Berangkat" section and break
    if "Berangkat" in line:
      break

    # Split the line on tabs and check if the line matches the prefix pattern
    split_data = line.split("\t")
    # print(split_data)
    if len(split_data) > 0 and prefix_pattern.match(split_data[0].strip()):
      if "MSTR" in split_data[0]:
        passengers.append(split_data[0].strip() + " *Child*")
      else:
        passengers.append(split_data[0].strip())

      # output_text += pass_name + "\n"
      # num += 1

  # Get Infant Data
  for i in range(inf_idx, len(lines)):
    line = lines[i].strip()

    if "Penumpang & Daftar kursi" in line:
      break

    if line and not any (x in line for x in ["Passenger", "Type", "Gender"]):
      name = line.strip()
      if i + 1 < len(lines) and "Infant" in lines[i + 1]:
        inf_name = name.split("Perjalanan dengan")[0]
        infants.append(inf_name)

  total_passengers = len(passengers) + len(infants)
  
  if total_passengers == 1:
    output_text += passengers[0] + "\n"
  else:
    for idx, passenger in enumerate(passengers, 1):
      output_text += f"{idx}. {passenger}\n"

  # Output Infant Data
  start_num = len(passengers) + 1 if total_passengers > 1 else 2
  for idx, infant in enumerate(infants, start_num):
    output_text += f"{idx}. {infant} *Infant*\n"

  # Get Itin
  itin_idx = get_index(lines, "Berangkat") + 2
  # print(lines[itin_idx:])

  output_text += "\n*By Citilink*\n"

  while itin_idx < len(lines):
    if "Kembali" in lines[itin_idx]:
      itin_idx += 1
      continue
    # Extract date
    date_pattern = r"\d{2} \w+ \d{2}"

    # Convert the list slice to a string before using it in re.search
    date_match = re.search(date_pattern, ' '.join(lines[itin_idx:]))
    date = date_match.group(0) if date_match else ""
    # print(date)

    # Extract airport codes
    place_pattern = r"\b([A-Z]{3})\b"

    # Convert the list slice to a string before using it in re.findall
    places = re.findall(place_pattern, ' '.join(lines[itin_idx:]))
    # print(places)
    # if len(places) < 2:
    #   itin_idx += 5  # Skip to the next iteration if not enough codes are found
    #   continue

    itinerary = places[0] + "-" + places[1] if len(places) >= 1 else ""

    # Extract time
    time_pattern = r"Jam (\d{1,2}.\d{2})"

    # Convert the list slice to a string before using it in re.findall
    times = re.findall(time_pattern, ' '.join(lines[itin_idx:]))
    normalized_times = []
    for t in times:
        hour, minute = t.split(".")
        normalized_time = f"{int(hour):02}.{minute}"  # ensures 2-digit hour
        normalized_times.append(normalized_time)

    if len(normalized_times) >= 2:
        time_info = f"{normalized_times[0]}-{normalized_times[1]}"
    else:
        time_info = ""

    # print("time: " + time_info)

    # Extract flight number
    flight_number_pattern = r"Penerbangan\s+([A-Z]+\s*\d+)"
    flight_match = re.search(flight_number_pattern, ' '.join(lines[itin_idx:]))
    # print(flight_match)
    flight_number = flight_match.group(1).replace(" ", "") if flight_match else ""
    # print(flight_number)

    # Combine all information
    if date and itinerary and time_info:
        full_itinerary = f"{date} | {itinerary} | {time_info} | {flight_number}\n"
        # print("Itinerary:", full_itinerary)
        output_text += full_itinerary

    itin_idx += 5

  return output_text
### END OF CITILINK LOGIC###

### LION AIR LOGIC ###
def parse_passenger_details(lines):
    pass_idx = get_index(lines, "Passenger Details") + 2
    output_text = ""
    passengers = []
  
    for i in lines[pass_idx:]:
        if "Itinerary Details" in i:
            break
          
        split_data = i.split("\t")
      
        if len(split_data) < 2:
            continue
          
        no_urut = split_data[0].strip()
        name = split_data[1].strip()
        passenger_number = re.match(r'(\d+)', no_urut)
        
        if passenger_number:
            no_urut = passenger_number.group(1) + "."
        else:
            no_urut = ''

        passengers.append((no_urut, name))
    
    # check passengers count
    if len(passengers) == 1:
        output_text += passengers[0][1] + "\n"  # only the name, no number
    else:
        for no_urut, name in passengers:
            pass_name = no_urut + " " + name
            output_text += pass_name + "\n"
    return output_text.strip()

def parse_itinerary(lines, itin_start_idx):
    itineraries_lines = lines[itin_start_idx:]
  
    # Split itineraries into segments
    flight_segments = []
    current_segment = []
    for line in itineraries_lines:
        if not line.strip():
            continue  # Skip empty lines
        if re.match(r'\s*[A-Za-z ]+[A-Za-z]{2}\d+', line):
            # This is a flight line, start new segment
            if current_segment:
                flight_segments.append(current_segment)
                current_segment = []
            current_segment.append(line)
        else:
            current_segment.append(line)
    if current_segment:
        flight_segments.append(current_segment)

    # Patterns for extracting information
    airport_pattern = r"\(([A-Z]{3})\)"
    date_pattern = r", ?(\d{1,2}) ?(\w{3})"
    time_pattern = r"(\d{2}:\d{2})"

    airline_list = []
    itineraries = []

    for segment in flight_segments:
        segment_idx = 0
        airline_name = ""
        flight_number = ""
        dep_place = ""
        dep_time = ""
        dep_date = ""
        arr_place = ""
        arr_time = ""
        arr_date = ""

        # Extract airline name and flight number
        flight_line = segment[segment_idx].strip()
        segment_idx += 1
        match = re.match(r'^(.*?)\s*([A-Za-z]{2}\d+)$', flight_line)
        if match:
            airline_name = match.group(1).strip()
            flight_number = match.group(2).strip()
        else:
            # Handle cases like "Batik AirID7021"
            match = re.match(r'^(.*? Air)([A-Za-z]{2}\d+)', flight_line)
            if match:
                airline_name = match.group(1).strip()
                flight_number = match.group(2).strip()
            else:
                continue  # Unable to parse flight line

        if airline_name not in airline_list:
            airline_list.append(airline_name)

        # Skip aircraft type line if present
        if segment_idx < len(segment):
            next_line = segment[segment_idx].strip()
            if not re.search(airport_pattern, next_line) and not re.search(time_pattern, next_line):
                segment_idx += 1

        # Extract dep_place and dep_time
        dep_place_found = False
        prev_line = "" 
      
        while segment_idx < len(segment):
            line = segment[segment_idx].strip()
            dep_place_match = re.findall(airport_pattern, line)
            dep_time_match = re.search(time_pattern, line)
            dep_date_match = re.search(date_pattern, line)
            
            if dep_place_match and not dep_place_found:
                dep_place = dep_place_match[0]  # Extract only the first match for departure place
                dep_place_found = True  # Mark dep_place as found to avoid overwriting it
                # print("Departure Place: ", dep_place)
            if dep_time_match:
                dep_time = dep_time_match.group(1)
            if dep_date_match:
                dep_date = dep_date_match.group(1) + " " + dep_date_match.group(2)

            # Store the previous line before moving to the next line
            prev_line = line

            # If all departure details are found, proceed to next
            if dep_place and dep_time and dep_date:
                segment_idx += 1
                break
            segment_idx += 1

        # Extract arr_place, arr_time, and arr_date
        arr_place_found = False
        while segment_idx < len(segment):
            line = segment[segment_idx].strip()
            # print(line)

            arr_place_match = re.findall(airport_pattern, line)
            # print("arr_place_match: ", arr_place_match)
            arr_time_match = re.search(time_pattern, line)
            arr_date_match = re.search(date_pattern, line)

            if arr_place_match and not arr_place_found:
              arr_place = arr_place_match[0]
              arr_place_found = True
              # print("Arrival Place: ", arr_place)
            # If the current line does not contain an airport pattern, check the previous line for arrival place
            elif not arr_place_match and prev_line:
                prev_place_match = re.findall(airport_pattern, prev_line)
                if prev_place_match:
                    arr_place = prev_place_match[-1]  # Use the last match for arrival place
                    arr_place_found = True
                    # print("Arrival Place (from previous line): ", arr_place)

            # Handle arrival time and date on the current line
            if arr_time_match:
                arr_time = arr_time_match.group(1)
            if arr_date_match:
                arr_date = arr_date_match.group(1) + " " + arr_date_match.group(2)

            # If all arrival details are found, proceed
            if arr_place and arr_time and arr_date:
                segment_idx += 1
                break
            segment_idx += 1

        # After processing all lines, check if all data was found
        if dep_place and dep_time and arr_place and arr_time and dep_date:
            itinerary = dep_place + "-" + arr_place
            date = dep_date
            time = dep_time + "-" + arr_time
            flight_info = date + " | " + itinerary + " | " + time + " | " + flight_number
            itineraries.append(flight_info)
        else:
            continue 

    if not itineraries:
        return "No itinerary details found."
    output_text = "*By " + ", ".join(airline_list) + "*\n"

    for itin in itineraries:
        output_text += itin + "\n"

    return output_text.strip()

def parse_konfirmasi_lionair(text):
    lines = text.strip().split('\n')
    output_text = ""

    # Process passenger details
    passenger_details = parse_passenger_details(lines)
    output_text += passenger_details + "\n\n"

    # Determine the starting index of itinerary details
    itin_start_idx = get_index(lines, "Itinerary Details") + 2

    # Parse the itinerary details
    itineraries_output = parse_itinerary(lines, itin_start_idx)
    output_text += itineraries_output

    print("\nResult Konfirmasi\n")
    print(output_text)
    return output_text

### END OF LION AIR LOGIC ###

### JETSTAR LOGIC ###
def parse_jetstar(text):
  print("\nResult Konfirmasi\n")
  lines = text.strip().split('\n')
  pass_idx = get_index_multiple(lines, ["Penumpang", "Passengers"]) + 1
  output_text = ""
  num = 1

  passengers = []

  # Get Passenger Data
  while pass_idx < len(lines):
    # split_data = lines[i].split("\t")
    line = lines[pass_idx].strip()

    if not line:
      break
    if "(" in line and ")" in line:
      pass_idx += 1
      continue

    # if len(split_data) > 0:
    passengers.append(line)
    pass_idx += 1
  
  # Add passengers to output
  if len(passengers) == 1:
    output_text += f"{passengers[0]}\n"
  else:
    for i, p in enumerate(passengers, 1):
      output_text += f"{i}. {p}\n"

  output_text += "\n*By Jetstar Airlines*\n"
  
  # Get Itin
  itin_idx = get_index_multiple(lines, ["Booking reference", "REFERENSI PEMESANAN"]) + 2

  while itin_idx < len(lines):
    line = lines[itin_idx].strip()

    # Find flight number
    if re.match(r'^[A-Z0-9]{2,4}\d{2,4}$', line):  # e.g. 3K287
      flight_number = line

      # Expect format to be:
      # line: SIN
      # line: KNO
      origin = lines[itin_idx - 2].strip()
      destination = lines[itin_idx - 1].strip()
      route = f"{origin}-{destination}"

      # Find departure time (should be ~7 lines ahead)
      for j in range(itin_idx + 1, len(lines)):
        if re.match(r'\d{1,2}:\d{2}[ap]m', lines[j], re.IGNORECASE):
          dep_time_raw = lines[j].strip()
          dep_time = convert_time24h(dep_time_raw)
          arr_time_raw = lines[j + 4].strip()
          # print(arr_time_raw)
          arr_time = convert_time24h(arr_time_raw)
          date_line = lines[j - 1].strip()
          try:
            date = datetime.strptime(date_line, "%a\n%d %b %Y").strftime("%d %b %Y")
          except:
            date = date_line  # fallback

            output_text += f"{date} | {route} | {dep_time}-{arr_time} | {flight_number}\n"
            break
      break  # assuming one segment

    itin_idx += 1

  return output_text
  
### END OF JETSTAR LOGIC ###
def main_amd(text):
  if(is_confirmation_amd(text)):
    return handle_confirmation_amd(text)
  else:
    return handle_schedule_amd(text)

def main_airasia(text):  
  if(is_penawaran(text)):
    return parse_penawaran_air_asia(text)
  else:
    return parse_konfirmasi_air_asia(text)

def main_sq(text):
  if is_konfirmasi_new(text):
    return parse_konfirmasi_1(text)
  else:
    return parse_flight_schedule(text)

def main_garuda(text):
  return handle_confirmation_garuda(text)

def main_citilink(text):
  return parse_konfirmasi_citilink(text)

def main_lionair(text):
  return parse_konfirmasi_lionair(text)

def main_jetstar(text):
  return parse_jetstar(text)

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
  def text_box_1_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  def text_box_2_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  def convert_click(self, **event_args):
    """This method is called when the button is clicked"""
    # convert_result = anvil.server.call('convert',  self.text_area.text)
    airline = self.airline.selected_value
    
    if self.text_area.text:
      summary = None
      if airline == "SQ":
        summary = main_sq(self.text_area.text)

      if airline == "Air Asia":
        summary = main_airasia(self.text_area.text)

      if airline == "AMADEUS":
        summary = main_amd(self.text_area.text)

      if airline == "GARUDA":
        summary = main_garuda(self.text_area.text)

      if airline == "CITILINK":
        summary = main_citilink(self.text_area.text)

      if airline == "Lion Air":
        summary = main_lionair(self.text_area.text)

      if airline == "Jetstar":
        summary = main_jetstar(self.text_area.text)
        
      if summary:
        self.btn_copy.visible = True
        self.result.visible = True
        self.result.text = summary
        self.result.underline = False
    pass

  def outlined_button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.text_area.text = ""
    pass

  def btn_copy_click(self, **event_args):
    """This method is called when the button is clicked"""
    get_open_form().call_js("cpy", self.result.text)
    n = Notification("Copied to Clipboard", title="Status", style="success")
    n.show()

  def airline_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
    
