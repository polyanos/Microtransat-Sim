import sailboat as sb
import visualisation as vs
import wind as w
import simpylc as simp
import control as con



simp.World(con.Control, sb.Sailboat, w.Wind, vs.Visualisation)
