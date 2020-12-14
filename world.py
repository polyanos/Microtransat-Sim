import sailboat as sb
import visualisation as vs
import wind as w
import simpylc as simp
import control as con
import pid as pid
import pid_sail as pidsail


simp.World(con.Control, sb.Sailboat, w.Wind, vs.Visualisation, pid.Pid, pidsail.Pid_sail)
