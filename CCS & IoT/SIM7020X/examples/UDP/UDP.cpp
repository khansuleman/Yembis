/**
*  @filename   :   UDP.cpp
*  @brief      :   Implements for sim7020 4g hat raspberry pi demo
*  @author     :   Kaloha from Waveshare
*
*  Copyright (C) Waveshare     January 1 2019
*  http://www.waveshare.com / http://www.waveshare.net
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documnetation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to  whom the Software is
* furished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
* THE SOFTWARE.
*/

#include "../arduPi.h"
#include "../sim7020x.h"

// Pin definition
int POWERKEY = 4;

/*********************TCP and UDP**********************/
char aux_string[50];
char server_ip[] = "118.190.93.84";
char port[] = "2317";
char message[] = "Waveshare Sending UDP data with socket_id";


void setup() {

	sim7020.PowerOn(POWERKEY);
	
	memset(aux_string, '\0', 50);
	

	/***************Make sure all sockets are closed******************/
//	sim7020.sendATcommand("AT+CSOCL=0",500);
//	sim7020.sendATcommand("AT+CSOCL=1",500);
//	sim7020.sendATcommand("AT+CSOCL=2",500);
//	sim7020.sendATcommand("AT+CSOCL=3",500);
//	sim7020.sendATcommand("AT+CSOCL=4",500);

	/*********************5 road TCP client sockets Sending Test******************/
	//for(int i=0;i<5;i++)
	//{
		//sim7020.sendATcommand("AT+CSOC=1,1,1",2000);
		if(sim7020.sendATcommand("AT+CSOC=1,2,1","+CSOC:",500)){
			printf("Created UDP socket id %d Successfully!\n",0);
	//	}

	sim7020.sendATcommand("AT+CSOCON=0,2317,\"118.190.93.84\"",6000);
	sim7020.sendATcommand("AT+CSOSEND=0,0,\"Waveshare Send to Socket id 0 using UDP\"",6000);
	/*	snprintf(aux_string, sizeof(aux_string), "AT+CSOCON=%s,%s,\"%s\"", (char)('0'+i), port, server_ip);
		sim7020.sendATcommand(aux_string, "OK", 5000);

		snprintf(aux_string, sizeof(aux_string), "AT+CSOSEND=%s,0,\"%s%s\"", (char)('0'+i), message,(char)('0'+i));
		sim7020.sendATcommand(aux_string, 2000);*/
	}

	/***************Close all******************/
	printf("\n");
	sim7020.sendATcommand("AT+CSOCL=0",500);
	printf("Close Socket\n");
	//sim7020.sendATcommand("AT+CSOCL=1",500);
	//sim7020.sendATcommand("AT+CSOCL=2",500);
	//sim7020.sendATcommand("AT+CSOCL=3",500);
	//sim7020.sendATcommand("AT+CSOCL=4",500);

}


void loop() {

}

int main() {
	setup();
	return (0);
}