#!/bin/bash
#Launch PPTP VPN Connections and add routers
#By HSS
#2014-10-25

if [ ! -e "/etc/ppp/peers/$1" ]; then
  echo "\
The file /etc/ppp/peers/$1 does not exist. Please create it or use
a command line argument to use another file in the /etc/ppp/peers/ directory."
  exit 1
fi


num=`ps -A |grep -c \`basename "$0"\``
if [ $num -gt 2 ];then
 echo another daemon running
 exit
fi




if [ -x /usr/bin/kill ]; then
  KILL="/usr/bin/kill"
else
  KILL="/bin/kill"
fi
SIG=TERM
DONE="stopped"
MODE=""

[ ! -n "$1" ] && echo NO provider peer specificed,terminatering && exit 1

############################################################################
#get the ppp name via pid
function get_ppp_name(){
	if ls /var/run/ppp*.pid >/dev/null 2>&1;then
		for pids in /var/run/ppp*.pid;do
        	if [ `cat $pids` == $1 ];then
                	echo `basename $pids|cut -d . -f 1`
                	break
        	fi
        	done
	fi

}

#function to add default gate way for provider id
function add_route(){
	route add default dev $1
	/usr/local/pptp-vpn/cczu-route.sh >/dev/null 2>&1
	echo route added!
}

#get the pid of provider of peer
function getid() {
PEER=$(echo $1 | sed -e 's#/#\\/#g')
PID=$(ps -o pid,cmd axw | awk "/^ *[0-9]* *(\/usr\/sbin\/)?pppd call $PEER( |\$)/ {print \$1}")
echo $PID
}

#kill the provider of ppp
function kill_peer(){
PID=$1
if [ "$PID" ]; then
    $KILL -$SIG $PID || {
        echo "$0: $KILL failed.  None ${DONE}."
        exit 1
    }
else
   echo "$0: I could not find a pppd process for provider '$1'. None ${DONE}."
   exit 1
fi
}

function connect(){
providerID=`getid $1`
if [ -n "$providerID" ];then
	echo there is already a provider named $1 exits,which the pid is $providerID
	#exit
else
	i=0
	echo provider $1 not found,will start it 
	while [ True ]
	do
		poff $1 >/dev/null
		pon $1
		newID=`getid $1`
		sleep 8
		#echo $newID "<-ID"
		ppp_name=''
		if /sbin/ifconfig |grep `get_ppp_name $newID` >/dev/null 2>&1;then
			
			echo $newID ======= `get_ppp_name $newID`
			ppp_name=`get_ppp_name $newID`
		fi
		if [ -n "$ppp_name" ];then
			add_route $ppp_name
			echo provider $1 started!
			break
		fi
		i=$(($i+1))
		poff $1 >/dev/null
		echo failed $i times
	done
fi
}

connect $1

echo $ppp_name is up

while [ True ]
do
if ! ifconfig |grep $ppp_name >/dev/null 2>&1 ;then
	connect $1
	echo $ppp_name is up
fi
sleep 3
done
