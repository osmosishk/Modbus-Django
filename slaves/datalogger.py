import minimalmodbus
import os.path
import time
import signal
import os, sys
import socket
import logging
import MySQLdb as mdb
import subprocess

logger = logging.getLogger('modbusmysql')
logger.setLevel(logging.INFO)
file_log_handler = logging.FileHandler('modbusmysql.log')
logger.addHandler(file_log_handler)

stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

# nice output format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log_handler.setFormatter(formatter)
stderr_log_handler.setFormatter(formatter)

Slaves = []

try:
    con = mdb.connect('localhost', 'pi', 'raspberrytony', 'modbus');
except Exception as e:
    logger.error('Cant connect with database: %s', e)
    sys.exit(0)


def receive_signal(signum, frame):
    logger.info('Exiting cuase signal recieved...')
    sys.exit(0)




class instrument_map:
    pass

#it retrieve the setting from mysql . and configuration the minimodbus , also retrieve the address to save it into address_dict{} so the program can read every address

def get_slaves():  # Get the slaves enabled and save his settings
    with con:
        # try to connect with database:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT IDSlaves,Name,MAC FROM slaves_slaves WHERE Enable ='1'")
        IDSlaves = cur.fetchall()

        if len(IDSlaves) == 0:  # IF there isnt any slave enabled
            logger.info('No Slaves Enabled. Revise settings. Exiting')
            sys.exit(0)
        in_p = ','.join(str(slave['IDSlaves']) for slave in IDSlaves)  # Get all IDSlaves with colons
        sql = 'SELECT * FROM slaves_setting WHERE Slaves_id IN (%s)'  # Get slaves's settings from idslaves enabled
        sql = sql % in_p
        print("setting " + sql)
        cur.execute(sql)
        Slaves_Enabled_Settings = cur.fetchall() # fetch all slave basic data


        i = -1
        sql = 'SELECT * FROM slaves_address WHERE Slaves_id IN (%s)'  # Get slaves's Address from idslaves enabled
        sql = sql % in_p
        print("Address " + sql)
        cur.execute(sql)
        Slaves_Enabled_Address = cur.fetchall()# fetch all slave and related address to be read

        for slave in Slaves_Enabled_Settings:  # Slaves enabled. Get settings , maybe there many slaves 
            i = i + 1
            Slaves.append(instrument_map())
            Slaves[i].instrument = minimalmodbus.Instrument('COM3', int(slave['Slaveaddres']))
            Slaves[i].instrument.serial.baudrate = slave['Baudrate']
            Slaves[i].instrument.serial.parity = slave['Parity']
            Slaves[i].instrument.serial.stopbits = int(slave['Stop'])
            Slaves[i].instrument.serial.bytesize = int(slave['Bits'])
            Slaves[i].IDSlave = slave['Slaves_id']
            for s in IDSlaves:  # iterate IDSlaves enabled to get the name
                if s['IDSlaves'] == slave['Slaves_id']:
                    Slaves[i].Name = s['Name']
                    Slaves[i].MAC = s['MAC']
                    Slaves[i].IDSlave = s['IDSlaves']
            address_dict = {}  # Address dict for the current slave
            j = -1
            for slave_address in Slaves_Enabled_Address:  # Slaves address. Save in same IDSlave
                if slave_address['Slaves_id'] == slave['Slaves_id']:
                    j = j + 1
                    address_dict[j] = slave_address
            Slaves[i].address_dict = address_dict
            for add in address_dict:
                print
                "IDAddress: " + str(add)
                print
                "Name: " + str(address_dict[add]['Name'])
                print
                "Units: " + str(address_dict[add]['Unit'])
    # except Exception,e:
    # logger.error("Error getting Slaves configuration: %s",Exception)

    return Slaves


def test_slaves(Slaves):  # Test the Slaves conexions and disable the ones who does not reply and also read the address on slaves..display which address is work
    for slave in Slaves:
        slave.conexion_up = False
        for address in slave.address_dict:  # for each address in each slave
            address_value = None  # Value read from the address
            count = 0  # counter to try read 10 times
            
            # if cannot reach the address 10 times..it will stop
            while address_value == None and count < 10:
                try:
                    slave.instrument.serial.flushInput()
                    address_value = slave.instrument.read_long(slave.address_dict[address]['Address'], 3)
                    time.sleep(0.5)
                except Exception as e:
                    count = count + 1
                    if count == 10:
                        logger.error("Error reading address. Slave: %s-%s:Address: %s. Exception:%s" % (
                        str(slave.IDSlave), str(slave.Name), str(slave.address_dict[address]), e))
            if address_value is not None:
                logger.info('Slave :%s Address:%s works' % (slave.IDSlave, slave.address_dict[address]['Address']))
                slave.conexion_up = True
    # Disabling Slaves who does not reply and delete them

    for slave in Slaves[:]:
        if slave.conexion_up == False:
            sys.exit(0)
    #    sql = 'UPDATE Slaves SET Enabled=0 WHERE IDSlave=%s'%slave.IDSlave #Get slaves's Address from idslaves enabled
    #    with con:#


#	try:#
#	  cur = con.cursor(mdb.cursors.DictCursor)
#	  cur.execute(sql)
#	  Slaves.remove(slave)
#	except Exception,e:
#	  logging.error('Error disabling non reachable Slaves - %s',e)

# create a txt file to save the reading , the fileanme is todaytime+ IDshave +MAC of raspberry
def save_header_log(slave):
    today_date = time.strftime("%Y-%m-%d")
    
    #if the *.tmp is existed ..just keep write each row .
    if os.path.exists("/var/log/modbusdatalogger/" + str(slave.IDSlave) + '-' + slave.MAC.replace(':',
                                                                                                  '') + '-' + slave.Name + '-' + today_date + ".tmp") == False:
        # Mv tmp to log so uploadFTP can find them.
        for filename in os.listdir('/var/log/modbusdatalogger'):
            base_file, ext = os.path.splitext(filename)
            if ext == ".tmp":
                os.rename('/var/log/modbusdatalogger/' + filename, '/var/log/modbusdatalogger/' + base_file + '.log')

        file_log = open('/var/log/modbusdatalogger/' + str(slave.IDSlave) + '-' + slave.MAC.replace(':',
                                                                                                    '') + '-' + slave.Name + '-' + today_date + '.tmp',
                        'w+')
        header_file = ''
        for address in slave.address_dict:
            header_file += str(slave.address_dict[address]['Name']) + '(' + str(
                slave.address_dict[address]['Units']) + ')' + ';'
        file_log.write(header_file + 'time' + '\n')
        file_log.close()


# save each row with data reading
def save_row(string, slave):
    today_date = time.strftime("%Y-%m-%d")
    file_log = open('/var/log/modbusdatalogger/' + str(slave.IDSlave) + '-' + slave.MAC.replace(':',
                                                                                                '') + '-' + slave.Name + '-' + today_date + '.tmp',
                    'a')
    file_log.write(string_reads + time.strftime("%H:%M:%S") + '\n')
    # print string_reads
    file_log.close()




Slaves = get_slaves() #create slaves
test_slaves(Slaves)
if len(Slaves) == 0:
    logger.info('No Slaves reachables. Revise settings. Exiting')
    sys.exit(0)

# infinite loop iterating slaves and address and saving into mysql
while True:
    for slave in Slaves:
        date_for_row_log_values = time.strftime('%Y-%m-%d %H:%M:%S')
        string_reads = ''
        slave.instrument.serial.flushInput()
        for address in slave.address_dict:
            value = None
            slave.instrument.serial.flushInput()
            count = 0
            while value == None and count < 10:
                with con:
                    try:
                        # print("Slave:%s, IDAddress:%s, Address:%s, Value:%s" % (slave.Name,address,slave.address_dict[address],slave.instrument.read_long(slave.address_dict[address],3)))
                        # value=slave.instrument.read_long(slave.address_dict[address]['Address'],3,signed=True)#get the value
                        value = slave.instrument.read_register(slave.address_dict[address]['Address'], 2, 3,
                                                               signed=True)
                        # save a row in log table
                        time.sleep(0.5)
                        string_reads += str(value) + ';'
                    except Exception as e:
                        logger.info('Address no reachable-%s', e)
                        # value="NULL";
                        if count == 9:
                            string_reads += '-' + ';'
                        slave.instrument.serial.flushInput()
                        count = count + 1
                        # time.sleep(0.5)

                # cur = con.cursor(mdb.cursors.DictCursor)
                # sql = "INSERT INTO Log(IDSlave,IDAddress,Value,Date) VALUES(%s,%s,%s,'%s')" #
                # sql = sql % (slave.IDSlave,address,value,date_for_row_log_values)
        #	logger.info(sql)
        # cur.execute(sql)
        #save_header_log(slave)
        #save_row(string_reads, slave)

    time.sleep(3)
