python3 run_me_first.py &
sleep 0.5
firefox --kiosk --private-window localhost:5000/src/index.html &
sleep 0.5
WINDOWID=`xdotool search --onlyvisible --name firefox`
echo $WINDOWID
xdotool windowmove $WINDOWID 1920 0
