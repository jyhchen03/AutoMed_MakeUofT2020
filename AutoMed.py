import sys
import pymongo
import dns
import time
import datetime
from datetime import datetime
from inputimeout import inputimeout, TimeoutOccurred
import RPi.GPIO as GPIO
import AutoMed_mechanical as mech

class AutoMedGUI:
    def main(self):
        client = pymongo.MongoClient("mongodb+srv://charyu:MakeUofT2020@medicinecabinet-hrf12.azure.mongodb.net/test?retryWrites=true&w=majority")
        db = client['MedicineCabinet1']
        col = db['Medication']
        col2 = db['Actions']

        loop = True
        while loop:
            print('\n\nWelcome to the AutoMed! Please select a function:\n\t[1] Demo Dispense\n\t[2] Add Prescription')

            selected_function = input('Enter your selected function: ')

            if(selected_function.lower() == '1'):
                time_input = input('Demo: Select desired time of day (morning, afternoon, evening): ')

                times = {'morning':'9:00', 'afternoon':'12:00', 'evening':'18:00'}

                print('\nIt is ' + times.get(time_input) + '. Time to take your pills!')
                
                
                try:
                    #inputimeout(prompt='\nPlease confirm you are here. If you do not, we will send a reminder. ', timeout=30)
                    input('Confirm you are here, otherwise reminder will be sent. ')
                    self.dispense(col, time_input, col2)

                except TimeoutOccurred:
                    print('\nSend reminder')

            elif(selected_function.lower() == '2'):
                print('\nAdding prescription')
                self.add_prescription(col)

            elif(selected_function.lower() == 'exit'):
                loop = False
                exit()
            
            else:
                print ('Invalid input, please try again')

    def dispense(self, col, time_input, col2):
        needed_meds = []
        for i in col.find({time_input:True}, {'_id': 1, 'med': 1, 'dosage': 1, 'current': 1, 'med_type':1, 'location':1}):
            needed_meds.append(dict(i))

        print('\nMedicine being dispensed:')
        
        for med in needed_meds:
            print(med.get('dosage') + ' units of ' + med.get('med'))
                
        #Open and dispense medication
        mech.rotate_exit('open')
        for med in needed_meds:
            #send command to release/dispose remaining pills
            mech.rotate_system(med.get('location'), 'open')
            mech.led(med.get('location'))
            print('\nPlease take your pills!')
                    
        time.sleep(10)
        
        #Close medication doors
        mech.rotate_exit('close')
        for med in needed_meds:
            #send command to release/dispose remaining pills
            mech.led(med.get('location'), 'off')
            mech.cabinet(med.get('location'), 'close')
            
        #Append data
        for med in needed_meds:
            #Update current amount of that med
            med['current'] = str(int(med.get('current')) - int(med.get('dosage')))
            
            #Update MongoDB to new current count, and add medication action
            col.update_one({'_id':med.get('_id')}, {'$set': {'current':med.get('current')}})
            col2.insert_one({'time':datetime.now(),
                             'med':med.get('med'),
                             'dosage':med.get('dosage')})
            
            #Warn if low on refills
            if(int(med.get('current')) < (4 * int(med.get('dosage')))):
                print('Reminder: Get refills on ' + med.get('med') + ' soon! Only ' + str(int(med.get('current'))/int(med.get('dosage'))) + ' doses left!')
            
            #Clear dose if no more left 
            if(int(med.get('current')) < int(med.get('dosage'))):
                print('Not enough pills left for a dose. Please remove pills from the hopper.')
                
                #send command to release/dispose remaining pills
                if(med.get('location') == '0'):
                    mech.rotate_system(med.get('location'), 'open')
                    mech.led(med.get('location'))
                    print('\nPlease take and dispose of the remaining pills!')
                    time.sleep(10)
                    mech.led(med.get('location'), 'off')
                    mech.cabinet(med.get('location'), 'close')
                    
                else:
                    mech.cabinet(med.get('location'))
                    mech.led(med.get('location'), 'on')
                    print('\nPlease take and dispose of the remaining pills!')
                    time.sleep(10)
                    mech.led(med.get('location'), 'off')
                    
                col.update_one({'_id':med.get('_id')}, {'$set': {'location':'', 'current':'0'}})


    def sort_medication(self, col):
        used_locations = []
        compare_index = ['0','1','2']
        for i in col.find({'location': {'$ne':''}}, {'_id': 0, 'location': 1}):
            used_locations.append(i.get('location'))
        if len(used_locations) > 3:
            print ('Exceeded capacity, please remove medication before adding')
        else:
            temp3 = [item for item in compare_index if item not in used_locations]
        return temp3

    def add_prescription(self, col):
        #Gather info and log in database
        print('\nPlease enter info on your prescription: ')
        name = input('Drug name: ')
        dosage = input('Dosage: ')
        total = input('Total Number: ')
        morning = input('Take in morning? ')
        afternoon = input('Take in afternoon? ')
        evening = input('Take in evening? ')
        pharmacist = input('Dispensing pharmacist: ')
        doctor = input('Prescribing doctor: ')
        expiry = input('Expiry date: ')
        med_type = input('Med type (capsule or other): ')
        
        #Set location based on which cabinet was used
        #0 is cabinet, 1, 2 are compartments
        empty_location = self.sort_medication(col)
        print ('\nEmpty spaces: ' + str((empty_location)))
        location = self.check_spaces(empty_location, med_type)
        
        if location is not None:
            
            if(location != '0'):
                mech.rotate_hopper('open')
                
            mech.rotate_system(location, 'open')
            mech.led(str(int(location) + 3), 'on')
            
            time.sleep(10)
            
            mech.rotate_system(location, 'close')
            mech.led(str(int(location) + 3), 'off')
            if(location != '0'):
                mech.rotate_hopper('close')
            
            col.insert_one({'med': name,
                    'dosage': dosage,
                    'total': total,
                    'current': total,
                    'morning': morning,
                    'afternoon': afternoon,
                    'evening': evening,
                    'pharmacist': pharmacist,
                    'doctor': doctor,
                    'expiry': expiry,
                    'med_type': med_type,
                    'location': location})

    #Prompt patient to place meds into cabinet
    def check_spaces(self, empty_location, med_type):
        if(med_type.lower() == 'other'):
            if '0' in empty_location:
                print('\nOpening cabinet')
                return '0'
            else:
                print('Cabinet is full')

        elif(med_type.lower() == 'capsule'):
            if (('1' in empty_location) or ('2' in empty_location)):
                if '1' in empty_location:
                    print('\nOpening pill compartment 1')
                    return '1'
                else:
                    print('\nOpening pill compartment 2')
                    return '2'
            else:
                print ('Pill compartments are full')
        
        else:
            print('Invalid input, please input valid med type (capsule or other):')
    
        return None


#run main
automed = AutoMedGUI()
automed.main()