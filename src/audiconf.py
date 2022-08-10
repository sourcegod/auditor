#! /usr/bin/env python
"""
    File: audiconf.py
    Configuration manager for Auditor
    Date: Sun, 07/08/2022
    Author: Coolbrother
"""

import xml.etree.ElementTree as ET

class AudiConf(object):
    """ Configuration manager """
    def __init__(self):
        self._instru_lst = []

    #-------------------------------------------

    def load(self, filename):
        """
        load XML file
        from AudiConf object
        """
        
        root_note = None
        self.instru_lst = []
        try:
            root_node = ET.parse(filename).getroot()
        except FileNotFoundError as err:
            print("Error: configuration file not found", err)
            return False
        
        # print(f"root_node: {root_node}")

        for elem in root_node.findall('instrumentList/instrument'):
            instru_dic = {}
            instru_dic["id"] = elem.findtext('id')
            filename = elem.findtext('filename')
            if filename is not None:
                instru_dic["filename"] =  filename
            else:
                layer = elem.find('layer')
                if layer is not None:
                    filename = layer.findtext('filename')
                instru_dic["filename"] =  filename


            instru_dic["name"] = elem.findtext('name')
            instru_dic["volume"] = elem.findtext('volume')
            instru_dic["isMuted"] = elem.findtext('isMuted')
            instru_dic["pan_L"] = elem.findtext('pan_L')
            instru_dic["pan_R"] = elem.findtext('pan_R')
            
            self.instru_lst.append(instru_dic)
            
        """
        for item in self.instru_lst:
            # print(item)
            print(f"id: {item['id']}, filename: {item['filename']}, name: {item['name']}")
            print(f"volume: {item['volume']}, isMuted: {item['isMuted']}, pan_L: {item['pan_L']}, pan_R: {item['pan_R']}")
        """    
        
        print("Loading Configuration file...")
        return True            
   
    #-------------------------------------------
    
    def get_instruments(self):
        """
        returns instrument list
        from AudiConf object
        """

        return self.instru_lst

    #-------------------------------------------

#========================================


if __name__ == "__main__":
    filename = "/var/tmp/test/drumkit_1.xml"
    app = AudiConf()
    app.load(filename)
    input("It's OK...")
#-------------------------------------------
