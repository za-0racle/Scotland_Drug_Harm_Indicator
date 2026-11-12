import csv,io,zipfile,math,warnings
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial
z=zipfile.ZipFile('/mnt/data/Group3_Data_Bundle_WeekA.zip')
rows=list(csv.DictReader(io.StringIO(z.read('Group3_Data_Bundle_WeekA/derived/quarterly_input_table.csv').decode())))
y=np.array([int(r['police_suspected_deaths']) for r in rows],dtype=float)
output=[]
for window in (8,12,16):
 zstat=0.0; failures=[]; vals=[]
 for i in range(window,len(y)):
  a=np.arange(window,dtype=float); a=(a-(window-1))/window
  X=sm.add_constant(a)
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   try:
    fit=NegativeBinomial(y[i-window:i],X,loglike_method='nb2').fit(disp=0,maxiter=500)
    alpha=float(fit.params[-1]); mu=float(np.exp(np.dot([1.,1./window],fit.params[:2])))
    if not (np.isfinite(mu) and mu>0 and np.isfinite(alpha) and alpha>=0): raise ValueError('bad fit')
    residual=(y[i]-mu)/np.sqrt(mu+alpha*mu*mu)
    zstat=.2*residual+.8*zstat
    signal=abs(zstat)>2.962*math.sqrt(.2/1.8)
    vals.append((rows[i]['year'],rows[i]['quarter'],round(zstat,8),signal,round(mu,6),round(alpha,8)))
   except Exception as e: failures.append((i,str(e)))
 print('window',window,'failures',failures,'flags',[(v[0],v[1]) for v in vals if v[3]],'range',min(v[2] for v in vals),max(v[2] for v in vals))
 for year,q,s,flag,mu,alpha in vals:output.append(dict(configuration_id={8:1,12:2,16:3}[window],observation_year=year,observation_quarter=q[1:],statistic_value=s,lower_limit=-0.9873333333,upper_limit=0.9873333333,signal_flag=str(flag).lower(),computation_reference='Recomputed NB2 rolling one-step prediction; see methodology README'))
with open('/mnt/data/group3_indicator_results_recomputed.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
shares=np.array([float(r['share_opioids']) for r in rows if r['share_opioids'] and 2022<=int(r['year'])<=2024])
cal=shares[:8];mu=cal.mean();sd=cal.std(ddof=1);k=.5*sd;h=4.77*sd
plus=minus=0
print('CUSUM mu sd k h',mu,sd,k,h)
for j,v in enumerate(shares[8:]):
 plus=max(0,plus+v-mu-k);minus=max(0,minus+mu-v-k)
 print('2024 Q'+str(j+1),v,'C+',plus,'C-',minus,'signal',max(plus,minus)>h)
