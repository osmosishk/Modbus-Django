import minimalmodbus
import os.path
import time
import signal
import os, sys
import socket
import logging
import MySQLdb as mdb
import subprocess
#savefilepath = "/var/log/modbusdatalogger/"
savefilepath = "C:/Github/Modbus-Django/modbus/"


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


def get_slaves():  # Get the slaves enabled and save his settings
    with con:
        # try:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT IDSlaves,Name,MAC FROM slaves_slaves WHERE Enable ='1'")
        IDSlaves = cur.fetchall()

        if len(IDSlaves) == 0:  # IF there isnt any slave enabled
            logger.info('No Slaves Enabled. Revise settings. Exiting')
            sys.exit(0)
        in_p = ','.join(str(slave['IDSlaves']) for slave in IDSlaves)# Get all IDSlaves with colons

        sql = 'SELECT * FROM slaves_setting WHERE Slaves_id IN (%s)'  # Get slaves's settings from idslaves enabled
        sql = sql % in_p
        cur.execute(sql)
        Slaves_Enabled_Settings = cur.fetchall()


        i = -1
        sql = 'SELECT * FROM slaves_address WHERE Slaves_id IN (%s)'  # Get slaves's Address from idslaves enabled
        sql = sql % in_p

        cur.execute(sql)
        Slaves_Enabled_Address = cur.fetchall()


        #print("Total rows are:  ", len(Slaves_Enabled_Address))
        cur.close()

        for slave in Slaves_Enabled_Settings:  # Slaves enabled. Get settings
            i = i + 1
            #print(slave)
            Slaves.append(instrument_map())
            Slaves[i].instrument = minimalmodbus.Instrument('COM7', int(slave['Slaves_id']))
            Slaves[i].instrument.serial.baudrate = slave['Baudrate']
            Slaves[i].instrument.serial.parity = slave['Parity']
            Slaves[i].instrument.serial.stopbits = int(slave['Stop'])
            Slaves[i].instrument.serial.bytesize = int(slave['Bits'])
            Slaves[i].instrument.serial.timeout = 0.2
            Slaves[i].instrument.mode = minimalmodbus.MODE_RTU
            Slaves[i].IDSlave = slave['Slaves_id']



            for s in IDSlaves:# iterate IDSlaves enabled to get the name
                if int(s['IDSlaves']) == int(slave['Slaves_id']):

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
            #print(Slaves[i].address_dict)
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


def test_slaves(Slaves):  # Test the Slaves conexions and disable the ones who does not reply

    for slave in Slaves:


        slave.conexion_up = False
        for address in slave.address_dict:  # for each address in each slave
            address_value = None  # Value read from the address
            count = 0  # counter to try read 10 times

            while address_value == None and count < 10:
                try:
                    slave.instrument.serial.flushInput()
                    address_value = slave.instrument.read_long(int(slave.address_dict[address]['Address']), 3)
                    #address_value = slave.instrument.read_long(2, 3)
                    #print (address_value)

                    time.sleep(0.5)
                except Exception as e:
                    count = count + 1
                    if count == 10:
                        logger.error("Error reading address. Slave: %s-%s:Address: %s. Exception:%s" % (
                        str(slave.IDSlave), str(slave.Name), str(slave.address_dict[address]), e))

            if address_value is not None:
                logger.info('  Slave :%s Address:%s works' % (  slave.IDSlave, slave.address_dict[address]['Address']))
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
def checkTableExists(tablename):
    try:
        con = mdb.connect('localhost', 'pi', 'raspberrytony', 'modbus')
        cur = con.cursor()
    except Exception as e:
        logger.error('Cant connect with database: %s', e)
        sys.exit(0)

    cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
    if cur.fetchone()[0] == 1:
        cur.close()
        return True

    cur.close()
    return False

def save_header_log(slave):
    today_date = time.strftime("%Y-%m-%d")

    if checkTableExists("helloworld"):
        print("Table exist")
    else:
        print("Table don't exit")



    if not os.path.exists(savefilepath + str(slave.IDSlave) + '-' + slave.MAC.replace(':','') + '-' + slave.Name + '-' + today_date + ".tmp"):
        # Mv tmp to log so uploadFTP can find them.
        print("Tmp log file exist")
        for filename in os.listdir(savefilepath):
            base_file, ext = os.path.splitext(filename)
            if ext == ".tmp":
                os.rename(savefilepath + filename, savefilepath + base_file + '.log')
        file_log = open(savefilepath + str(slave.IDSlave) + '-' + slave.MAC.replace(':',
                                                                                    '') + '-' + slave.Name + '-' + today_date + '.tmp',
                        'w+')
        header_file = ''
        for address in slave.address_dict:
            header_file += str(slave.address_dict[address]['Name']) + '(' + str(
                slave.address_dict[address]['Unit']) + ')' + ';'

        file_log.write(header_file + 'time' + '\n')
        file_log.close()



def save_row(string, slave):
    today_date = time.strftime("%Y-%m-%d")
    file_log = open(savefilepath + str(slave.IDSlave) + '-' + slave.MAC.replace(':','') + '-' + slave.Name + '-' + today_date + '.tmp','a')
    file_log.write(string_reads + time.strftime("%H:%M:%S") + '\n')
    print("Writing Value" , string_reads)
    file_log.close()




Slaves = get_slaves()
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
                try:
                    print("Reading Address %s /  Type %s" % (
                        slave.address_dict[address]['Address'], slave.address_dict[address]['value_class']))

                    # print("Slave:%s, IDAddress:%s, Address:%s, Value:%s" % (slave.IDSlave,address,slave.address_dict[address],slave.instrument.read_long(slave.address_dict[address],3)))
                    # value=slave.instrument.read_long(slave.address_dict[address]['Address'],3,signed=True)#get the value

                    value = slave.instrument.read_long(int(slave.address_dict[address]['Address']), 3, True, 0)
                    #value = slave.instrument.read_float(int(slave.address_dict[address]['Address']), 3,4, 0)
                    #value = slave.instrument.read_register(int(slave.address_dict[address]['Address']),2)

                    # save a row in log table
                    time.sleep(1)
                    string_reads += str(value) + ';'


                except Exception as e:
                    logger.info('Real - Address no reachable-%s', e)
                    # value="NULL";
                    if count == 9:
                        string_reads += '-' + ';'
                    slave.instrument.serial.flushInput()
                    count = count + 1

                    # cur = con.cursor(mdb.cursors.DictCursor)
                    # sql = "INSERT INTO Log(IDSlave,IDAddress,Value,Date) VALUES(%s,%s,%s,'%s')" #
                    # sql = sql % (slave.IDSlave,address,value,date_for_row_log_values)
                    #	logger.info(sql)
                    # cur.execute(sql)

        save_header_log(slave)
        save_row(string_reads, slave)


    time.sleep(5)
