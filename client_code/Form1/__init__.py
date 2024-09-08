from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import re
from datetime import datetime
import sys

def diff_day(date1, date2):  
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
  if is_konfirmasi(text) == True:
    kon = parse_konfirmasi(text)
    return kon

  else:
    flights = parse_penawaran(text)
    return flights



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
    
