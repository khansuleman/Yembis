CC=g++
DLIBS=-lbcm2835 -lrt -lpthread
OBJS= *.o ../arduPi.o ../sim7020x.o
main:$(OBJS) 
	$(CC) -Wall -o main $(OBJS)  $(DLIBS) 

%.o:%.c
	$(CC) -c -o $@ $<

clean:
	rm -f *.o main

