import sys, time
sys.path.insert(0, '.')
import aula_wired as a
d = a.open_dev()
a.send(d, [0x8a,0,0,1,0,0xe3,1]); time.sleep(0.05)
r = d.get_feature_report(a.RID, a.LEN)
print(bytes(r[:7+227]).hex())
a.send(d, [0x87,0,0,1,0,2]); time.sleep(0.05)
print(bytes(d.get_feature_report(a.RID, a.LEN)[:16]).hex())
