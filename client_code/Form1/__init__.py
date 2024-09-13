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
  # print("halo")
  flights = []
  i = 0

  first_departure_date = None
  
  while i < len(lines):
    # print("looping")
    flight = {}

    if len(lines) - i >= 12:
      flight['departure_date'] = lines[i]
      flight['arrival_date'] = lines[i+1]
      flight['departure_time'] = lines[i + 2]
      flight['arrival_time'] = lines[i + 3]
      flight['departure_airport_code'] = lines[i + 4]
      flight['arrival_airport_code'] = lines[i + 5]
      flight['flight_code'] = lines[i + 9]

      # print(flight['arrival_date'])
      
      if "Layover" not in lines[i-1]:
        first_departure_date = flight['departure_date']
        print("first " + first_departure_date)

      # and i+12 >= len(lines) -> untuk input 2 layover (3 flight) masih keitung days di flight ke-2nya
      if "Layover" in lines[i-1]:
        print("last " + flight['arrival_date'])
        days = diff_day(first_departure_date, flight['arrival_date'])
        print(days)
        flight['arrival_time'] += f"(+{days})" if days > 0 else ""
      
      flights.append(flight)
      
      if i+13 <= len(lines) and "layover" in lines[i+12].lower():
        i += 13
      else:
        i += 12 
    else:
      break
  
  output = "*By Singapore Airlines*\n"
  for flight in flights:
      output += f"{flight['departure_date']} | {flight['departure_airport_code']}-{flight['arrival_airport_code']} | {flight['departure_time']}-{flight['arrival_time']} | {flight['flight_code']}\n"
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
  passengerData = [line for line in lines if "Full Detail" in line]

  flights = []
  passengers = []
  output_text = ""

  for data in flightData:
    flight = {}
    data = data.split(" ")
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
    passengers.append(f"{data[2] if data[2] != '' else ''} {data[0]} {data[1]}")

  for i, passenger in enumerate(passengers, 1):
    output_text += f"{i}. {passenger}\n"
  
  output_text += "\n"
  output_text += "*By Singapore Airlines*\n"

  for flight in flights:
    output_text += f"{flight['departure_date']} | {flight['departure_airport_code']}-{flight['arrival_airport_code']} | {flight['departure_time']}-{flight['arrival_time']} | {flight['flight_code']} {flight['cabin_class']}\n"

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
  datetime = text[5]
  city = text[6][2:]
  city = city[:3] + "-" + city[3:]
  dep_time = text[9][:2]+"."+text[9][2:]
  arr_time = text[10][:2]+"."+text[10][2:]
  output = datetime + " | " + city + " | " + dep_time + "-" + arr_time + "\n"
  return output

def remove_numeric_amd(text):
  result = ''.join(i for i in text if not i.isdigit())
  return result

def handle_name_amd(text):
  split = text.split("(")[0].strip()
  split = split.split("/")
  last_name = split[0]
  front_name = split[1].split(" ")
  name = front_name[-1] + " " + ' '.join(front_name[0:len(front_name)-1]) + " " + last_name
  name = name.replace('FNU', '')
  name = re.sub(' +', ' ', name)
  return name

def handle_schedule_amd(text):
  split = text.split("\n")
  split = [i for i in split if "RTSVC" not in i]
  split = [i for i in split if len(i) != 0]
  flag = 1

  output = "*By Singapore Airlines*\n"

  for i in split:
    index = i.strip().split(" ")

    # kalau inputnya ada yang ga pakai '*'
    # print("before: " + index[6])
    if '*' not in index[6]:
      index[6] = index[6] + '*' + index[7]
      del index[7]
      # print("after: " + index[6])
      
    if flag == int(index[0]):
      output += clean_schedule_amd(index)
      flag+=1
  return output

def handle_confirmation_amd(text):
  split = text.split("\n")
  split = [i for i in split if "RTSVC" not in i]
  split = [i for i in split if len(i) != 0]

  output = ""
  pnr = ""
  count=1
  flag=0
  for idx, item in enumerate(split):
    if idx == 0:
      pnr = item
    elif "." in item:
      names = item.strip().split(".")
      for name in names:
        new_name = remove_numeric_amd(name)
        if len(new_name) != 0:
          output += str(count) + ". " + handle_name_amd(new_name) + "\n"
          count+=1
    else:
      if flag == 0:
        output += "\n*By ___ Airlines*\n"
        flag = 1
      index = item.strip().split(" ")
      output += clean_schedule_amd(index)          
  
  return output

### END of AMADEUS FUNCTION LOGIC ###

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
    return parse_penawaran_1(text)

def main_garuda(text):
  return "*****Still on Development*****\n.\n.\n.\n.\n.\n.\n.\n.\n*****Still on Development*****"

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

      if airline == "Garuda":
        summary = main_garuda(self.text_area.text)
      
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
    
