import sailboat as sb
import visualisation as vs
import wind as w
import simpylc as simp
import control as con
#import waypoints as wp
#from sailboat import * as sb
'''from visualisation import *
from control import *
from wind import *
from simpylc.engine import World
'''

simp.World(con.Control, sb.Sailboat, w.Wind, vs.Visualisation)
