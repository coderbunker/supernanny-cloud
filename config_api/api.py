#!flask/bin/python
from flask import Flask, jsonify

import json
import logging

logger = logging.getLogger('get.arduino.config')

class ArduinoDataTransferObj():
    location = ''
    room = ''
    mac = ''
    sensor_type = ''
    port = ''
    offset_temperature = 0
    offset_humidity = 0

def init_logger():
    logger.info('Logger initialization started')
    hdlr = logging.FileHandler('logfile.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    logger.info('Logger initialization finished')

def getJsonConfig():
    with open('config.json', 'r') as json_config_file:
        json_read = json_config_file.read()
        return json.loads(json_read)

def getJsonDataTransferObj(arduinoMac):
    logger.info('Get configuration for ' + arduinoMac)
    piConfig = config['arduinoConfigs']
    arduino_dto = None 
    for room in piConfig['rooms']:
        for arduino in room['arduinos']:
            if arduino['mac'] == arduinoMac:
                arduino_dto = ArduinoDataTransferObj
                arduino_dto.location = piConfig['location']
                arduino_dto.room = room['name']
                arduino_dto.mac = arduinoMac
                arduino_dto.sensor_type = arduino['sensor_type']
                arduino_dto.port = arduino['port']

                # TODO: Is there any possibility to remove hardcoded values?
                if arduino_dto.sensor_type == 'quality':
                    arduino_dto.offset_temperature = arduino['offset_temperature']
                    arduino_dto.offset_humidity = arduino['offset_humidity']

                logger.info('Configuration for ' + arduinoMac + ' found')
                break
        if arduino_dto != None:
            break

        logger.info('Getting configuration finished')
    return arduino_dto
            
app = Flask(__name__)
init_logger()
config = getJsonConfig()

@app.route('/api/v1.0/config', methods=['GET'])
def get_config():
    return jsonify({'config': config})

@app.route('/api/v1.0/config/<string:config_mac>', methods=['GET'])
def get_task(config_mac):
    return getJsonDataTransferObj(config_mac).__dict__

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
