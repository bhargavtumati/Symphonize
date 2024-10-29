def timeConversion(s):
    # Write your code here
    if "PM" in s:
        time=(int)(s[0:2])
        if time<12:
            time=time+12
            return str(time)+s[2:len(s)-2]
        return s[:len(s)-2]
    elif "AM" in s:
        time=(int)(s[0:2])
        if time==12:
            return "00"+s[2:len(s)-2]
        return s[:len(s)-2]
    
s="07:05:45PM"
print(timeConversion(s))