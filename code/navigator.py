# B= boat position
# T = Target position
# BH = boat heading
# WV = wind vector

# vt = ~vb · ~t0


# initualize begin values
# default value 0 of dezelfde met elkaar

# true wind angle = 0

# a= 0, vt,R,max=0, ?b,max,R=?w,abs,inv

# true wind angle = 0
# vt = (~vb · ~t0) , rechts, max boat angle

# ?b(max boat angle) rechts = ?w (hook van wind vector) 




# if(boating heading > boating heading right max)
# {
# 	set curring boat heading as boat heading right max
# 	max rechter hook van boot = (inverse absolute win hook + true wind hook)

# 	if(truewind a >= 180degrees(changeable)){
# 	do this again but for left side
# 	}else {true wind = truewind + delta truewind}


# }

# if((boat max right angle - (hook tussen b en eind bestemming)) < (boat max left angle -(hook tussen b en eind bestemming))
# {
# 	if(max boat heading right * efficiency < max boat heading left){
# 	new boat angle = max boat heading left
# 	}else {new boat angle = max boat heading right}
# 	return new boat angle;
# }

boatHeading = 0 #Vtr
boatHeadingMax = 0 #Vtrm Right and left
#phiBMaxR = 0 #phi wind,absolute,inverse + alpha(true wind?)
vBHypotheses = 0 # fpolar (|abs(trueWindVector)|)trueWindAlpha




def navigator(self, boatHeading, boatHeadingMax):
    phiBMaxR = 0 #phi wind,absolute,inverse + alpha(true wind?)
    trueWindAlpha = 0 #hook of wind
    deltaTrueWindAlpha = 0

    if boatHeading > boatHeadingMax:
        boatHeading = boatHeadingMax

        if trueWindAlpha >= 180:
            navigator(self, boatHeading, boatHeading)
            pass
        else:
            trueWindAlpha += deltaTrueWindAlpha 
            pass
        
        pass
    else:
        pass


    pass